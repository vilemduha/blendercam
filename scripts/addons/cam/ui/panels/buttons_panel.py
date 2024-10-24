"""CNC CAM 'buttons_panel.py'

Parent (Mixin) class for all panels in 'panels'
Sets up polling and operations to show / hide panels based on Interface Level
"""

import inspect

import bpy


# Panel definitions
class CAMButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    always_show_panel = False
    COMPAT_ENGINES = {"CNCCAM_RENDER"}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        engine_check = engine in cls.COMPAT_ENGINES

        show_check = cls.always_show_panel

        operations = context.scene.cam_operations
        operations_count = len(operations)
        operation_index = context.scene.cam_active_operation
        operation = operations[operation_index] if operations_count > 0 else None
        op_check = operation is not None

        level = int(context.scene.interface.level)
        level_check = cls.panel_interface_level <= level

        check_1 = engine_check and show_check
        check_2 = engine_check and op_check and level_check

        return True if check_1 or check_2 else False

    def __init__(self):
        context = bpy.context

        self.level = int(context.scene.interface.level)
        self.machine = context.scene.cam_machine

        addon_prefs = context.preferences.addons["bl_ext.user_default.blendercam"].preferences
        self.use_experimental = addon_prefs.experimental

        operations = context.scene.cam_operations
        operations_count = len(operations)
        operation_index = context.scene.cam_active_operation
        self.op = operations[operation_index] if operations_count > 0 else None
