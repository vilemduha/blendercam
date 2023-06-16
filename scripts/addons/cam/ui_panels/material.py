
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants


class CAM_MATERIAL_Properties(bpy.types.PropertyGroup):

    estimate_from_model: bpy.props.BoolProperty(
        name="Estimate cut area from model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=cam.utils.update_material
    )

    radius_around_model: bpy.props.FloatProperty(
        name='Radius around model',
        description="Increase cut area around the model on X and Y by this amount",
        default=0.0, unit='LENGTH', precision=cam.constants.PRECISION,
        update=cam.utils.update_material
    )

    center_x: bpy.props.BoolProperty(
        name="Center on X axis",
        description="Position model centered on X",
        default=False, update=cam.utils.update_material
    )

    center_y: bpy.props.BoolProperty(
        name="Center on Y axis",
        description="Position model centered on Y",
        default=False, update=cam.utils.update_material
    )

    z_position: bpy.props.EnumProperty(
        name="Z placement", items=(
            ('ABOVE', 'Above', 'Place object vertically above the XY plane'),
            ('BELOW', 'Below', 'Place object vertically below the XY plane'),
            ('CENTERED', 'Centered', 'Place object vertically centered on the XY plane')),
        description="Position below Zero", default='BELOW',
        update=cam.utils.update_material
    )

    # material_origin
    origin: bpy.props.FloatVectorProperty(
        name='Material origin', default=(0, 0, 0), unit='LENGTH',
        precision=cam.constants.PRECISION, subtype="XYZ",
        update=cam.utils.update_material
    )

    # material_size
    size: bpy.props.FloatVectorProperty(
        name='Material size', default=(0.200, 0.200, 0.100), min=0, unit='LENGTH',
        precision=cam.constants.PRECISION, subtype="XYZ",
        update=cam.utils.update_material
    )


# Position object for CAM operation. Tests object bounds and places them so the object
# is aligned to be positive from x and y and negative from z."""
class CAM_MATERIAL_PositionObject(bpy.types.Operator):

    bl_idname = "object.material_cam_position"
    bl_label = "position object for CAM operation"
    bl_options = {'REGISTER', 'UNDO'}
    interface_level = 0

    def execute(self, context):
        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            cam.utils.positionObject(operation)
        else:
            print('no object assigned')
        return {'FINISHED'}

    def draw(self, context):
        if not self.interface_level <= int(self.context.scene.interface.level): return
        self.layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

class CAM_MATERIAL_Panel(CAMButtonsPanel, bpy.types.Panel):
    bl_label = "CAM Material size and position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"
    panel_interface_level = 0

    prop_level = {
        'estimate_from_model': 0,
        'radius_around_model': 1,
        'position_object': 0
    }

    def draw_estimate_from_image(self):
        if self.op.geometry_source not in ['OBJECT', 'COLLECTION']:
            self.layout.label(text='Estimated from image')

    def draw_estimate_from_object(self):
        if self.op.geometry_source in ['OBJECT', 'COLLECTION']:
            if not self.has_correct_level('estimate_from_model'): return
            self.layout.prop(self.op.material, 'estimate_from_model')
            if self.op.material.estimate_from_model:
                row_radius = self.layout.row()
                if self.has_correct_level('radius_around_model'):
                    row_radius.label(text="Additional radius")
                    row_radius.prop(self.op.material, 'radius_around_model', text='')
            else:
                self.layout.prop(self.op.material, 'origin')
                self.layout.prop(self.op.material, 'size')

    # Display Axis alignment section
    def draw_axis_alignment(self):
        if not self.has_correct_level('position_object'): return
        if self.op.geometry_source in ['OBJECT', 'COLLECTION']:
            row_axis = self.layout.row()
            row_axis.prop(self.op.material, 'center_x')
            row_axis.prop(self.op.material, 'center_y')
            self.layout.prop(self.op.material, 'z_position')
            self.layout.operator("object.material_cam_position", text="Position object")

    def draw(self, context):
        self.context = context

        if self.op is None:
            return

        # FIXME: This function displays the progression of a job with a progress bar
        # Commenting because it makes no sense here
        # Consider removing it entirely
        # self.layout.template_running_jobs()

        self.draw_estimate_from_image()
        self.draw_estimate_from_object()
        self.draw_axis_alignment()
