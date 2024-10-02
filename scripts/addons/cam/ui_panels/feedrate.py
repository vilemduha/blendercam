"""CNC CAM 'feedrate.py'

'CAM Feedrate' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_FEEDRATE_Panel(CAMButtonsPanel, Panel):
    """CAM Feedrate Panel"""
    bl_label = "CAM Feedrate"
    bl_idname = "WORLD_PT_CAM_FEEDRATE"
    panel_interface_level = 0

    prop_level = {
        'draw_feedrate': 0,
        'draw_sim_feedrate': 2,
        'draw_plunge_feedrate': 1,
        'draw_plunge_angle': 1,
        'draw_spindle_rpm': 0
    }

    def draw_feedrate(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'feedrate')

    def draw_sim_feedrate(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'do_simulation_feedrate')

    def draw_plunge_feedrate(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'plunge_feedrate')

    def draw_plunge_angle(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'plunge_angle')

    def draw_spindle_rpm(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'spindle_rpm')

    def draw(self, context):
        self.context = context

        self.draw_feedrate()
        self.draw_sim_feedrate()
        self.draw_plunge_feedrate()
        self.draw_plunge_angle()
        self.draw_spindle_rpm()
