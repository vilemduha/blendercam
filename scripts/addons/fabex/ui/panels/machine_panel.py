"""Fabex 'machine.py'

'CAM Machine' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_MACHINE_Panel(CAMParentPanel, Panel):
    """CAM Machine Panel"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bl_label = "[ Machine ]"
    bl_idname = "FABEX_PT_CAM_MACHINE"
    panel_interface_level = 0
    always_show_panel = True

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

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

        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 1.2
        # Post Processor
        col.prop(self.machine, "post_processor")
        # System
        row = col.row(align=True)
        row.prop(context.scene.unit_settings, "system")
        row.prop(context.scene.unit_settings, "length_unit", text="")

        # Collet Size
        if self.level >= 2:
            box.prop(self.machine, "collet_size")

        # Working Area
        box.prop(self.machine, "working_area")

        # Supplemental Axis
        if self.level >= 3:
            row = box.row(align=True)
            row.prop(self.machine, "axis_4")
            row.prop(self.machine, "axis_5")

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
            header.label(text="Machine G-code")
            if panel:
                panel.use_property_split = False
                col = panel.column()
                # Tool Options
                if self.level >= 2:
                    col.prop(self.machine, "output_tool_definitions")
                    subheader, subpanel = col.panel(idname="tool_change", default_closed=False)
                    subheader.prop(self.machine, "output_tool_change")
                    if subpanel:
                        subpanel.enabled = self.machine.output_tool_change
                        subpanel.prop(self.machine, "output_G43_on_tool_change")

                # Block Numbers
                if self.level >= 2:
                    subheader, subpanel = col.panel(idname="block_numbers", default_closed=True)
                    subheader.prop(self.machine, "output_block_numbers")
                    if subpanel:
                        subpanel.enabled = self.machine.output_block_numbers
                        subpanel.use_property_split = True
                        column = subpanel.column(align=True)
                        column.prop(self.machine, "start_block_number")
                        column.prop(self.machine, "block_number_increment")

                # Split Files
                if self.level >= 2:
                    subheader, subpanel = col.panel(idname="split", default_closed=False)
                    subheader.prop(self.machine, "eval_splitting")
                    if subpanel:
                        subpanel.enabled = self.machine.eval_splitting
                        subpanel.use_property_split = True
                        subpanel.prop(self.machine, "split_limit")

            # Hourly Rate
            layout.prop(
                self.machine,
                "hourly_rate",
                text="Price ($/hour)",
            )
