import bpy
from bpy.types import Menu


class Fabex_SubMenu(Menu):
    bl_label = "Fabex SubMenu"
    bl_idname = "OBJECT_MT_fabex_submenu"

    def draw(self, context):
        layout = self.layout
        layout.menu("OBJECT_MT_tools_curvetools")
        layout.menu("OBJECT_MT_tools_curvecreate")
        layout.operator("object.cam_pack_objects")
        layout.operator("object.cam_slice_objects", text="Slice Object")
        layout.operator("scene.calculate_bas_relief", text="Bas Relief")


class Fabex_Menu(Menu):
    bl_label = "Fabex Menu"
    bl_idname = "OBJECT_MT_fabex_menu"

    def draw(self, context):
        layout = self.layout

        if context.scene.render.engine == "FABEX_RENDER":
            layout.menu("OBJECT_MT_fabex_submenu", text="Fabex CNC")
        else:
            pass
