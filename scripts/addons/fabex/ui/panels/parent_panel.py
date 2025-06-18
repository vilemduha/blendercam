"""Fabex 'buttons_panel.py'

Parent (Mixin) class for all panels in 'panels'
Sets up polling and operations to show / hide panels based on Interface Level
"""

import inspect

import bpy


# Panel definitions
class CAMParentPanel:
    always_show_panel = False
    COMPAT_ENGINES = {"FABEX_RENDER"}

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

    def __init__(self, *args, **kwargs):
        context = bpy.context

        self.level = int(context.scene.interface.level)
        self.machine = context.scene.cam_machine

        operations = context.scene.cam_operations
        operations_count = len(operations)
        operation_index = context.scene.cam_active_operation
        self.op = operations[operation_index] if operations_count > 0 else None

        # Auto-title and widen panels when called from pie_menu
        if not context.area.type == "PROPERTIES" and not context.region.type in ["UI", "TOOLS"]:
            self.layout.ui_units_x = 20
            self.layout.label(text=self.bl_label)
