"""Fabex 'ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

from math import pi
import os
import random
import subprocess
import textwrap
import threading
import time
import traceback

import shapely
from shapely import geometry as sgeometry
from shapely import affinity, prepared, speedups

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    FloatProperty,
)
from bpy.types import (
    Operator,
    PropertyGroup,
)
from mathutils import Euler, Vector

from .. import (
    bridges,
    gcode_path,
    pack,
    polygon_utils_cam,
    simple,
    simulation,
    utils,
)
from .async_op import (
    AsyncCancelledException,
    AsyncOperatorMixin,
    progress_async,
)
from ..constants import PRECISION
from ..exception import CamException
from ..pack import pack_curves
from ..utils import (
    add_machine_area_object,
    get_bounds_worldspace,
    chain_valid,
    source_valid,
    reload_paths,
    silhouette_offset,
    was_hidden_dict,
)


class threadCom:  # object passed to threads to read background process stdout info
    def __init__(self, o, proc):
        self.opname = o.name
        self.out_text = ""
        self.proc = proc
        self.lasttext = ""


def thread_read(tcom):
    """Reads the standard output of a background process in a non-blocking
    manner.

    This function reads a line from the standard output of a background
    process associated with the provided `tcom` object. It searches for a
    specific substring that indicates progress information, and if found,
    extracts that information and assigns it to the `outtext` attribute of
    the `tcom` object. This allows for real-time monitoring of the
    background process's output without blocking the main thread.

    Args:
        tcom (object): An object that has a `proc` attribute with a `stdout`
            stream from which to read the output.

    Returns:
        None: This function does not return a value; it modifies the `tcom`
            object in place.
    """
    inline = tcom.proc.stdout.readline()
    inline = str(inline)
    s = inline.find("progress{")
    if s > -1:
        e = inline.find("}")
        tcom.out_text = inline[s + 9 : e]


@bpy.app.handlers.persistent
def timer_update(context):
    """Monitor background processes related to camera path calculations.

    This function checks the status of background processes that are
    responsible for calculating camera paths. It retrieves the current
    processes and monitors their state. If a process has finished, it
    updates the corresponding camera operation and reloads the necessary
    paths. If the process is still running, it restarts the associated
    thread to continue monitoring.

    Args:
        context: The context in which the function is called, typically
            containing information about the current scene and operations.
    """
    text = ""
    s = bpy.context.scene
    if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, "cam_processes"):
        processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
        for p in processes:
            # proc=p[1].proc
            readthread = p[0]
            tcom = p[1]
            if not readthread.is_alive():
                readthread.join()
                # readthread.
                tcom.lasttext = tcom.out_text
                if tcom.out_text != "":
                    print(tcom.opname, tcom.out_text)
                    tcom.out_text = ""

                if "finished" in tcom.lasttext:
                    processes.remove(p)

                    o = s.cam_operations[tcom.opname]
                    o.computing = False
                    reload_paths(o)
                    update_z_buffer_image_tag = False
                    update_offset_image_tag = False
                else:
                    readthread = threading.Thread(target=thread_read, args=([tcom]), daemon=True)
                    readthread.start()
                    p[0] = readthread
            o = s.cam_operations[tcom.opname]  # changes
            o.out_text = tcom.lasttext  # changes


class PathsBackground(Operator):
    """Calculate CAM Paths in Background. File Has to Be Saved Before."""

    bl_idname = "object.calculate_cam_paths_background"
    bl_label = "Calculate CAM Paths in Background"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute the camera operation in the background.

        This method initiates a background process to perform camera operations
        based on the current scene and active camera operation. It sets up the
        necessary paths for the script and starts a subprocess to handle the
        camera computations. Additionally, it manages threading to ensure that
        the main thread remains responsive while the background operation is
        executed.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the completion status of the operation.
        """

        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o
        o.computing = True

        bpath = bpy.app.binary_path
        fpath = bpy.data.filepath

        for p in bpy.utils.script_paths():
            scriptpath = p + os.sep + "addons" + os.sep + "cam" + os.sep + "backgroundop.py"
            print(scriptpath)
            if os.path.isfile(scriptpath):
                break
        proc = subprocess.Popen(
            [bpath, "-b", fpath, "-P", scriptpath, "--", "-o=" + str(s.cam_active_operation)],
            bufsize=1,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

        tcom = threadCom(o, proc)
        readthread = threading.Thread(target=thread_read, args=([tcom]), daemon=True)
        readthread.start()
        # self.__class__.cam_processes=[]
        if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, "cam_processes"):
            bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes = []
        bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append(
            [readthread, tcom]
        )
        return {"FINISHED"}


class KillPathsBackground(Operator):
    """Remove CAM Path Processes in Background."""

    bl_idname = "object.kill_calculate_cam_paths_background"
    bl_label = "Kill Background Computation of an Operation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute the camera operation in the given context.

        This method retrieves the active camera operation from the scene and
        checks if there are any ongoing processes related to camera path
        calculations. If such processes exist and match the current operation,
        they are terminated. The method then marks the operation as not
        computing and returns a status indicating that the execution has
        finished.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary with a status key indicating the result of the execution.
        """

        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o

        if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, "cam_processes"):
            processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
            for p in processes:
                tcom = p[1]
                if tcom.opname == o.name:
                    processes.remove(p)
                    tcom.proc.kill()
                    o.computing = False

        return {"FINISHED"}


async def _calc_path(operator, context):
    """Calculate the path for a given operator and context.

    This function processes the current scene's camera operations based on
    the specified operator and context. It handles different geometry
    sources, checks for valid operation parameters, and manages the
    visibility of objects and collections. The function also retrieves the
    path using an asynchronous operation and handles any exceptions that may
    arise during this process. If the operation is invalid or if certain
    conditions are not met, appropriate error messages are reported to the
    operator.

    Args:
        operator (bpy.types.Operator): The operator that initiated the path calculation.
        context (bpy.types.Context): The context in which the operation is executed.

    Returns:
        tuple: A tuple indicating the status of the operation.
            Returns {'FINISHED', True} if successful,
            {'FINISHED', False} if there was an error,
            or {'CANCELLED', False} if the operation was cancelled.
    """

    s = bpy.context.scene
    o = s.cam_operations[s.cam_active_operation]
    if o.geometry_source == "OBJECT":
        ob = bpy.data.objects[o.object_name]
        ob.hide_set(False)
    if o.geometry_source == "COLLECTION":
        obc = bpy.data.collections[o.collection_name]
        for ob in obc.objects:
            ob.hide_set(False)
    if o.strategy == "CARVE":
        curvob = bpy.data.objects[o.curve_source]
        curvob.hide_set(False)
    """if o.strategy == 'WATERLINE':
        ob = bpy.data.objects[o.object_name]
        ob.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)"""
    mesh = bpy.data.meshes.get(f"cam_path_{o.name}")
    if mesh:
        bpy.data.meshes.remove(mesh)

    text = "Operation can't be performed, see Warnings for info"
    if not o.valid:
        operator.report(
            {"ERROR_INVALID_INPUT"},
            text,
        )
        progress_async(text)
        # bpy.ops.cam.popup(text=text)
        return {"FINISHED", False}

    # check for free movement height < maxz and return with error
    if o.movement.free_height < o.max_z:
        operator.report(
            {"ERROR_INVALID_INPUT"},
            "Free Movement Height Is Less than Operation Depth Start \n Correct and Try Again.",
        )
        progress_async("Operation Can't Be Performed, See Warnings for Info")
        # bpy.ops.cam.popup(text=text)
        return {"FINISHED", False}

    if o.computing:
        return {"FINISHED", False}

    o.operator = operator

    if o.use_layers:
        o.movement.parallel_step_back = False
    try:
        await gcode_path.get_path(context, o)
        print("Got Path Okay")
    except CamException as e:
        traceback.print_tb(e.__traceback__)
        error_str = "\n".join(textwrap.wrap(str(e), width=80))
        operator.report({"ERROR"}, error_str)
        # bpy.ops.cam.popup(text=error_str)
        return {"FINISHED", False}
    except AsyncCancelledException as e:
        # bpy.ops.cam.popup(text=str(e))
        return {"CANCELLED", False}
    except Exception as e:
        print("FAIL", e)
        traceback.print_tb(e.__traceback__)
        operator.report({"ERROR"}, str(e))
        # bpy.ops.cam.popup(text=str(e))
        return {"FINISHED", False}
    coll = bpy.data.collections.get("RigidBodyWorld")
    if coll:
        bpy.data.collections.remove(coll)

    return {"FINISHED", True}


class CalculatePath(Operator, AsyncOperatorMixin):
    """Calculate CAM Paths"""

    bl_idname = "object.calculate_cam_path"
    bl_label = "Calculate CAM Paths"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        """Check if the current camera operation is valid.

        This method checks the active camera operation in the given context and
        determines if it is valid. It retrieves the active operation from the
        scene's camera operations and validates it using the `isValid` function.
        If the operation is valid, it returns True; otherwise, it returns False.

        Args:
            context (Context): The context containing the scene and camera operations.

        Returns:
            bool: True if the active camera operation is valid, False otherwise.
        """

        s = context.scene
        o = s.cam_operations[s.cam_active_operation]
        if o is not None:
            if source_valid(o, context):
                return True
        return False

    async def execute_async(self, context):
        """Execute an asynchronous calculation of a path.

        This method performs an asynchronous operation to calculate a path based
        on the provided context. It awaits the result of the calculation and
        prints the success status along with the return value. The return value
        can be used for further processing or analysis.

        Args:
            context (Any): The context in which the path calculation is to be executed.

        Returns:
            Any: The result of the path calculation.
        """

        (retval, success) = await _calc_path(self, context)
        print(f"CALCULATED PATH (success={success},retval={retval}")
        return retval


class PathsAll(Operator):
    """Calculate All CAM Paths"""

    bl_idname = "object.calculate_cam_paths_all"
    bl_label = "Calculate All CAM Paths"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute camera operations in the current Blender context.

        This function iterates through the camera operations defined in the
        current scene and executes the background calculation for each
        operation. It sets the active camera operation index and prints the name
        of each operation being processed. This is typically used in a Blender
        add-on or script to automate camera path calculations.

        Args:
            context (bpy.context): The current Blender context.

        Returns:
            dict: A dictionary indicating the completion status of the operation,
                typically {'FINISHED'}.
        """

        i = 0
        for o in bpy.context.scene.cam_operations:
            bpy.context.scene.cam_active_operation = i
            print("\nCalculating Path :" + o.name)
            print("\n")
            bpy.ops.object.calculate_cam_paths_background()
            i += 1

        return {"FINISHED"}

    def draw(self, context):
        """Draws the user interface elements for the operation selection.

        This method utilizes the Blender layout system to create a property
        search interface for selecting operations related to camera
        functionalities. It links the current instance's operation property to
        the available camera operations defined in the Blender scene.

        Args:
            context (bpy.context): The context in which the drawing occurs,
        """

        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CamPackObjects(Operator):
    """Calculate All CAM Paths"""

    bl_idname = "object.cam_pack_objects"
    bl_label = "Pack Curves on Sheet"
    bl_options = {"REGISTER", "UNDO"}

    sheet_fill_direction: EnumProperty(
        name="Fill Direction",
        items=(
            ("X", "X", "Fills sheet in X axis direction"),
            ("Y", "Y", "Fills sheet in Y axis direction"),
        ),
        description="Fill direction of the packer algorithm",
        default="Y",
    )
    sheet_x: FloatProperty(
        name="X Size",
        description="Sheet size",
        min=0.001,
        max=10,
        default=0.5,
        precision=PRECISION,
        unit="LENGTH",
    )
    sheet_y: FloatProperty(
        name="Y Size",
        description="Sheet size",
        min=0.001,
        max=10,
        default=0.5,
        precision=PRECISION,
        unit="LENGTH",
    )
    distance: FloatProperty(
        name="Minimum Distance",
        description="Minimum distance between objects(should be " "at least cutter diameter!)",
        min=0.001,
        max=10,
        default=0.01,
        precision=PRECISION,
        unit="LENGTH",
    )
    tolerance: FloatProperty(
        name="Placement Tolerance",
        description="Tolerance for placement: smaller value slower placemant",
        min=0.001,
        max=0.02,
        default=0.005,
        precision=PRECISION,
        unit="LENGTH",
    )
    rotate: BoolProperty(
        name="Enable Rotation",
        description="Enable rotation of elements",
        default=True,
    )
    rotate_angle: FloatProperty(
        name="Placement Angle Rotation Step",
        description="Bigger rotation angle, faster placemant",
        default=0.19635 * 4,
        min=pi / 180,
        max=pi,
        precision=5,
        subtype="ANGLE",
        unit="ROTATION",
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        """Execute the operation in the given context.

        This function sets the Blender object mode to 'OBJECT', retrieves the
        currently selected objects, and calls the `pack_curves` function from the
        `pack` module. It is typically used to finalize operations on selected
        objects in Blender.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the completion status of the operation.
        """

        bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
        obs = bpy.context.selected_objects
        if speedups.available:
            speedups.enable()
        t = time.time()

        sheetsizex = self.sheet_x
        sheetsizey = self.sheet_y
        direction = self.sheet_fill_direction
        distance = self.distance
        tolerance = self.tolerance
        rotate = self.rotate
        rotate_angle = self.rotate_angle

        # in this, position, rotation, and actual poly will be stored.
        polyfield = []
        for ob in bpy.context.selected_objects:
            simple.activate(ob)
            bpy.ops.object.make_single_user(type="SELECTED_OBJECTS")
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            z = ob.location.z
            bpy.ops.object.location_clear()
            bpy.ops.object.rotation_clear()

            chunks = utils.curve_to_chunks(ob)
            npolys = utils.chunks_to_shapely(chunks)
            # add all polys in silh to one poly
            poly = shapely.ops.unary_union(npolys)

            poly = poly.buffer(distance / 1.5, 8)
            poly = poly.simplify(0.0003)
            polyfield.append([[0, 0], 0.0, poly, ob, z])
        random.shuffle(polyfield)
        # primitive layout here:
        allpoly = prepared.prep(sgeometry.Polygon())  # main collision poly.

        shift = tolerance  # one milimeter by now.
        rotchange = rotate_angle  # in radians

        xmin, ymin, xmax, ymax = polyfield[0][2].bounds
        if direction == "X":
            mindist = -xmin
        else:
            mindist = -ymin
        i = 0
        p = polyfield[0][2]
        placedpolys = []
        rotcenter = sgeometry.Point(0, 0)
        for pf in polyfield:
            print(i)
            rot = 0
            porig = pf[2]
            placed = False
            xmin, ymin, xmax, ymax = p.bounds
            if direction == "X":
                x = mindist
                y = -ymin
            if direction == "Y":
                x = -xmin
                y = mindist

            itera = 0
            best = None
            hits = 0
            besthit = None
            while not placed:
                # swap x and y, and add to x
                # print(x,y)
                p = porig

                if rotate:
                    ptrans = affinity.rotate(p, rot, origin=rotcenter, use_radians=True)
                    ptrans = affinity.translate(ptrans, x, y)
                else:
                    ptrans = affinity.translate(p, x, y)
                xmin, ymin, xmax, ymax = ptrans.bounds
                # print(iter,p.bounds)

                if (
                    xmin > 0
                    and ymin > 0
                    and (
                        (direction == "Y" and xmax < sheetsizex)
                        or (direction == "X" and ymax < sheetsizey)
                    )
                ):
                    if not allpoly.intersects(ptrans):
                        # we do more good solutions, choose best out of them:
                        hits += 1
                        if best is None:
                            best = [x, y, rot, xmax, ymax]
                            besthit = hits
                        if direction == "X":
                            if xmax < best[3]:
                                best = [x, y, rot, xmax, ymax]
                                besthit = hits
                        elif ymax < best[4]:
                            best = [x, y, rot, xmax, ymax]
                            besthit = hits

                if hits >= 15 or (
                    itera > 20000 and hits > 0
                ):  # here was originally more, but 90% of best solutions are still 1
                    placed = True
                    pf[3].location.x = best[0]
                    pf[3].location.y = best[1]
                    pf[3].location.z = pf[4]
                    pf[3].rotation_euler.z = best[2]

                    pf[3].select_set(state=True)

                    # print(mindist)
                    mindist = mindist - 0.5 * (xmax - xmin)
                    # print(mindist)
                    # print(iter)

                    # reset polygon to best position here:
                    ptrans = affinity.rotate(porig, best[2], rotcenter, use_radians=True)
                    ptrans = affinity.translate(ptrans, best[0], best[1])

                    print(best[0], best[1], itera)
                    placedpolys.append(ptrans)
                    allpoly = prepared.prep(sgeometry.MultiPolygon(placedpolys))

                    # cleanup allpoly
                    print(itera, hits, besthit)
                if not placed:
                    if direction == "Y":
                        x += shift
                        mindist = y
                        if xmax + shift > sheetsizex:
                            x = x - xmin
                            y += shift
                    if direction == "X":
                        y += shift
                        mindist = x
                        if ymax + shift > sheetsizey:
                            y = y - ymin
                            x += shift
                    if rotate:
                        rot += rotchange
                itera += 1
            i += 1
        t = time.time() - t

        polygon_utils_cam.shapely_to_curve("test", sgeometry.MultiPolygon(placedpolys), 0)
        print(t)
        # layout.
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Sheet Size")
        col.prop(self, "sheet_x", text="X")
        col.prop(self, "sheet_y", text="Y")
        col.prop(self, "sheet_fill_direction")
        col = layout.column(align=True)
        col.prop(self, "distance")
        col.prop(self, "tolerance")
        header, panel = col.panel_prop(self, "rotate")
        header.label(text="Rotation")
        if panel:
            col = panel.column(align=True)
            col.prop(self, "rotate_angle", text="Placement Angle Step")

        # box_2 = layout.box()
        # col = box_2.column()
        # col.scale_y = 1.2
        # col.operator("object.cam_pack_objects", icon="FCURVE")


class CamSliceObjects(Operator):
    """Slice a Mesh Object Horizontally"""

    # warning, this is a separate and neglected feature, it's a mess - by now it just slices up the object.
    bl_idname = "object.cam_slice_objects"
    bl_label = "Slice Object - Useful for Lasercut Puzzles etc"
    bl_options = {"REGISTER", "UNDO"}

    slice_distance: FloatProperty(
        name="Slicing Distance",
        description="Slices distance in z, should be most often " "thickness of plywood sheet.",
        min=0.001,
        max=10,
        default=0.005,
        precision=PRECISION,
        unit="LENGTH",
    )
    slice_above_0: BoolProperty(
        name="Slice Above 0",
        description="only slice model above 0",
        default=False,
    )
    slice_3d: BoolProperty(
        name="3D Slice",
        description="For 3D carving",
        default=False,
    )
    indexes: BoolProperty(
        name="Add Indexes",
        description="Adds index text of layer + index",
        default=True,
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        """Slice a 3D object into layers based on a specified thickness.

        This function takes a 3D object and slices it into multiple layers
        according to the specified thickness. It creates a new collection for
        the slices and optionally creates text labels for each slice if the
        indexes parameter is set. The slicing can be done in either 2D or 3D
        based on the user's selection. The function also handles the positioning
        of the slices based on the object's bounding box.

        Args:
            ob (bpy.types.Object): The 3D object to be sliced.
        """

        from .slice import slicing_2d, slicing_3d

        ob = bpy.context.active_object

        # April 2020 Alain Pelletier
        # get variables from menu
        thickness = self.slice_distance
        slice3d = self.slice_3d
        indexes = self.indexes
        above0 = self.slice_above_0
        # setup the collections
        scollection = bpy.data.collections.new("Slices")
        bpy.context.scene.collection.children.link(scollection)
        if indexes:
            tcollection = bpy.data.collections.new("Text")
            bpy.context.scene.collection.children.link(tcollection)

        bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
        minx, miny, minz, maxx, maxy, maxz = utils.get_bounds_worldspace([ob])

        start_height = minz
        if above0 and minz < 0:
            start_height = 0

        # calculate amount of layers needed
        layeramt = 1 + int((maxz - start_height) // thickness)

        for layer in range(layeramt):
            height = round(layer * thickness, 6)  # height of current layer
            t = str(layer) + "-" + str(height * 1000)
            slicename = "slice_" + t  # name for the current slice
            tslicename = "t_" + t  # name for the current slice text
            height += start_height
            print(slicename)

            ob.select_set(True)  # select object to be sliced
            bpy.context.view_layer.objects.active = ob  # make object to be sliced active
            bpy.ops.object.duplicate()  # make a copy of object to be sliced
            bpy.context.view_layer.objects.active.name = slicename  # change the name of object

            # attribute active object to obslice
            obslice = bpy.context.view_layer.objects.active
            scollection.objects.link(obslice)  # link obslice to scollecton
            if slice3d:
                # slice 3d at desired height and stop at desired height
                slicesuccess = slicing_3d(obslice, height, height + thickness)
            else:
                # slice object at desired height
                slicesuccess = slicing_2d(obslice, height)

            if indexes and slicesuccess:
                # text objects
                bpy.ops.object.text_add()  # new text object
                textob = bpy.context.active_object
                textob.data.size = 0.006  # change size of object
                textob.data.body = t  # text content
                textob.location = (0, 0, 0)  # text location
                textob.name = tslicename  # change the name of object
                bpy.ops.object.select_all(action="DESELECT")  # deselect everything
                tcollection.objects.link(textob)  # add to text collection
                textob.parent = obslice  # make textob child of obslice

        # select all slices
        for obj in bpy.data.collections["Slices"].all_objects:
            obj.select_set(True)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "slice_distance")
        col.prop(self, "slice_above_0")
        col.prop(self, "slice_3d")
        col.prop(self, "indexes")


def get_chain_operations(chain):
    """Return chain operations associated with a given chain object.

    This function iterates through the operations of the provided chain
    object and retrieves the corresponding operations from the current
    scene's camera operations in Blender. Due to limitations in Blender,
    chain objects cannot store operations directly, so this function serves
    to extract and return the relevant operations for further processing.

    Args:
        chain (object): The chain object from which to retrieve operations.

    Returns:
        list: A list of operations associated with the given chain object.
    """
    chop = []
    for cho in chain.operations:
        for so in bpy.context.scene.cam_operations:
            if so.name == cho.name:
                chop.append(so)
    return chop


class PathsChain(Operator, AsyncOperatorMixin):
    """Calculate a Chain and Export the G-code Alltogether."""

    bl_idname = "object.calculate_cam_paths_chain"
    bl_label = "Calculate CAM Paths in Current Chain and Export Chain G-code"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        """Check the validity of the active camera chain in the given context.

        This method retrieves the active camera chain from the scene and checks
        its validity using the `isChainValid` function. It returns a boolean
        value indicating whether the camera chain is valid or not.

        Args:
            context (Context): The context containing the scene and camera chain information.

        Returns:
            bool: True if the active camera chain is valid, False otherwise.
        """

        s = context.scene
        if len(s.cam_chains) > 0:
            chain = s.cam_chains[s.cam_active_chain]
            return chain_valid(chain, context)[0]
        else:
            return False

    async def execute_async(self, context):
        """Execute asynchronous operations for camera path calculations.

        This method sets the object mode for the Blender scene and processes a
        series of camera operations defined in the active camera chain. It
        reports the progress of each operation and handles any exceptions that
        may occur during the path calculation. After successful calculations, it
        exports the resulting mesh data to a specified G-code file.

        Args:
            context (bpy.context): The Blender context containing scene and

        Returns:
            dict: A dictionary indicating the result of the operation,
            typically {'FINISHED'}.
        """

        s = context.scene
        bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
        chain = s.cam_chains[s.cam_active_chain]
        chainops = get_chain_operations(chain)
        meshes = []
        try:
            for i in range(0, len(chainops)):
                s.cam_active_operation = s.cam_operations.find(chainops[i].name)
                self.report({"INFO"}, f"Calculating Path: {chainops[i].name}")
                result, success = await _calc_path(self, context)
                if not success and "FINISHED" in result:
                    self.report({"ERROR"}, f"Couldn't Calculate Path: {chainops[i].name}")
        except Exception as e:
            print("FAIL", e)
            traceback.print_tb(e.__traceback__)
            self.report({"ERROR"}, str(e))
            return {"FINISHED"}

        for o in chainops:
            meshes.append(bpy.data.objects["cam_path_{}".format(o.name)].data)
        gcode_path.export_gcode_path(chain.filename, meshes, chainops)
        return {"FINISHED"}


class PathExportChain(Operator):
    """Calculate a Chain and Export the G-code Together."""

    bl_idname = "object.cam_export_paths_chain"
    bl_label = "Export CAM Paths in Current Chain as G-code"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Check the validity of the active camera chain in the given context.

        This method retrieves the currently active camera chain from the scene
        context and checks its validity using the `isChainValid` function. It
        returns a boolean indicating whether the active camera chain is valid or
        not.

        Args:
            context (object): The context containing the scene and camera chain information.

        Returns:
            bool: True if the active camera chain is valid, False otherwise.
        """

        s = context.scene
        chain = s.cam_chains[s.cam_active_chain]
        return chain_valid(chain, context)[0]

    def execute(self, context):
        """Execute the camera path export process.

        This function retrieves the active camera chain from the current scene
        and gathers the mesh data associated with the operations of that chain.
        It then exports the G-code path using the specified filename and the
        collected mesh data. The function is designed to be called within the
        context of a Blender operator.

        Args:
            context (bpy.context): The context in which the operator is executed.

        Returns:
            dict: A dictionary indicating the completion status of the operation,
                typically {'FINISHED'}.
        """

        s = bpy.context.scene

        chain = s.cam_chains[s.cam_active_chain]
        chainops = get_chain_operations(chain)
        meshes = []

        # if len(chainops)<4:

        for o in chainops:
            # bpy.ops.object.calculate_cam_paths_background()
            meshes.append(bpy.data.objects["cam_path_{}".format(o.name)].data)
        gcode_path.export_gcode_path(chain.filename, meshes, chainops)
        return {"FINISHED"}


class PathExport(Operator):
    """Export G-code. Can Be Used only when the Path Object Is Present"""

    bl_idname = "object.cam_export"
    bl_label = "Export Operation G-code"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute the camera operation and export the G-code path.

        This method retrieves the active camera operation from the current scene
        and exports the corresponding G-code path to a specified filename. It
        prints the filename and relevant operation details to the console for
        debugging purposes. The G-code path is generated based on the camera
        path data associated with the active operation.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the completion status of the operation,
                typically {'FINISHED'}.
        """

        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]

        print(
            "EXPORTING",
            operation.filename,
            bpy.data.objects["cam_path_{}".format(operation.name)].data,
            operation,
        )

        gcode_path.export_gcode_path(
            operation.filename,
            [bpy.data.objects["cam_path_{}".format(operation.name)].data],
            [operation],
        )
        return {"FINISHED"}


class CAMSimulate(Operator, AsyncOperatorMixin):
    """Simulate CAM Operation
    This Is Performed by: Creating an Image, Painting Z Depth of the Brush Subtractively.
    Works only for Some Operations, Can Not Be Used for 4-5 Axis."""

    bl_idname = "object.cam_simulate"
    bl_label = "CAM Simulation"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    operation: StringProperty(
        name="Operation",
        description="Specify the operation to calculate",
        default="Operation",
    )

    async def execute_async(self, context):
        """Execute an asynchronous simulation operation based on the active camera
        operation.

        This method retrieves the current scene and the active camera operation.
        It constructs the operation name and checks if the corresponding object
        exists in the Blender data. If it does, it attempts to run the
        simulation asynchronously. If the simulation is cancelled, it returns a
        cancellation status. If the object does not exist, it reports an error
        and returns a finished status.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation, either
                {'CANCELLED'} or {'FINISHED'}.
        """

        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]

        operation_name = "cam_path_{}".format(operation.name)

        if operation_name in bpy.data.objects:
            try:
                await simulation.do_simulation(operation_name, [operation])
            except AsyncCancelledException as e:
                return {"CANCELLED"}
        else:
            self.report({"ERROR"}, "No Computed Path to Simulate")
            return {"FINISHED"}
        return {"FINISHED"}

    def draw(self, context):
        """Draws the user interface for selecting camera operations.

        This method creates a layout element in the user interface that allows
        users to search and select a specific camera operation from a list of
        available operations defined in the current scene. It utilizes the
        Blender Python API to integrate with the UI.

        Args:
            context: The context in which the drawing occurs, typically
                provided by Blender's UI system.
        """

        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CAMSimulateChain(Operator, AsyncOperatorMixin):
    """Simulate CAM Chain, Compared to Single Op Simulation Just Writes Into One Image and Thus Enables
    to See how Ops Work Together."""

    bl_idname = "object.cam_simulate_chain"
    bl_label = "CAM Simulation"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        """Check the validity of the active camera chain in the scene.

        This method retrieves the currently active camera chain from the scene's
        camera chains and checks its validity using the `isChainValid` function.
        It returns a boolean indicating whether the active camera chain is
        valid.

        Args:
            context (object): The context containing the scene and its properties.

        Returns:
            bool: True if the active camera chain is valid, False otherwise.
        """

        s = context.scene
        if len(s.cam_chains) > 0:
            chain = s.cam_chains[s.cam_active_chain]
            return chain_valid(chain, context)[0]
        else:
            return False

    operation: StringProperty(
        name="Operation",
        description="Specify the operation to calculate",
        default="Operation",
    )

    async def execute_async(self, context):
        """Execute an asynchronous simulation for a specified camera chain.

        This method retrieves the active camera chain from the current Blender
        scene and determines the operations associated with that chain. It
        checks if all operations are valid and can be simulated. If valid, it
        proceeds to execute the simulation asynchronously. If any operation is
        invalid, it logs a message and returns a finished status without
        performing the simulation.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation, either
            operation completed successfully.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chainops = get_chain_operations(chain)

        canSimulate = True
        for operation in chainops:
            if operation.name not in bpy.data.objects:
                canSimulate = True  # force true
            print("operation name " + str(operation.name))
        if canSimulate:
            try:
                await simulation.do_simulation(chain.name, chainops)
            except AsyncCancelledException as e:
                return {"CANCELLED"}
        else:
            print("no computed path to simulate")
            return {"FINISHED"}
        return {"FINISHED"}

    def draw(self, context):
        """Draw the user interface for selecting camera operations.

        This function creates a user interface element that allows the user to
        search and select a specific camera operation from a list of available
        operations in the current scene. It utilizes the Blender Python API to
        create a property search layout.

        Args:
            context: The context in which the drawing occurs, typically containing
                information about the current scene and UI elements.
        """

        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CamChainAdd(Operator):
    """Add New CAM Chain"""

    bl_idname = "scene.cam_chain_add"
    bl_label = "Add New CAM Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera chain creation in the given context.

        This function adds a new camera chain to the current scene in Blender.
        It updates the active camera chain index and assigns a name and filename
        to the newly created chain. The function is intended to be called within
        a Blender operator context.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation's completion status,
                specifically returning {'FINISHED'} upon successful execution.
        """

        # main(context)
        s = bpy.context.scene
        s.cam_chains.add()
        chain = s.cam_chains[-1]
        s.cam_active_chain = len(s.cam_chains) - 1
        chain.name = "Chain_" + str(s.cam_active_chain + 1)
        chain.filename = chain.name
        chain.index = s.cam_active_chain

        return {"FINISHED"}


class CamChainRemove(Operator):
    """Remove CAM Chain"""

    bl_idname = "scene.cam_chain_remove"
    bl_label = "Remove CAM Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera chain removal process.

        This function removes the currently active camera chain from the scene
        and decrements the active camera chain index if it is greater than zero.
        It modifies the Blender context to reflect these changes.

        Args:
            context: The context in which the function is executed.

        Returns:
            dict: A dictionary indicating the status of the operation,
                specifically {'FINISHED'} upon successful execution.
        """

        bpy.context.scene.cam_chains.remove(bpy.context.scene.cam_active_chain)
        if bpy.context.scene.cam_active_chain > 0:
            bpy.context.scene.cam_active_chain -= 1

        return {"FINISHED"}


class CamChainOperationAdd(Operator):
    """Add Operation to Chain"""

    bl_idname = "scene.cam_chain_operation_add"
    bl_label = "Add Operation to Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute an operation in the active camera chain.

        This function retrieves the active camera chain from the current scene
        and adds a new operation to it. It increments the active operation index
        and assigns the name of the currently selected camera operation to the
        newly added operation. This is typically used in the context of managing
        camera operations in a 3D environment.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the execution status, typically {'FINISHED'}.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        s = bpy.context.scene
        chain.operations.add()
        chain.active_operation += 1
        chain.operations[-1].name = s.cam_operations[s.cam_active_operation].name
        return {"FINISHED"}


class CamChainOperationUp(Operator):
    """Add Operation to Chain"""

    bl_idname = "scene.cam_chain_operation_up"
    bl_label = "Add Operation to Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the operation to move the active camera operation in the chain.

        This function retrieves the current scene and the active camera chain.
        If there is an active operation (i.e., its index is greater than 0), it
        moves the operation one step up in the chain by adjusting the indices
        accordingly. After moving the operation, it updates the active operation
        index to reflect the change.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the result of the operation,
                specifically returning {'FINISHED'} upon successful execution.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        a = chain.active_operation
        if a > 0:
            chain.operations.move(a, a - 1)
            chain.active_operation -= 1
        return {"FINISHED"}


class CamChainOperationDown(Operator):
    """Add Operation to Chain"""

    bl_idname = "scene.cam_chain_operation_down"
    bl_label = "Add Operation to Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the operation to move the active camera operation in the chain.

        This function retrieves the current scene and the active camera chain.
        It checks if the active operation can be moved down in the list of
        operations. If so, it moves the active operation one position down and
        updates the active operation index accordingly.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the result of the operation,
                specifically {'FINISHED'} when the operation completes successfully.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        a = chain.active_operation
        if a < len(chain.operations) - 1:
            chain.operations.move(a, a + 1)
            chain.active_operation += 1
        return {"FINISHED"}


class CamChainOperationRemove(Operator):
    """Remove Operation from Chain"""

    bl_idname = "scene.cam_chain_operation_remove"
    bl_label = "Remove Operation from Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the operation to remove the active operation from the camera
        chain.

        This method accesses the current scene and retrieves the active camera
        chain. It then removes the currently active operation from that chain
        and adjusts the index of the active operation accordingly. If the active
        operation index becomes negative, it resets it to zero to ensure it
        remains within valid bounds.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the execution status, typically
                containing {'FINISHED'} upon successful completion.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chain.operations.remove(chain.active_operation)
        chain.active_operation -= 1
        if chain.active_operation < 0:
            chain.active_operation = 0
        return {"FINISHED"}


def fix_units():
    """Set up units for Fabex.

    This function configures the unit settings for the current Blender
    scene. It sets the rotation system to degrees and the scale length to
    1.0, ensuring that the units are appropriately configured for use within
    Fabex.
    """
    s = bpy.context.scene

    s.unit_settings.system_rotation = "DEGREES"

    s.unit_settings.scale_length = 1.0
    # Blender CAM doesn't respect this property and there were users reporting problems, not seeing this was changed.


class CamOperationAdd(Operator):
    """Add New CAM Operation"""

    bl_idname = "scene.cam_operation_add"
    bl_label = "Add New CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera operation based on the active object in the scene.

        This method retrieves the active object from the Blender context and
        performs operations related to camera settings. It checks if an object
        is selected and retrieves its bounding box dimensions. If no object is
        found, it reports an error and cancels the operation. If an object is
        present, it adds a new camera operation to the scene, sets its
        properties, and ensures that a machine area object is present.

        Args:
            context: The context in which the operation is executed.
        """
        # Open Sidebar to show Operation Settings
        if context.scene.interface.operation_location == "SIDEBAR":
            view3d = [a for a in context.screen.areas if a.type == "VIEW_3D"][0]
            view3d.spaces[0].show_region_ui = True

        s = bpy.context.scene
        fix_units()

        ob = bpy.context.active_object
        if ob is None:
            self.report({"ERROR_INVALID_INPUT"}, "Please Add an Object to Base the Operation on.")
            return {"CANCELLED"}

        minx, miny, minz, maxx, maxy, maxz = get_bounds_worldspace([ob])
        s.cam_operations.add()
        o = s.cam_operations[-1]
        o.object_name = ob.name
        o.min_z = minz

        s.cam_active_operation = len(s.cam_operations) - 1

        o.name = f"Op_{ob.name}_{s.cam_active_operation + 1}"
        o.filename = o.name

        if s.objects.get("CAM_machine") is None:
            add_machine_area_object()

        return {"FINISHED"}


class CamOperationCopy(Operator):
    """Copy CAM Operation"""

    bl_idname = "scene.cam_operation_copy"
    bl_label = "Copy Active CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera operation in the given context.

        This method handles the execution of camera operations within the
        Blender scene. It first checks if there are any camera operations
        available. If not, it returns a cancellation status. If there are
        operations, it copies the active operation, increments the active
        operation index, and updates the name and filename of the new operation.
        The function also ensures that the new operation's name is unique by
        appending a copy suffix or incrementing a numeric suffix.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation,
                either {'CANCELLED'} if no operations are available or
                {'FINISHED'} if the operation was successfully executed.
        """

        # main(context)
        scene = bpy.context.scene

        fix_units()

        scene = bpy.context.scene
        if len(scene.cam_operations) == 0:
            return {"CANCELLED"}
        copyop = scene.cam_operations[scene.cam_active_operation]
        scene.cam_operations.add()
        scene.cam_active_operation += 1
        l = len(scene.cam_operations) - 1
        scene.cam_operations.move(l, scene.cam_active_operation)
        o = scene.cam_operations[scene.cam_active_operation]

        for k in copyop.keys():
            value = copyop[k]
            if isinstance(value, bpy.types.PropertyGroup):
                for subkey in value.keys():
                    o[k][subkey] = value[subkey]
            elif isinstance(value, (int, float, str, bool, list)):
                o[k] = value

        o.computing = False

        # ###get digits in the end

        isdigit = True
        numdigits = 0
        num = 0
        if o.name[-1].isdigit():
            numdigits = 1
            while isdigit:
                numdigits += 1
                isdigit = o.name[-numdigits].isdigit()
            numdigits -= 1
            o.name = o.name[:-numdigits] + str(int(o.name[-numdigits:]) + 1).zfill(numdigits)
            o.filename = o.name
        else:
            o.name = o.name + "_copy"
            o.filename = o.filename + "_copy"

        return {"FINISHED"}


class CamOperationRemove(Operator):
    """Remove CAM Operation"""

    bl_idname = "scene.cam_operation_remove"
    bl_label = "Remove CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera operation in the given context.

        This function performs the active camera operation by deleting the
        associated object from the scene. It checks if there are any camera
        operations available and handles the deletion of the active operation's
        object. If the active operation is removed, it updates the active
        operation index accordingly. Additionally, it manages a dictionary that
        tracks hidden objects.

        Args:
            context (bpy.context): The Blender context containing the scene and operations.

        Returns:
            dict: A dictionary indicating the result of the operation, either
                {'CANCELLED'} if no operations are available or {'FINISHED'} if the
                operation was successfully executed.
        """

        scene = context.scene
        try:
            if len(scene.cam_operations) == 0:
                # # Close Sidebar
                # view3d = [a for a in context.screen.areas if a.type == "VIEW_3D"][0]
                # if view3d.regions[5].active_panel_category == "CNC":
                #     view3d.spaces[0].show_region_ui = False
                return {"CANCELLED"}
            active_op = scene.cam_operations[scene.cam_active_operation]
            active_op_object = bpy.data.objects[active_op.name]
            scene.objects.active = active_op_object
            bpy.ops.object.delete(True)
        except:
            pass

        ao = scene.cam_operations[scene.cam_active_operation]
        print(was_hidden_dict)
        if ao.name in was_hidden_dict:
            del was_hidden_dict[ao.name]

        scene.cam_operations.remove(scene.cam_active_operation)
        if scene.cam_active_operation > 0:
            scene.cam_active_operation -= 1

        return {"FINISHED"}


# move cam operation in the list up or down
class CamOperationMove(Operator):
    """Move CAM Operation"""

    bl_idname = "scene.cam_operation_move"
    bl_label = "Move CAM Operation in List"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        name="Direction",
        items=(("UP", "Up", ""), ("DOWN", "Down", "")),
        description="Direction",
        default="DOWN",
    )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute a camera operation based on the specified direction.

        This method modifies the active camera operation in the Blender context
        based on the direction specified. If the direction is 'UP', it moves the
        active operation up in the list, provided it is not already at the top.
        Conversely, if the direction is not 'UP', it moves the active operation
        down in the list, as long as it is not at the bottom. The method updates
        the active operation index accordingly.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation has finished, with
            the key 'FINISHED'.
        """

        # main(context)
        a = bpy.context.scene.cam_active_operation
        cops = bpy.context.scene.cam_operations
        if self.direction == "UP":
            if a > 0:
                cops.move(a, a - 1)
                bpy.context.scene.cam_active_operation -= 1

        else:
            if a < len(cops) - 1:
                cops.move(a, a + 1)
                bpy.context.scene.cam_active_operation += 1

        return {"FINISHED"}


class CamOrientationAdd(Operator):
    """Add Orientation to CAM Operation, for Multiaxis Operations"""

    bl_idname = "scene.cam_orientation_add"
    bl_label = "Add Orientation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera orientation operation in Blender.

        This function retrieves the active camera operation from the current
        scene, creates an empty object to represent the camera orientation, and
        adds it to a specified group. The empty object is named based on the
        operation's name and the current count of objects in the group. The size
        of the empty object is set to a predefined value for visibility.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation's completion status,
                typically {'FINISHED'}.
        """

        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        gname = o.name + "_orientations"
        bpy.ops.object.empty_add(type="ARROWS")

        oriob = bpy.context.active_object
        oriob.empty_draw_size = 0.02  # 2 cm

        simple.add_to_group(oriob, gname)
        oriob.name = "ori_" + o.name + "." + str(len(bpy.data.collections[gname].objects)).zfill(3)

        return {"FINISHED"}


class CamBridgesAdd(Operator):
    """Add Bridge Objects to Curve"""

    bl_idname = "scene.cam_bridges_add"
    bl_label = "Add Bridges / Tabs"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the camera operation in the given context.

        This function retrieves the active camera operation from the current
        scene and adds automatic bridges to it. It is typically called within
        the context of a Blender operator to perform specific actions related to
        camera operations.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the result of the operation, typically
            containing the key 'FINISHED' to signify successful completion.
        """

        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        bridges.add_auto_bridges(o)
        return {"FINISHED"}
