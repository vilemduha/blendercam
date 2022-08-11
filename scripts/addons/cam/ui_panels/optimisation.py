import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_OPTIMISATION_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM optimisation panel"""
    bl_label = "CAM optimisation"
    bl_idname = "WORLD_PT_CAM_OPTIMISATION"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'optimize')
                if ao.optimize:
                    layout.prop(ao, 'optimize_threshold')
                if ao.geometry_source == 'OBJECT' or ao.geometry_source == 'COLLECTION':
                    exclude_exact = ao.strategy in ['MEDIAL_AXIS', 'POCKET', 'CUTOUT', 'DRILL', 'PENCIL',
                                                    'CURVE']
                    if not exclude_exact:
                        if not ao.use_exact:
                            layout.prop(ao, 'use_exact')
                            layout.label(text="Exact mode must be set for opencamlib to work ")

                        opencamlib_version = self.opencamlib_version()
                        if opencamlib_version is None:
                            layout.label(text="Opencamlib is NOT available ")
                            layout.prop(ao, 'exact_subdivide_edges')
                        else:
                            layout.label(text=f"Opencamlib v{opencamlib_version} installed")
                            layout.prop(ao, 'use_opencamlib')

                    if exclude_exact or not ao.use_exact:
                        layout.prop(ao, 'pixsize')
                        layout.prop(ao, 'imgres_limit')

                        sx = ao.max.x - ao.min.x
                        sy = ao.max.y - ao.min.y
                        resx = int(sx / ao.pixsize)
                        resy = int(sy / ao.pixsize)
                        l = 'resolution: ' + str(resx) + ' x ' + str(resy)
                        layout.label(text=l)

                layout.prop(ao, 'simulation_detail')
                layout.prop(ao, 'circle_detail')
