import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_FEEDRATE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM feedrate panel"""
    bl_label = "CAM feedrate"
    bl_idname = "WORLD_PT_CAM_FEEDRATE"
    panel_interface_level = 0

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):

        self.layout.prop(ao, 'feedrate')
        self.layout.prop(ao, 'do_simulation_feedrate')
        self.layout.prop(ao, 'plunge_feedrate')
        self.layout.prop(ao, 'plunge_angle')
        self.layout.prop(ao, 'spindle_rpm')
