"""Fabex 'info.py'

'CAM Info & Warnings' properties and panel in Properties > Render
"""

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
    opencamlib_version,
    update_operation,
)
from ...constants import (
    PRECISION,
    CHIPLOAD_PRECISION,
    MAX_OPERATION_TIME,
)
from ...version import __version__ as cam_version
from ...simple import strInUnits

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
    bl_label = "CAM Info & Warnings"
    bl_idname = "WORLD_PT_CAM_INFO"
    panel_interface_level = 0
    always_show_panel = True

    # Display the Info Panel
    def draw(self, context):
        layout = self.layout

        # Fabex Version
        layout.label(text=f'Fabex v{".".join([str(x) for x in cam_version])}')

        # OpenCAMLib Version
        if self.level >= 1:
            ocl_version = opencamlib_version()
            if ocl_version is None:
                layout.label(text="OpenCAMLib is not Installed")
            else:
                layout.label(text=f"OpenCAMLib v{ocl_version}")

        if self.op is None:
            return
        else:
            # Operation Warnings
            for line in self.op.info.warnings.rstrip("\n").split("\n"):
                if len(line) > 0:
                    layout.label(text=line, icon="ERROR")

            # Operation Time Estimate
            if not int(self.op.info.duration * 60) > 0:
                return

            time_estimate = f"Operation Duration: {int(self.op.info.duration*60)}s "
            if self.op.info.duration > 60:
                time_estimate += f" ({int(self.op.info.duration / 60)}h"
                time_estimate += f" {round(self.op.info.duration % 60)}min)"
            elif self.op.info.duration > 1:
                time_estimate += f" ({round(self.op.info.duration % 60)}min)"

            layout.label(text=time_estimate)

            # Operation Chipload
            if not self.op.info.chipload > 0:
                return

            chipload = f"Chipload: {strInUnits(self.op.info.chipload, 4)}/tooth"
            layout.label(text=chipload)

            # Operation Money Cost
            if self.level >= 1:
                if not int(self.op.info.duration * 60) > 0:
                    return

                row = self.layout.row()
                row.label(text="Hourly Rate")
                row.prop(bpy.context.scene.cam_machine, "hourly_rate", text="")

                if float(bpy.context.scene.cam_machine.hourly_rate) < 0.01:
                    return

                cost_per_second = bpy.context.scene.cam_machine.hourly_rate / 3600
                total_cost = self.op.info.duration * 60 * cost_per_second
                op_cost = f"Operation Cost: ${total_cost:.2f} (${cost_per_second:.2f}/s)"
                layout.label(text=op_cost)
