"""CNC CAM 'machine.py'

'CAM Machine' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_MACHINE_Panel(CAMButtonsPanel, Panel):
    """CAM Machine Panel"""

    bl_label = "CAM Machine"
    bl_idname = "WORLD_PT_CAM_MACHINE"

    def draw(self, context):
        layout = self.layout

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

        # Post Processor
        layout.prop(self.machine, "post_processor")

        # Split Files
        if self.level >= 2:
            layout.prop(self.machine, "eval_splitting")
            if self.machine.eval_splitting:
                layout.prop(self.machine, "split_limit")

        # System
        layout.prop(bpy.context.scene.unit_settings, "system")

        # Position Definitions
        if self.level >= 2:
            layout.prop(self.machine, "use_position_definitions")
            if self.machine.use_position_definitions:
                layout.prop(self.machine, "starting_position")
                layout.prop(self.machine, "mtc_position")
                layout.prop(self.machine, "ending_position")

        # Working Area
        layout.prop(self.machine, "working_area")

        # Feedrates
        if self.level >= 1:
            layout.prop(self.machine, "feedrate_min")
            layout.prop(self.machine, "feedrate_max")
            layout.prop(self.machine, "feedrate_default")

        # Spindle Speeds
        # TODO: spindle default and feedrate default should become part of the cutter definition...
        layout.prop(self.machine, "spindle_min")
        layout.prop(self.machine, "spindle_max")
        layout.prop(self.machine, "spindle_start_time")
        layout.prop(self.machine, "spindle_default")

        # Tool Options
        if self.level >= 2:
            layout.prop(self.machine, "output_tool_definitions")
            layout.prop(self.machine, "output_tool_change")
            if self.machine.output_tool_change:
                layout.prop(self.machine, "output_g43_on_tool_change")

        # Supplemental Axis
        if self.level >= 3:
            layout.prop(self.machine, "axis4")
            layout.prop(self.machine, "axis5")

        # Collet Size
        if self.level >= 2:
            layout.prop(self.machine, "collet_size")

        # Block Numbers
        if self.level >= 2:
            layout.prop(self.machine, "output_block_numbers")
            if self.machine.output_block_numbers:
                layout.prop(self.machine, "start_block_number")
                layout.prop(self.machine, "block_number_increment")

        # Hourly Rate
        if self.level >= 1:
            layout.prop(self.machine, "hourly_rate")
