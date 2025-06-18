"""Fabex 'info.py'

'CAM Info & Warnings' properties and panel in Properties > Render
"""

from datetime import timedelta

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


# Info panel
# This panel gives general information about the current operation
class CAM_INFO_Panel(CAMParentPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {"HIDE_HEADER"}

    bl_label = "Info & Warnings"
    bl_idname = "FABEX_PT_CAM_INFO"
    panel_interface_level = 0
    always_show_panel = True

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    # Display the Info Panel
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        main = layout.box()
        main.label(text=f"[ Info ]", icon="INFO")
        if context.window_manager.progress > 0:
            col = main.column(align=True)
            col.scale_y = 2
            percent = int(context.window_manager.progress * 100)
            col.progress(
                factor=context.window_manager.progress,
                text=f"Processing...{percent}%",
            )
        if self.op is None:
            return
        else:
            if not self.op.info.warnings == "":
                # Operation Warnings
                box = main.box()
                col = box.column(align=True)
                col.alert = True
                col.label(text="!!! WARNING !!!", icon="ERROR")
                for line in self.op.info.warnings.rstrip("\n").split("\n"):
                    if len(line) > 0:
                        icon = "BLANK1"
                        if line.startswith(("Path", "Operation", "X", "Y", "Z")):
                            icon = "MOD_WIREFRAME"
                        if line.startswith(("Memory", "Detail")):
                            icon = "MEMORY"
                        if line.startswith(("!!!")):
                            icon = "ERROR"
                        col.label(text=line, icon=icon)

            # Cutter Engagement
            if not self.op.strategy == "CUTOUT" and not self.op.cutter_type in ["LASER", "PLASMA"]:
                box = main.box()
                col = box.column(align=True)
                # Warns if cutter engagement is greater than 50%
                if self.op.cutter_type in ["BALLCONE"]:
                    engagement = round(
                        100 * self.op.distance_between_paths / self.op.ball_radius, 1
                    )
                else:
                    engagement = round(
                        100 * self.op.distance_between_paths / self.op.cutter_diameter, 1
                    )

                if engagement > 50:
                    col.alert = True
                    col.label(text="Warning: High Cutter Engagement", icon="ERROR")

                col.label(text="Cutter Engagement")
                row = col.split(factor=0.32)
                col_1 = row.column(align=True)
                col_1.alignment = "RIGHT"
                col_1.label(text="CWE:")
                col_2 = row.column(align=True)
                col_2.alignment = "LEFT"
                col_2.label(text=f"{engagement}%", icon="STYLUS_PRESSURE")

            # Operation Time Estimate
            duration = self.op.info.duration
            seconds = int(duration * 60)
            if not seconds > 0:
                return

            time_estimate = str(timedelta(seconds=seconds))
            split = time_estimate.split(":")
            split[0] += "h "
            split[1] += "m "
            split[2] += "s"
            time_estimate = split[0] + split[1] + split[2]

            box = main.box()
            col = box.column(align=True)
            col.label(text="Estimates")
            row = col.split(factor=0.32)
            title_col = row.column(align=True)
            title_col.alignment = "RIGHT"
            value_col = row.column(align=True)
            value_col.alignment = "LEFT"

            title_col.label(text="Time:")
            value_col.label(text=time_estimate, icon="TIME")

            # Operation Chipload
            if self.op.info.chipload > 0:
                chipload = self.op.feedrate / (self.op.spindle_rpm * self.op.cutter_flutes)
                chipload = f"{chipload:.5f}"
                title_col.label(text=f"Chipload:")
                value_col.label(
                    text=chipload,
                    icon="DRIVER_ROTATIONAL_DIFFERENCE",
                )
            else:
                pass

            # Operation Money Cost
            if self.level >= 1:
                if not int(self.op.info.duration * 60) > 0:
                    return

                if float(bpy.context.scene.cam_machine.hourly_rate) < 0.01:
                    return

                cost_per_second = bpy.context.scene.cam_machine.hourly_rate / 3600
                total_cost = self.op.info.duration * 6000 * cost_per_second
                op_cost = f"${total_cost:.2f}"  # (${cost_per_second:.2f}/s)"
                title_col.label(text="Cost:")
                value_col.label(text=op_cost, icon="TAG")
