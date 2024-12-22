import bpy
from bpy.types import Menu


class VIEW3D_MT_tools_curvetools(Menu):
    bl_label = "Curve Tools"
    bl_idname = "OBJECT_MT_tools_curvetools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_boolean")
        layout.operator("object.convex_hull")
        layout.operator("object.curve_intarsion")
        layout.operator("object.curve_overcuts")
        layout.operator("object.curve_overcuts_b")
        # layout.operator("object.silhouette")
        layout.operator("object.silhouette_offset")
        layout.operator("object.curve_remove_doubles")
        layout.operator("object.mesh_get_pockets")
        layout.operator("object.cam_pack_objects")
        layout.operator("object.cam_slice_objects", text="Slice Objects")
