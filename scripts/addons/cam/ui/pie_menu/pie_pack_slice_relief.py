"""Fabex 'pie_pack_slice_relief.py'

'Pack, Slice and Bas Relief' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_PackSliceRelief(Menu):
    bl_label = "∴    Pack | Slice | Bas Relief    ∴"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()
        pie.scale_y = 2

        # Left
        pie.operator("wm.call_panel", text="Pack", icon="PACKAGE").name = "WORLD_PT_CAM_PACK"

        # Right
        pie.operator("wm.call_panel", text="Slice", icon="ALIGN_JUSTIFY").name = (
            "WORLD_PT_CAM_SLICE"
        )

        # Bottom
        pie.operator("wm.call_panel", text="Bas Relief", icon="RNDCURVE").name = (
            "WORLD_PT_BASRELIEF"
        )

        # Top
        column = pie.column()
        box = column.box()
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"
