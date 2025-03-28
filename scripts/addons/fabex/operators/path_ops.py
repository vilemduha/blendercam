"""Fabex 'ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

from math import pi
import os
import subprocess
import textwrap
import threading
import time
import traceback

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    FloatProperty,
)
from bpy.types import Operator

from .async_op import (
    AsyncCancelledException,
    AsyncOperatorMixin,
)

from ..constants import was_hidden_dict
from ..exception import CamException
from ..gcode_path import (
    get_path,
    export_gcode_path,
)

from ..utilities.async_utils import progress_async
from ..utilities.chunk_utils import chunks_to_shapely
from ..utilities.shapely_utils import shapely_to_curve
from ..utilities.simple_utils import activate, add_to_group
from ..utilities.thread_utils import threadCom, thread_read, timer_update
from ..utilities.machine_utils import add_machine_area_object
from ..utilities.bounds_utils import get_bounds_worldspace
from ..utilities.operation_utils import (
    chain_valid,
    source_valid,
    reload_paths,
    get_chain_operations,
)


class PathsBackground(Operator):
    """Calculate CAM Paths in Background. File Has to Be Saved Before."""

    bl_idname = "object.calculate_cam_paths_background"
    bl_label = "Calculate CAM Paths in Background"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute the CAM operation in the background.

        This method initiates a background process to perform CAM operations
        based on the current scene and active CAM operation. It sets up the
        necessary paths for the script and starts a subprocess to handle the
        CAM computations. Additionally, it manages threading to ensure that
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
        """Execute the CAM operation in the given context.

        This method retrieves the active CAM operation from the scene and
        checks if there are any ongoing processes related to CAM path
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

    This function processes the current scene's CAM operations based on
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
        await get_path(context, o)
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

    def __init__(self, *args, **kwargs):
        Operator.__init__(self, *args, **kwargs)
        AsyncOperatorMixin.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    @classmethod
    def poll(cls, context):
        """Check if the current CAM operation is valid.

        This method checks the active CAM operation in the given context and
        determines if it is valid. It retrieves the active operation from the
        scene's CAM operations and validates it using the `isValid` function.
        If the operation is valid, it returns True; otherwise, it returns False.

        Args:
            context (Context): The context containing the scene and CAM operations.

        Returns:
            bool: True if the active CAM operation is valid, False otherwise.
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
        print(f"CALCULATED PATH (success={success},retval={retval})")
        return retval


class PathsAll(Operator):
    """Calculate All CAM Paths"""

    bl_idname = "object.calculate_cam_paths_all"
    bl_label = "Calculate All CAM Paths"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute CAM operations in the current Blender context.

        This function iterates through the CAM operations defined in the
        current scene and executes the background calculation for each
        operation. It sets the active CAM operation index and prints the name
        of each operation being processed. This is typically used in a Blender
        add-on or script to automate CAM path calculations.

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
        search interface for selecting operations related to CAM
        functionalities. It links the current instance's operation property to
        the available CAM operations defined in the Blender scene.

        Args:
            context (bpy.context): The context in which the drawing occurs,
        """

        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class PathsChain(Operator, AsyncOperatorMixin):
    """Calculate a Chain and Export the G-code Alltogether."""

    bl_idname = "object.calculate_cam_paths_chain"
    bl_label = "Calculate CAM Paths in Current Chain and Export Chain G-code"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    def __init__(self, *args, **kwargs):
        Operator.__init__(self, *args, **kwargs)
        AsyncOperatorMixin.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    @classmethod
    def poll(cls, context):
        """Check the validity of the active CAM chain in the given context.

        This method retrieves the active CAM chain from the scene and checks
        its validity using the `isChainValid` function. It returns a boolean
        value indicating whether the CAM chain is valid or not.

        Args:
            context (Context): The context containing the scene and CAM chain information.

        Returns:
            bool: True if the active CAM chain is valid, False otherwise.
        """

        s = context.scene
        if len(s.cam_chains) > 0:
            chain = s.cam_chains[s.cam_active_chain]
            return chain_valid(chain, context)[0]
        else:
            return False

    async def execute_async(self, context):
        """Execute asynchronous operations for CAM path calculations.

        This method sets the object mode for the Blender scene and processes a
        series of CAM operations defined in the active CAM chain. It
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

        # Ensure there is an active object, and force Object Mode
        if not context.mode == "OBJECT":
            operations = context.scene.cam_operations
            active_operation = operations[context.scene.cam_active_operation]
            context_object = context.scene.objects[active_operation.object_name]
            context.view_layer.objects.active = context_object
            bpy.ops.object.mode_set(mode="OBJECT")

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
        export_gcode_path(chain.filename, meshes, chainops)
        return {"FINISHED"}


class PathExportChain(Operator):
    """Calculate a Chain and Export the G-code Together."""

    bl_idname = "object.cam_export_paths_chain"
    bl_label = "Export CAM Paths in Current Chain as G-code"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Check the validity of the active CAM chain in the given context.

        This method retrieves the currently active CAM chain from the scene
        context and checks its validity using the `isChainValid` function. It
        returns a boolean indicating whether the active CAM chain is valid or
        not.

        Args:
            context (object): The context containing the scene and CAM chain information.

        Returns:
            bool: True if the active CAM chain is valid, False otherwise.
        """

        s = context.scene
        chain = s.cam_chains[s.cam_active_chain]
        return chain_valid(chain, context)[0]

    def execute(self, context):
        """Execute the CAM path export process.

        This function retrieves the active CAM chain from the current scene
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
        export_gcode_path(chain.filename, meshes, chainops)
        return {"FINISHED"}


class PathExport(Operator):
    """Export G-code. Can Be Used only when the Path Object Is Present"""

    bl_idname = "object.cam_export"
    bl_label = "Export Operation G-code"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Execute the CAM operation and export the G-code path.

        This method retrieves the active CAM operation from the current scene
        and exports the corresponding G-code path to a specified filename. It
        prints the filename and relevant operation details to the console for
        debugging purposes. The G-code path is generated based on the CAM
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

        export_gcode_path(
            operation.filename,
            [bpy.data.objects["cam_path_{}".format(operation.name)].data],
            [operation],
        )
        return {"FINISHED"}
