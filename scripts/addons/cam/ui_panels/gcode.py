import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_GCODE_Panel(CAMButtonsPanel, Panel):
    """CAM Operation G-code Options Panel"""
    bl_label = "CAM G-code Options"
    bl_idname = "WORLD_PT_CAM_GCODE"
    panel_interface_level = 1

    prop_level = {
        'draw_output_header': 1,
        'draw_output_trailer': 1,
        'draw_enable_dust': 1,
        'draw_enable_hold': 1,
        'draw_enable_mist': 1
    }

    def draw_output_header(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'output_header')
        if self.op.output_header:
            self.layout.prop(self.op, 'gcode_header')

    def draw_output_trailer(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'output_trailer')
        if self.op.output_trailer:
            self.layout.prop(self.op, 'gcode_trailer')

    def draw_enable_dust(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'enable_dust')
        if self.op.enable_dust:
            self.layout.prop(self.op, 'gcode_start_dust_cmd')
            self.layout.prop(self.op, 'gcode_stop_dust_cmd')

    def draw_enable_hold(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'enable_hold')
        if self.op.enable_hold:
            self.layout.prop(self.op, 'gcode_start_hold_cmd')
            self.layout.prop(self.op, 'gcode_stop_hold_cmd')

    def draw_enable_mist(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'enable_mist')
        if self.op.enable_mist:
            self.layout.prop(self.op, 'gcode_start_mist_cmd')
            self.layout.prop(self.op, 'gcode_stop_mist_cmd')

    def draw(self, context):
        self.context = context

        self.draw_output_header()
        self.draw_output_trailer()
        self.draw_enable_dust()
        self.draw_enable_hold()
        self.draw_enable_mist()
