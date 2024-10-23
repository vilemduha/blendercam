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
    COMPAT_ENGINES = {"CNCCAM_RENDER"}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return [True if engine in cls.COMPAT_ENGINES else False]

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
