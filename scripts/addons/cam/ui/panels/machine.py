"""Fabex 'machine.py'

'CAM Machine' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_MACHINE_Panel(CAMButtonsPanel, Panel):
    """CAM Machine Panel"""

    bl_label = "Machine"
    bl_idname = "WORLD_PT_CAM_MACHINE"
    panel_interface_level = 0
    always_show_panel = True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Presets
        if self.level >= 1:
            row = layout.row(align=True)
            row.menu("CAM_MACHINE_MT_presets", text=bpy.types.CAM_MACHINE_MT_presets.bl_label)
            row.operator(
                "render.cam_preset_machine_add",
                text="",
                icon="ADD",
            )
            row.operator(
                "render.cam_preset_machine_add",
                text="",
                icon="REMOVE",
            ).remove_active = True

        col = layout.column(align=True)
        # Post Processor
        col.prop(self.machine, "post_processor")
        # System
        col.prop(context.scene.unit_settings, "system")
        col.prop(context.scene.unit_settings, "length_unit", text="Unit")

        # Supplemental Axis
        if self.level >= 3:
            col.prop(self.machine, "axis4")
            col.prop(self.machine, "axis5")

        # Collet Size
        if self.level >= 2:
            col.prop(self.machine, "collet_size")

        # Working Area
        layout.prop(self.machine, "working_area")

        # Position Definitions
        if self.level >= 2:
            header, panel = layout.panel_prop(self.machine, "use_position_definitions")
            header.label(text="Position Definitions")
            if panel:
                panel.prop(self.machine, "starting_position")
                panel.prop(self.machine, "mtc_position")
                panel.prop(self.machine, "ending_position")

        # Feedrates
        if self.level >= 1:
            header, panel = layout.panel(idname="feedrate", default_closed=True)
            header.label(text="Feedrate (/min)")
            if panel:
                panel.prop(self.machine, "feedrate_default", text="Default")
                col = panel.column(align=True)
                col.prop(self.machine, "feedrate_min", text="Minimum")
                col.prop(self.machine, "feedrate_max", text="Maximum")

        # Spindle Speeds
        # TODO: spindle default and feedrate default should become part of the cutter definition...
        header, panel = layout.panel(idname="spindle", default_closed=True)
        header.label(text="Spindle Speed (RPM)")
        if panel:
            panel.prop(self.machine, "spindle_default", text="Default")
            col = panel.column(align=True)
            col.prop(self.machine, "spindle_min", text="Minimum")
            col.prop(self.machine, "spindle_max", text="Maximum")
            panel.prop(self.machine, "spindle_start_time", text="Start Delay (seconds)")

        # Gcode Options
        if self.level >= 1:
            header, panel = layout.panel(idname="gcode", default_closed=True)
            header.label(text="Gcode Options")
            if panel:
                col = panel.column(align=True)
                # Tool Options
                if self.level >= 2:
                    col.prop(self.machine, "output_tool_definitions")
                    col.prop(self.machine, "output_tool_change")
                    if self.machine.output_tool_change:
                        col.prop(self.machine, "output_g43_on_tool_change")

                # Block Numbers
                if self.level >= 2:
                    col.prop(self.machine, "output_block_numbers")
                    if self.machine.output_block_numbers:
                        col.prop(self.machine, "start_block_number")
                        col.prop(self.machine, "block_number_increment")

                # Split Files
                if self.level >= 2:
                    col.prop(self.machine, "eval_splitting")
                    if self.machine.eval_splitting:
                        col.prop(self.machine, "split_limit")

            # Hourly Rate
            layout.prop(
                self.machine,
                "hourly_rate",
                text="Price ($/hour)",
            )
