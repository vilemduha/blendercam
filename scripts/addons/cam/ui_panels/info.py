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

    # Display the Info Panel
    def draw(self, context):
        self.draw_opencamlib_version()

        if self.has_operations():
            self.draw_active_op_warnings()
            self.draw_active_op_time()
            self.draw_active_op_money_cost()
        else:
            self.layout.label(text='No CAM operation created')

    # Display the OpenCamLib version
    def draw_opencamlib_version(self):
        opencamlib_version = self.opencamlib_version()
        if opencamlib_version is None:
            self.layout.label(text = "Opencamlib is not installed")
        else:
            self.layout.label(text = f"Opencamlib v{opencamlib_version} installed")

    # Display warnings related to the current operation
    def draw_active_op_warnings(self):
        if self.active_op is None: return

        for line in self.active_op.warnings.rstrip("\n").split("\n"):
            if len(line) > 0 :
                self.layout.label(text=line, icon='ERROR')

    # Display the time estimation for the current operation
    def draw_active_op_time(self):
        if self.active_op is None: return
        if not self.active_op.valid: return
        if not int(self.active_op.duration*60) > 0: return

        time_estimate = f"Operation Time: {int(self.active_op.duration*60)}s " 
        if self.active_op.duration > 60:
            time_estimate += f" ({int(self.active_op.duration / 60)}h {round(self.active_op.duration % 60)}min)"
        elif self.active_op.duration > 1:
            time_estimate += f" ({round(self.active_op.duration % 60)}min)" 

        self.layout.label(text = time_estimate)


    # Display the chipload (does this work ?)
    def draw_active_op_chipload(self):
        if self.active_op is None: return
        if not self.active_op.valid: return
        if not self.active_op.chipload > 0: return

        chipload = f"Chipload: {strInUnits(self.active_op.chipload, 4)}/tooth"
        self.layout.label(text= chipload)

    # Display the current operation money cost
    def draw_active_op_money_cost(self):
        if self.active_op is None: return
        if not self.active_op.valid: return
        if not int(self.active_op.duration*60) > 0: return

        row = self.layout.row()
        row.label(text='Hourly Rate')
        row.prop(bpy.context.scene.cam_machine, 'hourly_rate', text='')

        # TODO: the hourly_rate button properties should be moved here (UI related only)
        # Right now, trying to do so causes an error
        
        if float(bpy.context.scene.cam_machine.hourly_rate) < 0.01: return

        cost_per_second = bpy.context.scene.cam_machine.hourly_rate / 3600
        op_cost = f"Operation cost: ${self.active_op.duration * 60 * cost_per_second:.2f} (${cost_per_second:.2f}/s)"
        self.layout.label(text = op_cost)

