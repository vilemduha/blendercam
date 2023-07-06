import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants


class CAM_OPTIMISATION_Properties(bpy.types.PropertyGroup):

    optimize: bpy.props.BoolProperty(
        name="Reduce path points", description="Reduce path points", default=True,
        update=cam.utils.update_operation)

    optimize_threshold: bpy.props.FloatProperty(
        name="Reduction threshold in μm", default=.2, min=0.000000001,
        max=1000, precision=20, update=cam.utils.update_operation)

    use_exact: bpy.props.BoolProperty(
        name="Use exact mode",
        description="Exact mode allows greater precision, but is slower with complex meshes",
        default=True, update=cam.utils.update_exact_mode)

    imgres_limit: bpy.props.IntProperty(
        name="Maximum resolution in megapixels", default=16, min=1, max=512,
        description="Limits total memory usage and prevents crashes. Increase it if you know what are doing",
        update=cam.utils.update_zbuffer_image)

    pixsize: bpy.props.FloatProperty(
        name="sampling raster detail", default=0.0001, min=0.00001, max=0.1,
        precision=cam.constants.PRECISION, unit="LENGTH", update=cam.utils.update_zbuffer_image)

    use_opencamlib: bpy.props.BoolProperty(
        name="Use OpenCAMLib",
        description="Use OpenCAMLib to sample paths or get waterline shape",
        default=False, update=cam.utils.update_opencamlib)

    exact_subdivide_edges: bpy.props.BoolProperty(
        name="Auto subdivide long edges",
        description="This can avoid some collision issues when importing CAD models",
        default=False, update=cam.utils.update_exact_mode)

    circle_detail: bpy.props.IntProperty(
        name="Detail of circles used for curve offsets", default=64, min=12, max=512,
        update=cam.utils.update_operation)

    simulation_detail: bpy.props.FloatProperty(
        name="Simulation sampling raster detail", default=0.0002, min=0.00001,
        max=0.01, precision=cam.constants.PRECISION, unit="LENGTH", update=cam.utils.update_operation)


class CAM_OPTIMISATION_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM optimisation panel"""
    bl_label = "CAM optimisation"
    bl_idname = "WORLD_PT_CAM_OPTIMISATION"
    panel_interface_level = 2

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        if self.op is None:
            return
        if not self.op.valid:
            return

        self.draw_optimize()
        self.layout.separator()
        self.draw_exact_mode()
        self.draw_use_opencamlib()
        self.layout.separator()
        self.draw_simulation_detail()

    def draw_optimize(self):
        if self.op is None:
            return
        if not self.op.valid:
            return

        self.layout.prop(self.op.optimisation, 'optimize')
        if self.op.optimisation.optimize:
            self.layout.prop(self.op.optimisation, 'optimize_threshold')

    def draw_exact_mode(self):
        if self.op is None:
            return
        if not self.op.valid:
            return

        if not self.op.geometry_source == 'OBJECT' or self.op.geometry_source == 'COLLECTION':
            return

        self.exact_possible = self.op.strategy not in [
            'MEDIAL_AXIS', 'POCKET', 'CUTOUT', 'DRILL', 'PENCIL', 'CURVE']

        if self.exact_possible:
            self.layout.prop(self.op.optimisation, 'use_exact')

        if not self.exact_possible or not self.op.optimisation.use_exact:
            self.layout.prop(self.op.optimisation, 'pixsize')
            self.layout.prop(self.op.optimisation, 'imgres_limit')

            sx = self.op.max.x - self.op.min.x
            sy = self.op.max.y - self.op.min.y
            resx = int(sx / self.op.optimisation.pixsize)
            resy = int(sy / self.op.optimisation.pixsize)

            if resx > 0 and resy > 0:
                resolution = 'Resolution: ' + str(resx) + ' x ' + str(resy)
                self.layout.label(text=resolution)

    def draw_use_opencamlib(self):
        if self.op is None:
            return
        if not self.op.valid:
            return
        if not (self.exact_possible and self.op.optimisation.use_exact):
            return

        opencamlib_version = cam.utils.opencamlib_version()

        if opencamlib_version is None:
            self.layout.label(text="Opencamlib is not available ")
            self.layout.prop(self.op.optimisation, 'exact_subdivide_edges')
        else:
            self.layout.prop(self.op.optimisation, 'use_opencamlib')

    def draw_simulation_detail(self):
        if self.op is None:
            return
        if not self.op.valid:
            return

        self.layout.prop(self.op.optimisation, 'simulation_detail')
        self.layout.prop(self.op.optimisation, 'circle_detail')
