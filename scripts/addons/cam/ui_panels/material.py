
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_MATERIAL_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM material panel"""
    bl_label = "CAM Material size and position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao:
                layout.template_running_jobs()
                if ao.geometry_source in ['OBJECT', 'COLLECTION']:
                    layout.prop(ao, 'material_from_model')

                    if ao.material_from_model:
                        layout.prop(ao, 'material_radius_around_model')
                    else:
                        layout.prop(ao, 'material_origin')
                        layout.prop(ao, 'material_size')

                    layout.prop(ao, 'material_center_x')
                    layout.prop(ao, 'material_center_y')
                    layout.prop(ao, 'material_Z')
                    layout.operator("object.cam_position", text="Position object")
                else:
                    layout.label(text='Estimated from image')
