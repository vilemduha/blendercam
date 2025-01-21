"""Fabex 'strategy_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

import bpy

from .orient_utils import add_orientation_object, remove_orientation_object


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
    print("Update Strategy")
    if o.machine_axes == "5" or (
        o.machine_axes == "4" and o.strategy_4_axis == "INDEXED"
    ):  # INDEXED 4 AXIS DOESN'T EXIST NOW...
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

    print("Update Exact ")
    o.changed = True
    o.update_z_buffer_image_tag = True
    o.update_offset_image_tag = True
    if o.optimisation.use_exact:
        if o.strategy == "POCKET" or o.strategy == "MEDIAL_AXIS" or o.inverse:
            o.optimisation.use_opencamlib = False
            print("Current Operation Cannot Use Exact Mode")
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

    print("Update OpenCAMLib ")
    o.changed = True
    if o.optimisation.use_opencamlib and (o.strategy == "POCKET" or o.strategy == "MEDIAL_AXIS"):
        o.optimisation.use_exact = False
        o.optimisation.use_opencamlib = False
        print("Current Operation Cannot Use OpenCAMLib")


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

    items = [
        (
            "CUTOUT",
            "Profile (Cutout)",
            "Cut the silhouette with offset",
            "MOD_SKIN",
            0,
        ),
        (
            "POCKET",
            "Pocket",
            "Pocket operation",
            "CLIPUV_DEHLT",
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
            "SNAP_EDGE",
            3,
        ),
        (
            "CROSS",
            "Cross",
            "Cross paths",
            "ADD",
            4,
        ),
        (
            "BLOCK",
            "Block",
            "Block path",
            "META_PLANE",
            5,
        ),
        (
            "SPIRAL",
            "Spiral",
            "Spiral path",
            "FORCE_VORTEX",
            6,
        ),
        (
            "CIRCLES",
            "Circles",
            "Circles path",
            "ONIONSKIN_ON",
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
            "MOD_OCEAN",
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
            "Medial Axis",
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
