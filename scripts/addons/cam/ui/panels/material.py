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
from ...utils import (
    positionObject,
    update_material,
)
from ...constants import PRECISION


class CAM_MATERIAL_Properties(PropertyGroup):

    estimate_from_model: BoolProperty(
        name="Estimate Cut Area from Model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=update_material,
    )

    radius_around_model: FloatProperty(
        name="Radius Around Model",
        description="Increase cut area around the model on X and " "Y by this amount",
        default=0.0,
        unit="LENGTH",
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
            ("ABOVE", "Above", "Place object vertically above the XY plane"),
            ("BELOW", "Below", "Place object vertically below the XY plane"),
            ("CENTERED", "Centered", "Place object vertically centered on the XY plane"),
        ),
        description="Position below Zero",
        default="BELOW",
        update=update_material,
    )

    origin: FloatVectorProperty(
        name="Material Origin",
        default=(0, 0, 0),
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_material,
    )

    size: FloatVectorProperty(
        name="Material Size",
        default=(0.200, 0.200, 0.100),
        min=0,
        unit="LENGTH",
        precision=PRECISION,
        subtype="XYZ",
        update=update_material,
    )


# Position object for CAM operation. Tests object bounds and places them so the object
# is aligned to be positive from x and y and negative from z."""
class CAM_MATERIAL_PositionObject(Operator):

    bl_idname = "object.material_cam_position"
    bl_label = "Position Object for CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            positionObject(operation)
        else:
            print("No Object Assigned")
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", context.scene, "cam_operations")


class CAM_MATERIAL_Panel(CAMButtonsPanel, Panel):
    bl_label = "CAM Material Size and Position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"
    panel_interface_level = 0

    def draw(self, context):
        layout = self.layout
        # Estimate from Image
        if self.op.geometry_source not in ["OBJECT", "COLLECTION"]:
            layout.label(text="Estimated from Image")

        # Estimate from Object
        if self.level >= 1:
            if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
                layout.prop(self.op.material, "estimate_from_model")
                if self.op.material.estimate_from_model:
                    row_radius = layout.row()
                    row_radius.label(text="Additional Radius")
                    row_radius.prop(self.op.material, "radius_around_model", text="")
                else:
                    layout.prop(self.op.material, "origin")
                    layout.prop(self.op.material, "size")

        # Axis Alignment
        if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
            row_axis = layout.row()
            row_axis.prop(self.op.material, "center_x")
            row_axis.prop(self.op.material, "center_y")
            layout.prop(self.op.material, "z_position")
            layout.operator("object.material_cam_position", text="Position Object")
