import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils

class CAM_OPTIMISATION_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM optimisation panel"""
    bl_label = "CAM optimisation"
    bl_idname = "WORLD_PT_CAM_OPTIMISATION"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        if self.active_op is None: return
        if not self.active_op.valid: return

        ao = self.active_op

        self.layout.prop(ao, 'optimize')
        if ao.optimize:
            self.layout.prop(ao, 'optimize_threshold')
        if ao.geometry_source == 'OBJECT' or ao.geometry_source == 'COLLECTION':
            exclude_exact = ao.strategy in ['MEDIAL_AXIS', 'POCKET', 'CUTOUT', 'DRILL', 'PENCIL',
                                            'CURVE']
            if not exclude_exact:
                self.layout.prop(ao, 'use_exact')
                self.layout.label(text="Exact mode must be set for opencamlib to work ")

                opencamlib_version = cam.utils.opencamlib_version()
                if opencamlib_version is None:
                    self.layout.label(text="Opencamlib is NOT available ")
                    self.layout.prop(ao, 'exact_subdivide_edges')
                else:                            
                    self.layout.prop(ao, 'use_opencamlib')

            if exclude_exact or not ao.use_exact:
                self.layout.prop(ao, 'pixsize')
                self.layout.prop(ao, 'imgres_limit')

                sx = ao.max.x - ao.min.x
                sy = ao.max.y - ao.min.y
                resx = int(sx / ao.pixsize)
                resy = int(sy / ao.pixsize)
                l = 'resolution: ' + str(resx) + ' x ' + str(resy)
                self.layout.label(text=l)

        self.layout.prop(ao, 'simulation_detail')
        self.layout.prop(ao, 'circle_detail')
