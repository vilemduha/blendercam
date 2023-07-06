
import bpy
import math
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants

class CAM_INTERFACE_Properties(bpy.types.PropertyGroup):
    level: bpy.props.EnumProperty(
        name="Interface",
        description="Choose visible options",
        items=[('0', "Basic", "Only show essential options"),
               ('1', "Advanced", "Show advanced options"),
               ('2', "Complete", "Show all options")],
        default='0',
    )

class CAM_INTERFACE_Panel(CAMButtonsPanel, bpy.types.Panel):
    bl_label = "Interface"
    bl_idname = "WORLD_PT_CAM_INTERFACE"
    always_show_panel = True

    def draw_interface_level(self):
        self.layout.prop(self.context.scene.interface, 'level', text='')

    def draw(self, context):
        self.context = context
        self.draw_interface_level()
