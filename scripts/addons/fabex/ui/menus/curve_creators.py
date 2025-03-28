import bpy
from bpy.types import Menu


class VIEW3D_MT_tools_add(Menu):
    bl_idname = "VIEW3D_MT_tools_add"
    bl_label = "Curve CAM Creators"

    def draw(self, context):
        layout = self.layout
        layout.menu("OBJECT_MT_tools_curvecreate", icon="FCURVE", text="Curve CAM Creators")


class VIEW3D_MT_tools_create(Menu):
    bl_idname = "OBJECT_MT_tools_curvecreate"
    bl_label = "Curve Creators"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_plate")
        layout.operator("object.curve_drawer")
        layout.operator("object.curve_mortise")
        layout.operator("object.curve_interlock")
        layout.operator("object.curve_puzzle")
        layout.operator("object.sine")
        layout.operator("object.lissajous")
        layout.operator("object.hypotrochoid")
        layout.operator("object.customcurve")
        layout.operator("object.curve_hatch")
        layout.operator("object.curve_gear")
        layout.operator("object.curve_flat_cone")
