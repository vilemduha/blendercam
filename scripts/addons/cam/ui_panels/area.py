
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils


class CAM_AREA_Properties(bpy.types.PropertyGroup):
    use_layers: bpy.props.BoolProperty(name="Use Layers",
        description="Use layers for roughing", default=True,
        update=cam.utils.update_operation)

    stepdown: bpy.props.FloatProperty(name="",
        description="Layer height", default=0.01, min=0.00001, max=32,
        precision=cam.constants.PRECISION,
        unit="LENGTH", update=cam.utils.update_operation)

    maxz: bpy.props.FloatProperty(name="Operation depth start",
        description='operation starting depth', default=0,
        min=-3, max=10, precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_operation)

    minz: bpy.props.FloatProperty(name="Operation depth end",
        default=-0.01, min=-3, max=3, precision=cam.constants.PRECISION,
        unit="LENGTH", update=cam.utils.update_operation)

    minz_from_material: bpy.props.BoolProperty(name="Depth from material",
        description="Operation ending depth from material",
        default=False, update=cam.utils.update_operation)

    minz_from_ob: bpy.props.BoolProperty(name="Depth from object",
        description="Operation ending depth from object",
        default=True, update=cam.utils.update_operation)

    source_image_scale_z: bpy.props.FloatProperty(
        name="Image source depth scale", default=0.01, min=-1, max=1,
        precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_zbuffer_image)

    source_image_size_x: bpy.props.FloatProperty(
        name="Image source x size", default=0.1, min=-10, max=10,
        precision=cam.constants.PRECISION, unit="LENGTH",
        update=cam.utils.update_zbuffer_image)

    source_image_offset: bpy.props.FloatVectorProperty(name='Image offset',
        default=(0, 0, 0), unit='LENGTH',
        precision=cam.constants.PRECISION, subtype="XYZ",
        update=cam.utils.update_zbuffer_image)

    source_image_crop: bpy.props.BoolProperty(name="Crop source image",
        description="Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image",
        default=False, update=cam.utils.update_zbuffer_image)

    source_image_crop_start_x: bpy.props.FloatProperty(name='crop start x',
        default=0, min=0, max=100, precision=cam.constants.PRECISION,
        subtype='PERCENTAGE', update=cam.utils.update_zbuffer_image)

    source_image_crop_start_y: bpy.props.FloatProperty(name='crop start y',
        default=0, min=0, max=100, precision=cam.constants.PRECISION,
        subtype='PERCENTAGE', update=cam.utils.update_zbuffer_image)

    source_image_crop_end_x: bpy.props.FloatProperty(name='crop end x',
        default=100, min=0, max=100, precision=cam.constants.PRECISION,
        subtype='PERCENTAGE', update=cam.utils.update_zbuffer_image)

    source_image_crop_end_y: bpy.props.FloatProperty(name='crop end y',
        default=100, min=0, max=100, precision=cam.constants.PRECISION,
        subtype='PERCENTAGE', update=cam.utils.update_zbuffer_image)

    ambient_behaviour: bpy.props.EnumProperty(name='Ambient',
        items=(('ALL', 'All', 'a'), ('AROUND', 'Around', 'a')),
        description='handling ambient surfaces', default='ALL',
        update=cam.utils.update_zbuffer_image)

    ambient_radius: bpy.props.FloatProperty(name="Ambient radius",
        description="Radius around the part which will be milled if ambient is set to Around",
        min=0.0, max=100.0, default=0.01, precision=cam.constants.PRECISION,
        unit="LENGTH", update=cam.utils.update_operation)

    ambient_cutter_restrict: bpy.props.BoolProperty(
        name="Cutter stays in ambient limits",
        description="Cutter doesn't get out from ambient limits otherwise goes on the border exactly",
        default=True, update=cam.utils.update_operation)

    use_limit_curve: bpy.props.BoolProperty(name="Use limit curve",
        description="A curve limits the operation area",
        default=False, update=cam.utils.update_operation)

    limit_curve: bpy.props.StringProperty(name='Limit curve',
        description='curve used to limit the area of the operation',
        update=cam.utils.update_operation)


class CAM_AREA_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation area panel"""
    bl_label = "CAM operation area "
    bl_idname = "WORLD_PT_CAM_OPERATION_AREA"
    panel_interface_level = 0

    prop_level = {
        'draw_use_layers': 0,
        'draw_maxz': 1,
        'draw_minz': 1,
        'draw_ambient': 1,
        'draw_limit_curve': 1
    }

    def draw_use_layers(self):
        if not self.has_correct_level(): return
        row = self.layout.row(align=True)
        row.prop(self.op.area, 'use_layers')
        if self.op.area.use_layers:
            row.prop(self.op.area, 'stepdown')

    def draw_maxz(self):
        if not self.has_correct_level(): return
        self.layout.prop(self.op.area, 'maxz')

    def draw_minz(self):
        if not self.has_correct_level(): return
        if self.op.geometry_source in ['OBJECT', 'COLLECTION']:
            if self.op.strategy == 'CURVE':
                self.layout.label(text="cannot use depth from object using CURVES")

            if not self.op.area.minz_from_ob:
                if not self.op.area.minz_from_material:
                    self.layout.prop(self.op.area, 'minz')
                self.layout.prop(self.op.area, 'minz_from_material')
            if not self.op.area.minz_from_material:
                self.layout.prop(self.op.area, 'minz_from_ob')
        else:
            self.layout.prop(self.op.area, 'source_image_scale_z')
            self.layout.prop(self.op.area, 'source_image_size_x')
            if self.op.source_image_name != '':
                i = bpy.data.images[self.op.source_image_name]
                if i is not None:
                    sy = int((self.op.area.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000
                    self.layout.label(text='image size on y axis: ' + strInUnits(sy, 8))
                    self.layout.separator()
            self.layout.prop(self.op.area, 'source_image_offset')
            col = self.layout.column(align=True)
            col.prop(self.op.area, 'source_image_crop', text='Crop source image')
            if self.op.area.source_image_crop:
                col.prop(self.op.area, 'source_image_crop_start_x', text='start x')
                col.prop(self.op.area, 'source_image_crop_start_y', text='start y')
                col.prop(self.op.area, 'source_image_crop_end_x', text='end x')
                col.prop(self.op.area, 'source_image_crop_end_y', text='end y')

    def draw_ambient(self):
        if not self.has_correct_level(): return
        if self.op.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'PARALLEL', 'CROSS']:
            self.layout.prop(self.op.area, 'ambient_behaviour')
            if self.op.area.ambient_behaviour == 'AROUND':
                self.layout.prop(self.op.area, 'ambient_radius')
            self.layout.prop(self.op.area, "ambient_cutter_restrict")

    def draw_limit_curve(self):
        if not self.has_correct_level(): return
        if self.op.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'PARALLEL', 'CROSS']:
            self.layout.prop(self.op.area, 'use_limit_curve')
            if self.op.area.use_limit_curve:
                self.layout.prop_search(self.op.area, "limit_curve", bpy.data, "objects")

    def draw(self, context):
        self.context = context

        self.draw_use_layers()
        self.draw_maxz()
        self.draw_minz()
        self.draw_ambient()
        self.draw_limit_curve()

