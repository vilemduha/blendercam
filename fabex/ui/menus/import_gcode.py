import bpy
from bpy.types import Menu


class TOPBAR_MT_import_gcode(Menu):
    bl_idname = "TOPBAR_MT_import_gcode"
    bl_label = "Import G-Code"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.gcode_import", text="Import G-Code (.gcode)")
