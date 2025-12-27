"""Fabex 'strategy_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

from math import pi

import numpy as np

import bpy
from mathutils import (
    Euler,
    Vector,
)

from ..chunk_builder import (
    CamPathChunk,
    CamPathChunkBuilder,
)
from ..ui.icons import preview_collections
from .logging_utils import log
from .operation_utils import get_move_and_spin
from .orient_utils import (
    add_orientation_object,
    remove_orientation_object,
)
from .silhouette_utils import silhouette_offset
from .simple_utils import progress


def update_strategy(o, context):
    """Update the strategy of the given object.

    This function modifies the state of the object `o` by setting its
    `changed` attribute to True and printing a message indicating that the
    strategy is being updated. Depending on the value of `machine_axes` and
    `strategy_4_axis`, it either adds or removes an orientation object
    associated with `o`. Finally, it calls the `updateExact` function to
    perform further updates based on the provided context.

    Args:
        o (object): The object whose strategy is to be updated.
        context (object): The context in which the update is performed.
    """

    """"""
    o.changed = True
    log.info("Update Strategy")
    if o.machine_axes == "5" or (o.machine_axes == "4" and o.strategy_4_axis == "INDEXED"):
        # INDEXED 4 AXIS DOESN'T EXIST NOW...
        add_orientation_object(o)
    else:
        remove_orientation_object(o)
    update_exact(o, context)


def update_cutout(o, context):
    pass


def update_exact(o, context):
    """Update the state of an object for exact operations.

    This function modifies the properties of the given object `o` to
    indicate that an update is required. It sets various flags related to
    the object's state and checks the optimization settings. If the
    optimization is set to use exact mode, it further checks the strategy
    and inverse properties to determine if exact mode can be used. If not,
    it disables the use of OpenCamLib.

    Args:
        o (object): The object to be updated, which contains properties related
        context (object): The context in which the update is being performed.

    Returns:
        None: This function does not return a value.
    """

    log.info("Update Exact ")
    o.changed = True
    o.update_z_buffer_image_tag = True
    o.update_offset_image_tag = True
    if o.optimisation.use_exact:
        if o.strategy == "POCKET" or o.strategy == "MEDIAL_AXIS" or o.inverse:
            o.optimisation.use_opencamlib = False
            log.info("Current Operation Cannot Use Exact Mode")
    else:
        o.optimisation.use_opencamlib = False


def update_opencamlib_1(o, context):
    """Update the OpenCAMLib settings for a given operation.

    This function modifies the properties of the provided operation object
    based on its current strategy and optimization settings. If the
    operation's strategy is either 'POCKET' or 'MEDIAL_AXIS', and if
    OpenCAMLib is being used for optimization, it disables the use of both
    exact optimization and OpenCAMLib, indicating that the current operation
    cannot utilize OpenCAMLib.

    Args:
        o (object): The operation object containing optimization and strategy settings.
        context (object): The context in which the operation is being updated.

    Returns:
        None: This function does not return any value.
    """

    log.info("Update OpenCAMLib ")
    o.changed = True
    if o.optimisation.use_opencamlib and (o.strategy == "POCKET" or o.strategy == "MEDIAL_AXIS"):
        o.optimisation.use_exact = False
        o.optimisation.use_opencamlib = False
        log.info("Current Operation Cannot Use OpenCAMLib")


def get_strategy_list(scene, context):
    """Get a list of available strategies for operations.

    This function retrieves a predefined list of operation strategies that
    can be used in the context of a 3D scene. Each strategy is represented
    as a tuple containing an identifier, a user-friendly name, and a
    description of the operation. The list includes various operations such
    as cutouts, pockets, drilling, and more. If experimental features are
    enabled in the preferences, additional experimental strategies may be
    included in the returned list.

    Args:
        scene: The current scene context.
        context: The current context in which the operation is being performed.

    Returns:
        list: A list of tuples, each containing the strategy identifier,
            name, and description.
    """

    fabex_icons = preview_collections["FABEX"]

    items = [
        (
            "CUTOUT",
            "Profile (Cutout)",
            "Cut the silhouette with offset",
            fabex_icons["ProfileCutoutIcon"].icon_id,  #  "MOD_SKIN",
            0,
        ),
        (
            "POCKET",
            "Pocket",
            "Pocket operation",
            fabex_icons["PocketIcon"].icon_id,  #  "CLIPUV_DEHLT",
            1,
        ),
        (
            "DRILL",
            "Drill",
            "Drill operation",
            "DISCLOSURE_TRI_DOWN",
            2,
        ),
        (
            "PARALLEL",
            "Parallel",
            "Parallel lines on any angle",
            fabex_icons["ParallelIcon"].icon_id,  #  "SNAP_EDGE",
            3,
        ),
        (
            "CROSS",
            "Cross",
            "Cross paths",
            fabex_icons["CrossIcon"].icon_id,  #  "ADD",
            4,
        ),
        (
            "BLOCK",
            "Block",
            "Block path",
            fabex_icons["BlockIcon"].icon_id,  # "META_PLANE",
            5,
        ),
        (
            "SPIRAL",
            "Spiral",
            "Spiral path",
            fabex_icons["SpiralIcon"].icon_id,  # "FORCE_VORTEX",
            6,
        ),
        (
            "CIRCLES",
            "Circles",
            "Circles path",
            fabex_icons["CirclesIcon"].icon_id,  # "ONIONSKIN_ON",
            7,
        ),
        (
            "OUTLINEFILL",
            "Outline Fill",
            "Detect outline and fill it with paths as pocket. Then sample these paths on the 3d surface",
            "FULLSCREEN_EXIT",
            8,
        ),
        (
            "CARVE",
            "Project Curve to Surface",
            "Engrave the curve path to surface",
            "CON_SHRINKWRAP",
            9,
        ),
        (
            "WATERLINE",
            "Waterline - Roughing (Below Z0)",
            "Waterline paths - constant z below zero",
            fabex_icons["WaterlineIcon"].icon_id,  # "MOD_OCEAN",
            10,
        ),
        (
            "CURVE",
            "Curve to Path",
            "Curve object gets converted directly to path",
            "CURVE_DATA",
            11,
        ),
        (
            "MEDIAL_AXIS",
            "Medial Axis (V-Carve)",
            "Medial axis, must be used with V or ball cutter, for engraving various width shapes with a single stroke ",
            "SHARPCURVE",
            12,
        ),
    ]
    return items


def update_exact_mode(self, context):
    """Update the exact mode of the active CAM operation.

    This function retrieves the currently active CAM operation from the
    Blender context and updates its exact mode using the `updateExact`
    function. It accesses the active operation through the `cam_operations`
    list in the current scene and passes the active operation along with the
    current context to the `updateExact` function.

    Args:
        context: The context in which the update is performed.
    """

    # from . import updateExact
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    update_exact(active_op, bpy.context)


def update_opencamlib(self, context):
    """Update the OpenCamLib with the current active operation.

    This function retrieves the currently active CAM operation from the
    Blender context and updates the OpenCamLib accordingly. It accesses the
    active operation from the scene's CAM operations and passes it along
    with the current context to the update function.

    Args:
        context: The context in which the operation is being performed, typically
            provided by
            Blender's internal API.
    """

    # from . import updateOpencamlib
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    update_opencamlib_1(active_op, bpy.context)


# add pocket op for medial axis and profile cut inside to clean unremoved material
def add_pocket(max_depth, sname, new_cutter_diameter):
    """Add a pocket operation for the medial axis and profile cut.

    This function first deselects all objects in the scene and then checks
    for any existing medial pocket objects, deleting them if found. It
    verifies whether a medial pocket operation already exists in the CAM
    operations. If it does not exist, it creates a new pocket operation with
    the specified parameters. The function also modifies the selected
    object's silhouette offset based on the new cutter diameter.

    Args:
        max_depth (float): The maximum depth of the pocket to be created.
        sname (str): The name of the object to which the pocket will be added.
        new_cutter_diameter (float): The diameter of the new cutter to be used.
    """

    bpy.ops.object.select_all(action="DESELECT")
    scene = bpy.context.scene
    mpocket_exists = False

    # OBJECT name
    mp_ob_name = f"{sname}_medial_pocket"

    # Delete old Medial Pocket object, if one exists
    # [ob.select_set(True) for ob in scene.objects if ob.name.startswith(mp_ob_name)]
    for ob in scene.objects:
        if ob.name.startswith(mp_ob_name):
            ob.select_set(True)
            bpy.ops.object.delete()

    # OPERATION name
    mp_op_name = f"{sname}_MedialPocket"

    # Verify Medial Pocket Operation exists
    for op in scene.cam_operations:
        if op.name == mp_op_name:
            mpocket_exists = True

    # Modify Silhouette with Cutter Radius
    ob = bpy.data.objects[sname]
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    silhouette_offset(
        ob,
        -new_cutter_diameter / 2,
        1,
        2,
    )
    bpy.context.active_object.name = mp_ob_name
    m_ob = bpy.context.view_layer.objects.active
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    m_ob.location.z = max_depth

    # Create a Pocket Operation if it does not exist already
    if not mpocket_exists:
        scene.cam_operations.add()
        o = scene.cam_operations[-1]
        o.object_name = mp_ob_name
        scene.cam_active_operation = len(scene.cam_operations) - 1
        o.name = mp_op_name
        o.filename = o.name
        o.strategy = "POCKET"
        o.use_layers = False
        o.material.estimate_from_model = False
        o.material.size[2] = -max_depth


def parallel_pattern(o, angle):
    """Generate path chunks for parallel movement based on object dimensions
    and angle.

    This function calculates a series of path chunks for a given object,
    taking into account its dimensions and the specified angle. It utilizes
    both a traditional method and an alternative algorithm (currently
    disabled) to generate these paths. The paths are constructed by
    iterating over calculated vectors and applying transformations based on
    the object's properties. The resulting path chunks can be used for
    various movement types, including conventional and climb movements.

    Args:
        o (object): An object containing properties such as dimensions and movement type.
        angle (float): The angle to rotate the path generation.

    Returns:
        list: A list of path chunks generated based on the object's dimensions and
            angle.
    """

    zlevel = 1
    pathd = o.distance_between_paths
    pathstep = o.distance_along_paths
    pathchunks = []

    xm = (o.max.x + o.min.x) / 2
    ym = (o.max.y + o.min.y) / 2
    vm = Vector((xm, ym, 0))
    xdim = o.max.x - o.min.x
    ydim = o.max.y - o.min.y
    dim = (xdim + ydim) / 2.0
    e = Euler((0, 0, angle))
    reverse = False

    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)
    meander_reverse = reverse and o.movement.type == "MEANDER"
    step_back_reverse = reverse and o.movement.parallel_step_back

    # Original pattern method, slower, but well tested
    # bpy.app.debug_value has a default value of 0 (False), so
    # this check will always pass unless Blender is launched
    # with the correct command line options: -d, --debug
    if bpy.app.debug_value == 0:
        dirvect = Vector((0, 1, 0))
        dirvect.rotate(e)
        dirvect.normalize()
        dirvect *= pathstep
        for a in range(int(-dim / pathd), int(dim / pathd)):
            # this is highly ineffective, computes path2x the area needed...
            chunk = CamPathChunkBuilder([])
            v = Vector((a * pathd, int(-dim / pathstep) * pathstep, 0))
            v.rotate(e)
            # shifting for the rotation, so pattern rotates around middle...
            v += vm

            for b in range(int(-dim / pathstep), int(dim / pathstep)):
                v += dirvect

                if o.min.x < v.x < o.max.x and o.min.y < v.y < o.max.y:
                    chunk.points.append((v.x, v.y, zlevel))

            if meander_reverse or conventional_CW or climb_CCW:
                chunk.points.reverse()

            if len(chunk.points) > 0:
                pathchunks.append(chunk.to_chunk())

            # parallel step back - for finishing, best with climb movement, saves cutter life by going into
            # material with climb, while using move back on the surface to improve finish
            # (which would otherwise be a conventional move in the material)
            if len(pathchunks) > 1 and step_back_reverse and not o.use_layers:
                if o.movement.type == "CONVENTIONAL" or o.movement.type == "CLIMB":
                    pathchunks[-2].reverse()

                changechunk = pathchunks[-1]
                pathchunks[-1] = pathchunks[-2]
                pathchunks[-2] = changechunk

            reverse = not reverse

    # Alternative pattern algorithm using numpy, didn't work as should so blocked now...
    else:
        v = Vector((0, 1, 0))
        v.rotate(e)
        e1 = Euler((0, 0, -pi / 2))
        v1 = v.copy()
        v1.rotate(e1)
        axis_across_paths = np.array(
            (
                np.arange(int(-dim / pathd), int(dim / pathd)) * pathd * v1.x + xm,
                np.arange(int(-dim / pathd), int(dim / pathd)) * pathd * v1.y + ym,
                np.arange(int(-dim / pathd), int(dim / pathd)) * 0,
            )
        )
        axis_along_paths = np.array(
            (
                np.arange(int(-dim / pathstep), int(dim / pathstep)) * pathstep * v.x,
                np.arange(int(-dim / pathstep), int(dim / pathstep)) * pathstep * v.y,
                np.arange(int(-dim / pathstep), int(dim / pathstep)) * 0 + zlevel,
            )
        )
        # rotate this first
        progress(axis_along_paths)
        chunks = []

        for a in range(0, len(axis_across_paths[0])):
            nax = axis_along_paths.copy()
            nax[0] += axis_across_paths[0][a]
            nax[1] += axis_across_paths[1][a]
            xfitmin = nax[0] > o.min.x
            xfitmax = nax[0] < o.max.x
            xfit = xfitmin & xfitmax
            nax = np.array(
                [
                    nax[0][xfit],
                    nax[1][xfit],
                    nax[2][xfit],
                ]
            )
            yfitmin = nax[1] > o.min.y
            yfitmax = nax[1] < o.max.y
            yfit = yfitmin & yfitmax
            nax = np.array(
                [
                    nax[0][yfit],
                    nax[1][yfit],
                    nax[2][yfit],
                ]
            )
            chunks.append(nax.swapaxes(0, 1))

        pathchunks = [CamPathChunk(chunk.tolist()) for chunk in chunks]

    return pathchunks
