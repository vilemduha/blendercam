import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_FEEDRATE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM feedrate panel"""
    bl_label = "CAM feedrate"
    bl_idname = "WORLD_PT_CAM_FEEDRATE"
    panel_interface_level = 0

    prop_level = {
        'feedrate': 0,
        'sim_feedrate': 2,
        'plunge_feedrate': 1,
        'plunge_angle': 1,
        'spindle_rpm': 0
    }

    def draw_feedrate(self):
        if not self.has_correct_level('feedrate'): return
        self.layout.prop(self.op, 'feedrate')

    def draw_sim_feedrate(self):
        if not self.has_correct_level('sim_feedrate'): return
        self.layout.prop(self.op, 'do_simulation_feedrate')

    def draw_plunge_feedrate(self):
        if not self.has_correct_level('plunge_feedrate'): return
        self.layout.prop(self.op, 'plunge_feedrate')

    def draw_plunge_angle(self):
        if not self.has_correct_level('plunge_angle'): return
        self.layout.prop(self.op, 'plunge_angle')

    def draw_spindle_rpm(self):
        if not self.has_correct_level('spindle_rpm'): return
        self.layout.prop(self.op, 'spindle_rpm')

    def draw(self, context):
        self.context = context

        self.draw_feedrate()
        self.draw_sim_feedrate()
        self.draw_plunge_feedrate()
        self.draw_plunge_angle()
        self.draw_spindle_rpm()
