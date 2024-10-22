"""CNC CAM 'material.py'

'CAM Material' properties and panel in Properties > Render
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
)
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)

from .buttons_panel import CAMButtonsPanel
from ..utils import (
    positionObject,
    update_material,
)
from ..constants import PRECISION


class CAM_MATERIAL_Properties(PropertyGroup):

    estimate_from_model: BoolProperty(
        name="Estimate Cut Area from Model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=update_material,
    )

    radius_around_model: FloatProperty(
        name='Radius Around Model',
        description="Increase cut area around the model on X and "
        "Y by this amount",
        default=0.0,
        unit='LENGTH',
        precision=PRECISION,
        update=update_material,
    )

    center_x: BoolProperty(
        name="Center on X Axis",
        description="Position model centered on X",
        default=False,
        update=update_material,
    )

    center_y: BoolProperty(
        name="Center on Y Axis",
        description="Position model centered on Y",
        default=False,
        update=update_material,
    )

    z_position: EnumProperty(
        name="Z Placement",
        items=(
            ('ABOVE', 'Above', 'Place object vertically above the XY plane'),
            ('BELOW', 'Below', 'Place object vertically below the XY plane'),
            ('CENTERED', 'Centered',
             'Place object vertically centered on the XY plane')
        ),
        description="Position below Zero",
        default='BELOW',
        update=update_material,
    )

    # material_origin
    origin: FloatVectorProperty(
        name='Material Origin',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=PRECISION,
        subtype="XYZ",
        update=update_material,
    )

    # material_size
    size: FloatVectorProperty(
        name='Material Size',
        default=(0.200, 0.200, 0.100),
        min=0,
        unit='LENGTH',
        precision=PRECISION,
        subtype="XYZ",
        update=update_material,
    )


# Position object for CAM operation. Tests object bounds and places them so the object
# is aligned to be positive from x and y and negative from z."""
class CAM_MATERIAL_PositionObject(Operator):

    bl_idname = "object.material_cam_position"
    bl_label = "Position Object for CAM Operation"
    bl_options = {'REGISTER', 'UNDO'}
    interface_level = 0

    def execute(self, context):
        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            positionObject(operation)
        else:
            print('No Object Assigned')
        return {'FINISHED'}

    def draw(self, context):
        if not self.interface_level <= int(self.context.scene.interface.level):
            return
        self.layout.prop_search(
            self, "operation", bpy.context.scene, "cam_operations")


class CAM_MATERIAL_Panel(CAMButtonsPanel, Panel):
    bl_label = "CAM Material Size and Position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"
    panel_interface_level = 0

    prop_level = {
        'draw_estimate_from_image': 0,
        'draw_estimate_from_object': 1,
        'draw_axis_alignment': 0
    }

    def draw_estimate_from_image(self):
        if not self.has_correct_level():
            return
        if self.op.geometry_source not in ['OBJECT', 'COLLECTION']:
            self.layout.label(text='Estimated from Image')

    def draw_estimate_from_object(self):
        if not self.has_correct_level():
            return
        if self.op.geometry_source in ['OBJECT', 'COLLECTION']:
            self.layout.prop(self.op.material, 'estimate_from_model')
            if self.op.material.estimate_from_model:
                row_radius = self.layout.row()
                row_radius.label(text="Additional Radius")
                row_radius.prop(self.op.material,
                                'radius_around_model', text='')
            else:
                self.layout.prop(self.op.material, 'origin')
                self.layout.prop(self.op.material, 'size')

    # Display Axis alignment section
    def draw_axis_alignment(self):
        if not self.has_correct_level():
            return
        if self.op.geometry_source in ['OBJECT', 'COLLECTION']:
            row_axis = self.layout.row()
            row_axis.prop(self.op.material, 'center_x')
            row_axis.prop(self.op.material, 'center_y')
            self.layout.prop(self.op.material, 'z_position')
            self.layout.operator(
                "object.material_cam_position", text="Position Object")

    def draw(self, context):
        self.context = context

        # FIXME: This function displays the progression of a job with a progress bar
        # Commenting because it makes no sense here
        # Consider removing it entirely
        # self.layout.template_running_jobs()

        self.draw_estimate_from_image()
        self.draw_estimate_from_object()
        self.draw_axis_alignment()
