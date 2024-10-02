"""CNC CAM 'pie_operation.py'

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
        pie.scale_y = 1.5

        # Left
        pie.operator(
            "wm.call_menu_pie",
            text='Area',
            icon='SHADING_BBOX'
        ).name = 'VIEW3D_MT_PIE_Area'
        # Right
        pie.operator(
            "wm.call_menu_pie",
            text='Optimisation',
            icon='MODIFIER'
        ).name = 'VIEW3D_MT_PIE_Optimisation'
        # Bottom
        pie.operator(
            "wm.call_menu_pie",
            text='Setup',
            icon='PREFERENCES'
        ).name = 'VIEW3D_MT_PIE_Setup'

        # Top
        box = pie.box()
        box.scale_x = 2
        box.scale_y = 1.5
        box.emboss = 'NONE'
        box.operator(
            "wm.call_menu_pie",
            text='',
            icon='HOME'
        ).name = 'VIEW3D_MT_PIE_CAM'

        # Top Left
        pie.operator(
            "wm.call_menu_pie",
            text='Movement',
            icon='ANIM_DATA'
        ).name = 'VIEW3D_MT_PIE_Movement'

        # Top Right
        pie.operator(
            "wm.call_menu_pie",
            text='Feedrate',
            icon='AUTO'
        ).name = 'VIEW3D_MT_PIE_Feedrate'

        # Bottom Left
        pie.operator(
            "wm.call_menu_pie",
            text='Cutter',
            icon='OUTLINER_DATA_GP_LAYER'
        ).name = 'VIEW3D_MT_PIE_Cutter'

        # Bottom Right
        pie.operator(
            "wm.call_menu_pie",
            text='G-Code Options',
            icon='EVENT_G'
        ).name = 'VIEW3D_MT_PIE_Gcode'
