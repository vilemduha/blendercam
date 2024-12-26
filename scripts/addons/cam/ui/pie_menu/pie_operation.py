"""Fabex 'pie_operation.py'

'Active Operation' Pie Menu - Parent to all active_op Pie Menus
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Operation(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Active Operation    ∴"

    def draw(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()
        pie.scale_y = 2

        # Left
        pie.operator(
            "wm.call_panel", text="Area", icon="SHADING_BBOX"
        ).name = "FABEX_PT_CAM_OPERATION_AREA"
        # Right
        pie.operator(
            "wm.call_panel", text="Optimisation", icon="MODIFIER"
        ).name = "FABEX_PT_CAM_OPTIMISATION"
        # Bottom
        pie.operator(
            "wm.call_panel", text="Setup", icon="PREFERENCES"
        ).name = "FABEX_PT_CAM_OPERATION"

        # Top
        box = pie.box()
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"

        # Top Left
        pie.operator(
            "wm.call_panel", text="Movement", icon="ANIM_DATA"
        ).name = "FABEX_PT_CAM_MOVEMENT"

        # Top Right
        pie.operator("wm.call_panel", text="Feedrate", icon="AUTO").name = "FABEX_PT_CAM_FEEDRATE"

        # Bottom Left
        pie.operator(
            "wm.call_panel", text="Cutter", icon="OUTLINER_DATA_GP_LAYER"
        ).name = "FABEX_PT_CAM_CUTTER"

        # Bottom Right
        pie.operator(
            "wm.call_panel", text="G-Code Options", icon="EVENT_G"
        ).name = "FABEX_PT_CAM_GCODE"
