"""Fabex 'gcode.py'

'CAM G-code Options' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_GCODE_Panel(CAMParentPanel, Panel):
    """CAM Operation G-code Options Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Operation G-code ]"
    bl_idname = "FABEX_PT_CAM_GCODE"
    panel_interface_level = 1

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    def draw(self, context):
        if self.level >= 1 and self.op is not None:
            layout = self.layout
            layout.use_property_decorate = False
            layout.use_property_split = False

            # Output Header
            header, panel = layout.panel("header", default_closed=True)
            header.prop(self.op, "output_header", text="Output Header")
            if panel:
                panel.enabled = self.op.output_header
                col = panel.column(align=True)
                col.use_property_split = True
                col.prop(self.op, "gcode_header", text="Commands")

            # Output Trailer
            header, panel = layout.panel("trailer", default_closed=True)
            header.prop(self.op, "output_trailer", text="Output Trailer")
            if panel:
                panel.enabled = self.op.output_trailer
                col = panel.column(align=True)
                col.use_property_split = True
                col.prop(self.op, "gcode_trailer", text="Commands")

            # Enable Dust Collector
            header, panel = layout.panel("dust", default_closed=True)
            header.prop(self.op, "enable_dust", text="Dust Collector")
            if panel:
                panel.enabled = self.op.enable_dust
                col = panel.column(align=True)
                col.use_property_split = True
                col.prop(self.op, "gcode_start_dust_cmd", text="Start")
                col.prop(self.op, "gcode_stop_dust_cmd", text="Stop")

            # Enable Hold Down
            header, panel = layout.panel("hold", default_closed=True)
            header.prop(self.op, "enable_hold", text="Hold Down")
            if panel:
                panel.enabled = self.op.enable_hold
                col = panel.column(align=True)
                col.use_property_split = True
                col.prop(self.op, "gcode_start_hold_cmd", text="Start")
                col.prop(self.op, "gcode_stop_hold_cmd", text="Stop")

            # Enable Mist
            header, panel = layout.panel("mist", default_closed=True)
            header.prop(self.op, "enable_mist", text="Mist")
            if panel:
                panel.enabled = self.op.enable_mist
                col = panel.column(align=True)
                col.use_property_split = True
                col.prop(self.op, "gcode_start_mist_cmd", text="Start")
                col.prop(self.op, "gcode_stop_mist_cmd", text="Stop")
