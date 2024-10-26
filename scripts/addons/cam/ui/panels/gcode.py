"""Fabex 'gcode.py'

'CAM G-code Options' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_GCODE_Panel(CAMButtonsPanel, Panel):
    """CAM Operation G-code Options Panel"""

    bl_label = "CAM G-code Options"
    bl_idname = "WORLD_PT_CAM_GCODE"
    panel_interface_level = 1

    def draw(self, context):
        if self.level >= 1 and self.op is not None:
            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False

            col = layout.column(align=True)
            # Output Header
            col.prop(self.op, "output_header")
            if self.op.output_header:
                col.prop(self.op, "gcode_header")

            # Output Trailer
            col.prop(self.op, "output_trailer")
            if self.op.output_trailer:
                col.prop(self.op, "gcode_trailer")

            # Enable Dust
            col.prop(self.op, "enable_dust")
            if self.op.enable_dust:
                col.prop(self.op, "gcode_start_dust_cmd")
                col.prop(self.op, "gcode_stop_dust_cmd")

            # Enable Hold
            col.prop(self.op, "enable_hold")
            if self.op.enable_hold:
                col.prop(self.op, "gcode_start_hold_cmd")
                col.prop(self.op, "gcode_stop_hold_cmd")

            # Enable Mist
            col.prop(self.op, "enable_mist")
            if self.op.enable_mist:
                col.prop(self.op, "gcode_start_mist_cmd")
                col.prop(self.op, "gcode_stop_mist_cmd")
