"""CNC CAM 'gcode.py'

'CAM G-code Options' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_GCODE_Panel(CAMButtonsPanel, Panel):
    """CAM Operation G-code Options Panel"""

    bl_label = "CAM G-code Options"
    bl_idname = "WORLD_PT_CAM_GCODE"

    def draw(self, context):
        layout = self.layout

        if self.level >= 1 and self.op is not None:

            # Output Header
            layout.prop(self.op, "output_header")
            if self.op.output_header:
                layout.prop(self.op, "gcode_header")

            # Output Trailer
            layout.prop(self.op, "output_trailer")
            if self.op.output_trailer:
                layout.prop(self.op, "gcode_trailer")

            # Enable Dust
            layout.prop(self.op, "enable_dust")
            if self.op.enable_dust:
                layout.prop(self.op, "gcode_start_dust_cmd")
                layout.prop(self.op, "gcode_stop_dust_cmd")

            # Enable Hold
            layout.prop(self.op, "enable_hold")
            if self.op.enable_hold:
                layout.prop(self.op, "gcode_start_hold_cmd")
                layout.prop(self.op, "gcode_stop_hold_cmd")

            # Enable Mist
            layout.prop(self.op, "enable_mist")
            if self.op.enable_mist:
                layout.prop(self.op, "gcode_start_mist_cmd")
                layout.prop(self.op, "gcode_stop_mist_cmd")
