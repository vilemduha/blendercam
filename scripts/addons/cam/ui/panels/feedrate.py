"""Fabex 'feedrate.py'

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

    def draw(self, context):
        layout = self.layout
        # Feedrate
        layout.prop(self.op, "feedrate")

        # Sim Feedrate
        if self.level >= 2:
            layout.prop(self.op, "do_simulation_feedrate")

        # Plunge Feedrate
        if self.level >= 1:
            layout.prop(self.op, "plunge_feedrate")
            # Plunge Angle
            layout.prop(self.op, "plunge_angle")

        # Spindle RPM
        layout.prop(self.op, "spindle_rpm")
