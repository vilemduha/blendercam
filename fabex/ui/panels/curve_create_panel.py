"""Fabex 'curve_creators.py' © 2012 Vilem Novak

Panels displayed in the 3D Viewport - Curve Tools, Creators and Import G-code
"""

from bpy.types import Panel


class VIEW3D_PT_tools_create(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "[ Curve Creators ]"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        col = layout.column(align=True)
        col.operator("object.curve_plate", icon="META_PLANE")
        col.operator("object.curve_drawer", icon="CON_SAMEVOL")
        col.operator("object.curve_mortise", icon="CHECKBOX_DEHLT")
        col.operator("object.curve_interlock", icon="REMOVE")
        col.operator("object.curve_puzzle", icon="HAND")
        col.operator("object.sine", icon="FORCE_HARMONIC")
        col.operator("object.lissajous", icon="VIEW_ORTHO")
        col.operator("object.hypotrochoid", icon="SHADING_WIRE", text="Hypotrochoid Figure")
        col.operator("object.customcurve", icon="IPO_BOUNCE")
        col.operator("object.curve_hatch", icon="OUTLINER_DATA_LIGHTPROBE")
        col.operator("object.curve_gear", icon="PREFERENCES")
        col.operator("object.curve_flat_cone", icon="MESH_CONE")
