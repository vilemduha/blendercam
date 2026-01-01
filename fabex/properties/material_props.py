"""Fabex 'material_props.py'

'CAM Material Properties'
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup
from ..utilities.material_utils import update_material
from ..constants import PRECISION


class CAM_MATERIAL_Properties(PropertyGroup):
    wire_color: FloatVectorProperty(
        name="Wire Color",
        description="Color of the CAM_Material box in the viewport",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        subtype="COLOR",
    )

    material_source: EnumProperty(
        name="Material Source",
        description="Data source for Stock Material Object - Estimated from the Model, Generated from Dimensions or Picked from an Object in the Scene",
        default="MODEL",
        items=(
            (
                "MODEL",
                "Operation Model",
                "Estimate the dimensions of the stock material using the Model",
            ),
            (
                "OBJECT",
                "Alternate Object",
                "Use Object found in Scene",
            ),
            (
                "DIMENSIONS",
                "Enter Dimensions",
                "Manually enter the dimensions and origin point of the stock material",
            ),
        ),
    )

    estimate_from_model: BoolProperty(
        name="Estimate Cut Area from Model",
        description="Estimate cut area based on model geometry",
        default=True,
        update=update_material,
    )

    alt_object: PointerProperty(
        name="Alternate Object",
        type=bpy.types.Object,
    )

    radius_around_model: FloatProperty(
        name="Radius Around Model",
        description="Increase cut area around the model on X and Y by this amount",
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
            (
                "ABOVE",
                "Above",
                "Place object vertically above the XY plane",
            ),
            (
                "BELOW",
                "Below",
                "Place object vertically below the XY plane",
            ),
            (
                "CENTERED",
                "Centered",
                "Place object vertically centered on the XY plane",
            ),
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
