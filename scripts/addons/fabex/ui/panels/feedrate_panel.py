"""Fabex 'feedrate.py'

'CAM Feedrate' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_FEEDRATE_Panel(CAMParentPanel, Panel):
    """CAM Feedrate Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Feedrate ]"
    bl_idname = "FABEX_PT_CAM_FEEDRATE"
    panel_interface_level = 0

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Feedrate
        layout.prop(self.op, "feedrate", text="Feedrate (/min)")

        # Spindle RPM
        layout.prop(self.op, "spindle_rpm", text="Spindle (RPM)")

        # Plunge Feedrate
        if self.level >= 1:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Plunge")
            col.prop(self.op, "plunge_feedrate", text="Speed")
            # Plunge Angle
            col.prop(self.op, "plunge_angle", text="Angle")

        # Sim Feedrate
        if self.level >= 3:
            header, panel = layout.panel("sim_feedrate", default_closed=True)
            header.label(text="╼ EXPERIMENTAL ╾", icon="EXPERIMENTAL")
            if panel:
                col = panel.column(align=True)
                col.use_property_split = False
                col.prop(
                    self.op,
                    "do_simulation_feedrate",
                    text="Adjust Feedrate with Simulation",
                )
