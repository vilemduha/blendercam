"""Fabex 'machine_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

import bpy

from ..constants import _IS_LOADING_DEFAULTS


def add_machine_area_object():
    """Add a machine area object to the current Blender scene.

    This function checks if a machine object named 'CAM_machine' already
    exists in the current scene. If it does not exist, it creates a new cube
    mesh object, applies transformations, and modifies its geometry to
    represent a machine area. The function ensures that the scene's unit
    settings are set to metric before creating the object and restores the
    original unit settings afterward. It also configures the display
    properties of the object for better visibility in the scene.  The
    function operates within Blender's context and utilizes various Blender
    operations to create and modify the mesh. It also handles the selection
    state of the active object.
    """

    s = bpy.context.scene
    ao = bpy.context.active_object
    if s.objects.get("CAM_machine") is not None:
        o = s.objects["CAM_machine"]
    else:
        oldunits = s.unit_settings.system
        oldLengthUnit = s.unit_settings.length_unit
        # need to be in metric units when adding machine mesh object
        # in order for location to work properly
        s.unit_settings.system = "METRIC"
        bpy.ops.mesh.primitive_cube_add(
            align="WORLD", enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0)
        )
        o = bpy.context.active_object
        o.name = "CAM_machine"
        o.data.name = "CAM_machine"
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        # o.type = 'SOLID'
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type="ONLY_FACE")
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE", action="TOGGLE")
        bpy.ops.mesh.select_all(action="TOGGLE")
        bpy.ops.mesh.subdivide(
            number_cuts=32,
            smoothness=0,
            quadcorner="STRAIGHT_CUT",
            fractal=0,
            fractal_along_normal=0,
            seed=0,
        )
        bpy.ops.mesh.select_nth(nth=2, offset=0)
        bpy.ops.mesh.delete(type="EDGE")
        bpy.ops.mesh.primitive_cube_add(
            align="WORLD", enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0)
        )

        bpy.ops.object.editmode_toggle()
        o.display_type = "BOUNDS"
        o.hide_render = True
        o.hide_select = True
        s.unit_settings.system = oldunits
        s.unit_settings.length_unit = oldLengthUnit

    o.dimensions = bpy.context.scene.cam_machine.working_area
    if ao is not None:
        ao.select_set(True)


def update_machine(self, context):
    """Update the machine with the given context.

    This function is responsible for updating the machine state based on the
    provided context. It prints a message indicating that the update process
    has started. If the global variable _IS_LOADING_DEFAULTS is not set to
    True, it proceeds to add a machine area object.

    Args:
        context: The context in which the machine update is being performed.
    """

    print("Update Machine")
    if not _IS_LOADING_DEFAULTS:
        add_machine_area_object()
