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
from ..utils import (
    opencamlib_version,
    update_operation,
)
from ..constants import (
    PRECISION,
    CHIPLOAD_PRECISION,
    MAX_OPERATION_TIME,
)
from ..version import __version__ as cam_version
from ..simple import strInUnits

# Info panel
# This panel gives general information about the current operation


class CAM_INFO_Properties(PropertyGroup):

    warnings: StringProperty(
        name='Warnings',
        description='Warnings',
        default='',
        update=update_operation,
    )

    chipload: FloatProperty(
        name="Chipload",
        description="Calculated chipload",
        default=0.0, unit='LENGTH',
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

    prop_level = {
        'draw_blendercam_version': 0,
        'draw_opencamlib_version': 1,
        'draw_op_warnings': 0,
        'draw_op_time': 0,
        'draw_op_chipload': 0,
        'draw_op_money_cost': 1,
    }

    # Draw blendercam version (and whether there are updates available)
    def draw_blendercam_version(self):
        if not self.has_correct_level():
            return
        self.layout.label(
            text=f'BlenderCAM v{".".join([str(x) for x in cam_version])}')
        if len(bpy.context.preferences.addons['cam'].preferences.new_version_available) > 0:
            self.layout.label(text=f"New Version Available:")
            self.layout.label(
                text=f"  {bpy.context.preferences.addons['cam'].preferences.new_version_available}")
            self.layout.operator("render.cam_update_now")

    # Display the OpenCamLib version
    def draw_opencamlib_version(self):
        if not self.has_correct_level():
            return
        ocl_version = opencamlib_version()
        if ocl_version is None:
            self.layout.label(text="OpenCAMLib is not Installed")
        else:
            self.layout.label(
                text=f"OpenCAMLib v{ocl_version}")

    # Display warnings related to the current operation
    def draw_op_warnings(self):
        if not self.has_correct_level():
            return
        for line in self.op.info.warnings.rstrip("\n").split("\n"):
            if len(line) > 0:
                self.layout.label(text=line, icon='ERROR')

    # Display the time estimation for the current operation
    def draw_op_time(self):
        if not self.has_correct_level():
            return
        if not int(self.op.info.duration * 60) > 0:
            return

        time_estimate = f"Operation Duration: {int(self.op.info.duration*60)}s "
        if self.op.info.duration > 60:
            time_estimate += f" ({int(self.op.info.duration / 60)}h"
            time_estimate += f" {round(self.op.info.duration % 60)}min)"
        elif self.op.info.duration > 1:
            time_estimate += f" ({round(self.op.info.duration % 60)}min)"

        self.layout.label(text=time_estimate)

    # Display the chipload (does this work ?)
    def draw_op_chipload(self):
        if not self.has_correct_level():
            return
        if not self.op.info.chipload > 0:
            return

        chipload = f"Chipload: {strInUnits(self.op.info.chipload, 4)}/tooth"
        self.layout.label(text=chipload)

    # Display the current operation money cost
    def draw_op_money_cost(self):
        if not self.has_correct_level():
            return
        if not int(self.op.info.duration * 60) > 0:
            return

        row = self.layout.row()
        row.label(text='Hourly Rate')
        row.prop(bpy.context.scene.cam_machine, 'hourly_rate', text='')

        if float(bpy.context.scene.cam_machine.hourly_rate) < 0.01:
            return

        cost_per_second = bpy.context.scene.cam_machine.hourly_rate / 3600
        total_cost = self.op.info.duration * 60 * cost_per_second
        op_cost = f"Operation Cost: ${total_cost:.2f} (${cost_per_second:.2f}/s)"
        self.layout.label(text=op_cost)

    # Display the Info Panel
    def draw(self, context):
        self.context = context
        self.draw_blendercam_version()
        self.draw_opencamlib_version()
        if self.op:
            self.draw_op_warnings()
            self.draw_op_time()
            self.draw_op_money_cost()
