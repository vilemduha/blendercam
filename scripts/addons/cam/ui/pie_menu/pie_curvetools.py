"""Fabex 'pie_curvetools.py'

'Curve Tools' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_CurveTools(Menu):
    bl_label = "∴    Curve Tools    ∴"

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column(align=True)
        column.operator("object.curve_boolean")
        column.operator("object.convex_hull")
        column.operator("object.curve_intarsion")

        # Right
        box = pie.box()
        column = box.column(align=True)
        column.operator("object.curve_overcuts")
        column.operator("object.curve_overcuts_b")

        # Bottom
        box = pie.box()
        column = box.column(align=True)
        column.operator("object.silhouete")
        column.operator("object.silhouete_offset")
        column.operator("object.curve_remove_doubles")
        column.operator("object.mesh_get_pockets")

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"
