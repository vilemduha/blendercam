"""Fabex 'pie_chains.py'

'Operations & Chains' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Chains(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operations & Chains    ∴"

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
            "wm.call_panel", text="Operations", icon="MOD_ENVELOPE"
        ).name = "FABEX_PT_CAM_OPERATIONS"

        # Right
        pie.operator("wm.call_panel", text="Chains", icon="LINKED").name = "FABEX_PT_CAM_CHAINS"

        # Bottom
        row = pie.row()
        row.label(text="")

        # Top
        box = pie.box()
        column = box.column(align=True)
        if operation.max_z > operation.movement.free_height:
            column.label(text="!ERROR! COLLISION!")
            column.label(text="Depth Start > Free Movement Height")
            column.label(text="!ERROR! COLLISION!")
            column.prop(operation.movement, "free_height")
            separator = column.separator(factor=1)
        column.scale_x = 2
        column.emboss = "NONE"
        column.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"
