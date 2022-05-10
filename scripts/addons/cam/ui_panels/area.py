
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_AREA_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation area panel"""
    bl_label = "CAM operation area "
    bl_idname = "WORLD_PT_CAM_OPERATION_AREA"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        self.scene = bpy.context.scene
        if not self.has_operations():
            self.layout.label(text='Add operation first')
            return

        self.ao = self.active_operation()

        if not self.ao.valid:
            return

        self.draw_z_limits()
        self.draw_xy_limits()

    # Draw layers option: use layers(y/n) and choose the stepdown
    def draw_z_limits(self):
        row = self.layout.row(align=True)
        row.prop(self.ao, 'use_layers')
        if self.ao.use_layers:
            row.prop(self.ao, 'stepdown')

        self.layout.prop(self.ao, 'maxz')

        if self.ao.maxz > self.ao.free_movement_height:
            self.layout.prop(self.ao, 'free_movement_height')
            self.layout.label(text='Depth start > Free movement')
            self.layout.label(text='POSSIBLE COLLISION')

        if self.ao.geometry_source in ['OBJECT', 'COLLECTION']:
            if self.ao.strategy == 'CURVE':
                self.layout.label(text="cannot use depth from object using CURVES")

            if not self.ao.minz_from_ob:
                if not self.ao.minz_from_material:
                    self.layout.prop(self.ao, 'minz') 
                self.layout.prop(self.ao, 'minz_from_material')
            if not self.ao.minz_from_material:
                self.layout.prop(self.ao, 'minz_from_ob')
        else:
            self.layout.prop(self.ao, 'source_image_scale_z')
            self.layout.prop(self.ao, 'source_image_size_x')
            if self.ao.source_image_name != '':
                i = bpy.data.images[self.ao.source_image_name]
                if i is not None:
                    sy = int((self.ao.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000
                    self.layout.label(text='image size on y axis: ' + strInUnits(sy, 8))
                    self.layout.separator()
            self.layout.prop(self.ao, 'source_image_offset')
            col = self.layout.column(align=True)
            col.prop(self.ao, 'source_image_crop', text='Crop source image')
            if self.ao.source_image_crop:
                col.prop(self.ao, 'source_image_crop_start_x', text='start x')
                col.prop(self.ao, 'source_image_crop_start_y', text='start y')
                col.prop(self.ao, 'source_image_crop_end_x', text='end x')
                col.prop(self.ao, 'source_image_crop_end_y', text='end y')

    def draw_xy_limits(self):
        self.layout.prop(self.ao, 'ambient_behaviour')
        if self.ao.ambient_behaviour == 'AROUND':
            self.layout.prop(self.ao, 'ambient_radius')

        self.layout.prop(self.ao, 'use_limit_curve')

        if self.ao.use_limit_curve:
            self.layout.prop_search(self.ao, "limit_curve", bpy.data, "objects")

        self.layout.prop(self.ao, "ambient_cutter_restrict")
