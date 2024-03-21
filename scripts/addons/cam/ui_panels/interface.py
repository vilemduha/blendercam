
import bpy
import math
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants


def update_interface(self, context):
    # set default for new files
    context.preferences.addons['cam'].preferences.default_interface_level = context.scene.interface.level
    bpy.ops.wm.save_userpref()


class CAM_INTERFACE_Properties(bpy.types.PropertyGroup):
    level: bpy.props.EnumProperty(
        name="Interface",
        description="Choose visible options",
        items=[('0', "Basic", "Only show essential options"),
               ('1', "Advanced", "Show advanced options"),
               ('2', "Complete", "Show all options"),
               ('3', "Experimental", "Show experimental options")],
        default='0',
        update=update_interface
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
