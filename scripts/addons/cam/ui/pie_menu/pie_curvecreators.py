"""Fabex 'pie_curvecreators.py'

'Curve Creators' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_CurveCreators(Menu):
    bl_label = "∴    Curve Creators    ∴"

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column(align=True)
        column.operator("object.curve_plate")
        column.operator("object.curve_drawer")
        column.operator("object.curve_mortise")
        column.operator("object.curve_interlock")

        # Right
        box = pie.box()
        column = box.column(align=True)
        column.operator("object.curve_puzzle")
        column.operator("object.sine")
        column.operator("object.lissajous")
        column.operator("object.hypotrochoid")

        # Bottom
        box = pie.box()
        column = box.column(align=True)
        column.operator("object.customcurve")
        column.operator("object.curve_hatch")
        column.operator("object.curve_gear")
        column.operator("object.curve_flat_cone")

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"
