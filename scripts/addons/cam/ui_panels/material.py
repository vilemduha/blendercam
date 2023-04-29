
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel
import cam.utils
import cam.constants


class CAM_MATERIAL_Properties(bpy.types.PropertyGroup):

    def update_material(self, context):
        cam.utils.addMaterialAreaObject()

    estimate_from_model: bpy.props.BoolProperty(
        name="Estimate cut area from model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=update_material
    )

    radius_around_model: bpy.props.FloatProperty(
        name='Radius around model',
        description="Increase cut area around the model on X and Y by this amount",
        default=0.0, unit='LENGTH', precision=cam.constants.PRECISION,
        update=update_material
    )

    center_x: bpy.props.BoolProperty(
        name="Center on X axis",
        description="Position model centered on X",
        default=False, update=update_material
    )

    center_y: bpy.props.BoolProperty(
        name="Center on Y axis",
        description="Position model centered on Y",
        default=False, update=update_material
    )

    z_position: bpy.props.EnumProperty(
        name="Z placement", items=(
            ('ABOVE', 'Above', 'Place object vertically above the XY plane'),
            ('BELOW', 'Below', 'Place object vertically below the XY plane'),
            ('CENTERED', 'Centered', 'Place object vertically centered on the XY plane')),
        description="Position below Zero", default='BELOW',
        update=update_material
    )

    # material_origin
    origin: bpy.props.FloatVectorProperty(
        name='Material origin', default=(0, 0, 0), unit='LENGTH',
        precision=cam.constants.PRECISION, subtype="XYZ",
        update=update_material
    )

    # material_size
    size: bpy.props.FloatVectorProperty(
        name='Material size', default=(0.200, 0.200, 0.100), min=0, unit='LENGTH',
        precision=cam.constants.PRECISION, subtype="XYZ",
        update=update_material
    )


# Position object for CAM operation. Tests object bounds and places them so the object
# is aligned to be positive from x and y and negative from z."""
class CAM_MATERIAL_PositionObject(bpy.types.Operator):

    bl_idname = "object.material_cam_position"
    bl_label = "position object for CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            cam.utils.positionObject(operation)
        else:
            print('no object assigned')
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CAM_MATERIAL_Panel(CAMButtonsPanel, bpy.types.Panel):
    bl_label = "CAM Material size and position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):

        if self.active_op is None:
            return

        # FIXME: This function displays the progression of a job with a progress bar
        # Commenting because it makes no sense here
        # Consider removing it entirely
        # self.layout.template_running_jobs()

        if self.active_op.geometry_source not in ['OBJECT', 'COLLECTION']:
            self.layout.label(text='Estimated from image')
            return

        self.layout.prop(self.active_op.material, 'estimate_from_model')

        if self.active_op.material.estimate_from_model:
            self.draw_estimate_material_from_model()
        else:
            self.draw_custom_material_size_and_origin()

        self.draw_axis_alignment()

    # Display section selecting the radius around the model
    def draw_estimate_material_from_model(self):
        row_radius = self.layout.row()
        row_radius.label(text="Additional radius")
        row_radius.prop(self.active_op.material, 'radius_around_model', text='')

    # Display section showing custom material size
    def draw_custom_material_size_and_origin(self):
        self.layout.prop(self.active_op.material, 'origin')
        self.layout.prop(self.active_op.material, 'size')

    # Display Axis alignment section
    def draw_axis_alignment(self):
        row_axis = self.layout.row()
        row_axis.prop(self.active_op.material, 'center_x')
        row_axis.prop(self.active_op.material, 'center_y')
        self.layout.prop(self.active_op.material, 'z_position')
        self.layout.operator("object.material_cam_position", text="Position object")
