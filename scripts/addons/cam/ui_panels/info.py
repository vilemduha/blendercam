import sys
import bpy

from cam.simple import strInUnits
from cam.ui_panels.buttons_panel import CAMButtonsPanel

# Info panel
# This panel gives general information about the current operation

class CAM_INFO_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM info panel"""
    bl_label = "CAM info & warnings"
    bl_idname = "WORLD_PT_CAM_INFO"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        self.draw_opencamlib_version()

        if self.has_operations():
            self.draw_active_op_warnings()
            self.draw_active_op_data()
            self.draw_active_op_money_cost()
        else:
            self.layout.label(text='No CAM operation created')

    def draw_opencamlib_version(self):
        opencamlib_version = self.opencamlib_version()
        if opencamlib_version is None:
            self.layout.label(text = "Opencamlib is not installed")
        else:
            self.layout.label(text = f"Opencamlib v{opencamlib_version} installed")

    def draw_active_op_warnings(self):
        active_op = self.active_operation()
        if active_op is None: return

        for line in active_op.warnings.rstrip("\n").split("\n"):
            if len(line) > 0 :
                self.layout.label(text=line, icon='ERROR')

    def draw_active_op_data(self):
        active_op = self.active_operation()
        if active_op is None: return
        if not active_op.valid: return
        if not int(active_op.duration*60) > 0: return

        active_op_time_text = "Operation Time: %d s " % int(active_op.duration*60)
        if active_op.duration > 60:
            active_op_time_text += " (%dh %dmin)" % (int(active_op.duration / 60), round(active_op.duration % 60))
        elif active_op.duration > 1:
            active_op_time_text += " (%dmin)" % round(active_op.duration % 60)

        self.layout.label(text = active_op_time_text)

        self.layout.label(text="Chipload: %s/tooth" % strInUnits(active_op.chipload, 4))

    def draw_active_op_money_cost(self):
        active_op = self.active_operation()
        if active_op is None: return
        if not active_op.valid: return
        if not int(active_op.duration*60) > 0: return

        # TODO: the hourly_rate button properties should be moved here (UI related only)
        # Right now, trying to do so causes an error
        self.layout.prop(self.scene.cam_machine, 'hourly_rate')

        if float(self.scene.cam_machine.hourly_rate) < 0.01: return

        cost_per_second = self.scene.cam_machine.hourly_rate / 3600
        self.layout.label(text = "Operation cost: $%.2f (%.2f $/s)"
            % (active_op.duration * 60 * cost_per_second, cost_per_second)
        )
