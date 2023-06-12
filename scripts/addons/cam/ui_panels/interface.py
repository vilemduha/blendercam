
import bpy
import math
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants

class CAM_INTERFACE_Properties(bpy.types.PropertyGroup):
    interface_level: bpy.props.EnumProperty(
        name="Interface",
        description="Choose the interface details",
        items=[('0', "Basic", "Basic interface"),
               ('1', "Advanced", "Advanced interface"),
               ('2', "Complete", "Complete interface")],
        default='0',
    )

class CAM_INTERFACE_Panel(CAMButtonsPanel, bpy.types.Panel):
    bl_label = "CAM interface"
    bl_idname = "WORLD_PT_CAM_INTERFACE"
    always_show_panel = True

    def draw_interface_level(self):
        self.layout.prop(self.op.interface, 'interface_level')

    def draw(self, context):
        self.context = context
        scene = bpy.context.scene

        self.draw_interface_level()
