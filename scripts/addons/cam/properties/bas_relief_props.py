"""bas_relief_props.py
"""

from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from ..constants import PRECISION


class BasReliefSettings(PropertyGroup):
    use_image_source: BoolProperty(
        name="Use Image Source",
        description="",
        default=False,
    )
    source_image_name: StringProperty(
        name="Image Source",
        description="image source",
    )
    view_layer_name: StringProperty(
        name="View Layer Source",
        description="Make a bas-relief from whatever is on this view layer",
    )
    bit_diameter: FloatProperty(
        name="Diameter of Ball End in mm",
        description="Diameter of bit which will be used for carving",
        min=0.01,
        max=50.0,
        default=3.175,
        precision=PRECISION,
    )
    pass_per_radius: IntProperty(
        name="Passes per Radius",
        description="Amount of passes per radius\n(more passes, " "more mesh precision)",
        default=2,
        min=1,
        max=10,
    )
    widthmm: IntProperty(
        name="Desired Width in mm",
        default=200,
        min=5,
        max=4000,
    )
    heightmm: IntProperty(
        name="Desired Height in mm",
        default=150,
        min=5,
        max=4000,
    )
    thicknessmm: IntProperty(
        name="Thickness in mm",
        default=15,
        min=5,
        max=100,
    )

    justifyx: EnumProperty(
        name="X",
        items=[("1", "Left", "", 0), ("-0.5", "Centered", "", 1), ("-1", "Right", "", 2)],
        default="-1",
    )
    justifyy: EnumProperty(
        name="Y",
        items=[
            ("1", "Bottom", "", 0),
            ("-0.5", "Centered", "", 2),
            ("-1", "Top", "", 1),
        ],
        default="-1",
    )
    justifyz: EnumProperty(
        name="Z",
        items=[
            ("-1", "Below 0", "", 0),
            ("-0.5", "Centered", "", 2),
            ("1", "Above 0", "", 1),
        ],
        default="-1",
    )

    depth_exponent: FloatProperty(
        name="Depth Exponent",
        description="Initial depth map is taken to this power. Higher = " "sharper relief",
        min=0.5,
        max=10.0,
        default=1.0,
        precision=PRECISION,
    )

    silhouette_threshold: FloatProperty(
        name="Silhouette Threshold",
        description="Silhouette threshold",
        min=0.000001,
        max=1.0,
        default=0.003,
        precision=PRECISION,
    )
    recover_silhouettes: BoolProperty(
        name="Recover Silhouettes",
        description="",
        default=True,
    )
    silhouette_scale: FloatProperty(
        name="Silhouette Scale",
        description="Silhouette scale",
        min=0.000001,
        max=5.0,
        default=0.3,
        precision=PRECISION,
    )
    silhouette_exponent: IntProperty(
        name="Silhouette Square Exponent",
        description="If lower, true depth distances between objects will be "
        "more visibe in the relief",
        default=3,
        min=0,
        max=5,
    )
    attenuation: FloatProperty(
        name="Gradient Attenuation",
        description="Gradient attenuation",
        min=0.000001,
        max=100.0,
        default=1.0,
        precision=PRECISION,
    )
    min_gridsize: IntProperty(
        name="Minimum Grid Size",
        default=16,
        min=2,
        max=512,
    )
    smooth_iterations: IntProperty(
        name="Smooth Iterations",
        default=1,
        min=1,
        max=64,
    )
    vcycle_iterations: IntProperty(
        name="V-Cycle Iterations",
        description="Set higher for planar constraint",
        default=2,
        min=1,
        max=128,
    )
    linbcg_iterations: IntProperty(
        name="LINBCG Iterations",
        description="Set lower for flatter relief, and when using " "planar constraint",
        default=5,
        min=1,
        max=64,
    )
    use_planar: BoolProperty(
        name="Use Planar Constraint",
        description="",
        default=False,
    )
    gradient_scaling_mask_use: BoolProperty(
        name="Scale Gradients with Mask",
        description="",
        default=False,
    )
    decimate_ratio: FloatProperty(
        name="Decimate Ratio",
        description="Simplify the mesh using the Decimate modifier. "
        "The lower the value the more simplyfied",
        min=0.01,
        max=1.0,
        default=0.1,
        precision=PRECISION,
    )

    gradient_scaling_mask_name: StringProperty(
        name="Scaling Mask Name",
        description="Mask name",
    )
    scale_down_before_use: BoolProperty(
        name="Scale Down Image Before Processing",
        description="",
        default=False,
    )
    scale_down_before: FloatProperty(
        name="Image Scale",
        description="Image scale",
        min=0.025,
        max=1.0,
        default=0.5,
        precision=PRECISION,
    )
    detail_enhancement_use: BoolProperty(
        name="Enhance Details",
        description="Enhance details by frequency analysis",
        default=False,
    )
    # detail_enhancement_freq=FloatProperty(name="frequency limit", description="Image scale", min=0.025, max=1.0, default=.5, precision=PRECISION)
    detail_enhancement_amount: FloatProperty(
        name="Amount",
        description="Image scale",
        min=0.025,
        max=1.0,
        default=0.5,
        precision=PRECISION,
    )

    advanced: BoolProperty(
        name="Advanced Options",
        description="Show advanced options",
        default=True,
    )
