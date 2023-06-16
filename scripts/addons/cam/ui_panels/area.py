
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_AREA_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation area panel"""
    bl_label = "CAM operation area "
    bl_idname = "WORLD_PT_CAM_OPERATION_AREA"
    panel_interface_level = 0

    def draw(self, context):
        self.context = context

        self.draw_z_limits()

        if self.op.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'PARALLEL', 'CROSS']:
            self.draw_xy_limits()

    # Draw layers option: use layers(y/n) and choose the stepdown
    def draw_z_limits(self):
        row = self.layout.row(align=True)
        row.prop(self.op, 'use_layers')
        if self.op.use_layers:
            row.prop(self.op, 'stepdown')

        self.layout.prop(self.op, 'maxz')

        if self.op.maxz > self.op.movement.free_height:
            self.layout.prop(self.op.movement, 'free_height')
            self.layout.label(text='Depth start > Free movement')
            self.layout.label(text='POSSIBLE COLLISION')

        if self.op.geometry_source in ['OBJECT', 'COLLECTION']:
            if self.op.strategy == 'CURVE':
                self.layout.label(text="cannot use depth from object using CURVES")

            if not self.op.minz_from_ob:
                if not self.op.minz_from_material:
                    self.layout.prop(self.op, 'minz')
                self.layout.prop(self.op, 'minz_from_material')
            if not self.op.minz_from_material:
                self.layout.prop(self.op, 'minz_from_ob')
        else:
            self.layout.prop(self.op, 'source_image_scale_z')
            self.layout.prop(self.op, 'source_image_size_x')
            if self.op.source_image_name != '':
                i = bpy.data.images[self.op.source_image_name]
                if i is not None:
                    sy = int((self.op.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000
                    self.layout.label(text='image size on y axis: ' + strInUnits(sy, 8))
                    self.layout.separator()
            self.layout.prop(self.op, 'source_image_offset')
            col = self.layout.column(align=True)
            col.prop(self.op, 'source_image_crop', text='Crop source image')
            if self.op.source_image_crop:
                col.prop(self.op, 'source_image_crop_start_x', text='start x')
                col.prop(self.op, 'source_image_crop_start_y', text='start y')
                col.prop(self.op, 'source_image_crop_end_x', text='end x')
                col.prop(self.op, 'source_image_crop_end_y', text='end y')

    def draw_xy_limits(self):
        self.layout.prop(self.op, 'ambient_behaviour')
        if self.op.ambient_behaviour == 'AROUND':
            self.layout.prop(self.op, 'ambient_radius')

        self.layout.prop(self.op, 'use_limit_curve')

        if self.op.use_limit_curve:
            self.layout.prop_search(self.op, "limit_curve", bpy.data, "objects")

        self.layout.prop(self.op, "ambient_cutter_restrict")
