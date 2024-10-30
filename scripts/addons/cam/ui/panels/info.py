"""Fabex 'info.py'

'CAM Info & Warnings' properties and panel in Properties > Render
"""

from datetime import timedelta

import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
)
from bpy.types import (
    Panel,
    PropertyGroup,
)
from .buttons_panel import CAMButtonsPanel
from ...utils import (
    update_operation,
)
from ...constants import (
    PRECISION,
    CHIPLOAD_PRECISION,
    MAX_OPERATION_TIME,
)
from ...simple import strInUnits
from ...version import __version__ as cam_version

# Info panel
# This panel gives general information about the current operation


class CAM_INFO_Properties(PropertyGroup):

    warnings: StringProperty(
        name="Warnings",
        description="Warnings",
        default="",
        update=update_operation,
    )

    chipload: FloatProperty(
        name="Chipload",
        description="Calculated chipload",
        default=0.0,
        unit="LENGTH",
        precision=CHIPLOAD_PRECISION,
    )

    duration: FloatProperty(
        name="Estimated Time",
        default=0.01,
        min=0.0000,
        max=MAX_OPERATION_TIME,
        precision=PRECISION,
        unit="TIME",
    )


class CAM_INFO_Panel(CAMButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # bl_category = "CNC"
    bl_options = {"HIDE_HEADER"}
    bl_order = 3

    bl_label = "Info & Warnings"
    bl_idname = "WORLD_PT_CAM_INFO"
    panel_interface_level = 0
    always_show_panel = True

    # Display the Info Panel
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        main = layout.box()
        main.label(text=f'Fabex v{".".join([str(x) for x in cam_version])}', icon="INFO")
        if context.window_manager.progress > 0:
            col = main.column(align=True)
            col.scale_y = 2
            percent = int(context.window_manager.progress * 100)
            col.progress(
                factor=context.window_manager.progress,
                text=f"Processing...{percent}% (Esc to Cancel)",
            )
        if self.op is None:
            return
        else:
            if not self.op.info.warnings == "":
                # Operation Warnings
                box = main.box()
                col = box.column(align=True)
                col.alert = True
                col.label(text="Warning!", icon="ERROR")
                for line in self.op.info.warnings.rstrip("\n").split("\n"):
                    if len(line) > 0:
                        col.label(text=line, icon="ERROR")

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
            col.label(text=f"Operation Duration: {time_estimate}", icon="TIME")

            # Operation Chipload
            if not self.op.info.chipload > 0:
                return

            chipload = f"Chipload: {strInUnits(self.op.info.chipload, 4)}/tooth"
            col.label(text=chipload)

            # Operation Money Cost
            if self.level >= 1:
                if not int(self.op.info.duration * 60) > 0:
                    return

                row = main.row()
                row.label(text="Hourly Rate")
                row.prop(bpy.context.scene.cam_machine, "hourly_rate", text="")

                if float(bpy.context.scene.cam_machine.hourly_rate) < 0.01:
                    return

                cost_per_second = bpy.context.scene.cam_machine.hourly_rate / 3600
                total_cost = self.op.info.duration * 60 * cost_per_second
                op_cost = f"Operation Cost: ${total_cost:.2f} (${cost_per_second:.2f}/s)"
                main.label(text=op_cost)
