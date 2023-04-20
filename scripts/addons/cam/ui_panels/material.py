
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_MATERIAL_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM material panel"""
    bl_label = "CAM Material size and position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):

        if self.active_op is None: return

        # FIXME: This function displays the progression of a job with a progress bar
        # Commenting because it makes no sense here
        # Consider removing it entirely
        # self.layout.template_running_jobs()

        if not self.active_op.geometry_source in ['OBJECT', 'COLLECTION']:
            self.layout.label(text='Estimated from image')
            return

        self.layout.prop(self.active_op, 'material_from_model')

        if self.active_op.material_from_model:
            self.draw_estimate_material_from_model()
        else:
            self.draw_custom_material_size_and_origin()

        self.draw_axis_alignment()
            
    # Display section selecting the radius around the model
    def draw_estimate_material_from_model(self):
        row_radius = self.layout.row()
        row_radius.label(text="Radius around model")
        row_radius.prop(self.active_op, 'material_radius_around_model')
    
    # Display section showing custom material size
    def draw_custom_material_size_and_origin(self):
        self.layout.prop(self.active_op, 'material_origin')
        self.layout.prop(self.active_op, 'material_size')

    # Display Axis alignment section
    def draw_axis_alignment(self):
        row_axis = self.layout.row()
        row_axis.prop(self.active_op, 'material_center_x')
        row_axis.prop(self.active_op, 'material_center_y')
        self.layout.prop(self.active_op, 'material_Z')
        self.layout.operator("object.cam_position", text="Position object")
