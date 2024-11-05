"""Fabex 'basrelief.py'

'Bas Relief' properties and panel in Properties > Render
"""

import bpy
from bpy.types import PropertyGroup, Panel
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from ...constants import PRECISION


class BasReliefsettings(PropertyGroup):
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


class BASRELIEF_Panel(Panel):
    """Bas Relief Panel"""

    bl_label = "╠ Bas Relief ╣"
    bl_idname = "WORLD_PT_BASRELIEF"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {"FABEX_RENDER"}

    @classmethod
    def poll(cls, context):
        """Check if the current render engine is compatible.

        This class method checks whether the render engine specified in the
        provided context is included in the list of compatible engines. It
        accesses the render settings from the context and verifies if the engine
        is part of the predefined compatible engines.

        Args:
            context (Context): The context containing the scene and render settings.

        Returns:
            bool: True if the render engine is compatible, False otherwise.
        """

        rd = context.scene.render
        return rd.engine in cls.COMPAT_ENGINES

    def draw(self, context):
        """Draw the user interface for the bas relief settings.

        This method constructs the layout for the bas relief settings in the
        Blender user interface. It includes various properties and options that
        allow users to configure the bas relief calculations, such as selecting
        images, adjusting parameters, and setting justification options. The
        layout is dynamically updated based on user selections, providing a
        comprehensive interface for manipulating bas relief settings.

        Args:
            context (bpy.context): The context in which the UI is being drawn.

        Returns:
            None: This method does not return any value; it modifies the layout
            directly.
        """

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # print(dir(layout))
        scene = context.scene

        br = scene.basreliefsettings

        # if br:
        # cutter preset

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Source")
        if br.use_image_source:
            col.prop_search(br, "source_image_name", bpy.data, "images")
        else:
            col.prop_search(br, "view_layer_name", context.scene, "view_layers")
        col.prop(br, "use_image_source")
        col.prop(br, "depth_exponent")
        col.prop(br, "advanced")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Parameters")
        col.prop(br, "bit_diameter", text="Ball End Diameter (mm)")
        col.prop(br, "pass_per_radius")
        col.prop(br, "widthmm", text="Desired Width (mm)")
        col.prop(br, "heightmm", text="Desired Height (mm)")
        col.prop(br, "thicknessmm", text="Thickness (mm)")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Justification")
        col.prop(br, "justifyx")
        col.prop(br, "justifyy")
        col.prop(br, "justifyz")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Silhouette")
        col.prop(br, "silhouette_threshold", text="Threshold")
        col.prop(br, "recover_silhouettes")
        if br.recover_silhouettes:
            col.prop(br, "silhouette_scale", text="Scale")
            if br.advanced:
                col.prop(br, "silhouette_exponent", text="Square Exponent")
        # layout.template_curve_mapping(br,'curva')
        # layout.prop(br,'attenuation')

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Iterations")
        if br.advanced:
            col.prop(br, "smooth_iterations", text="Smooth")
        col.prop(br, "vcycle_iterations", text="V-Cycle")
        col.prop(br, "linbcg_iterations", text="LINBCG")

        if br.advanced:
            layout.prop(br, "min_gridsize")
        layout.prop(br, "decimate_ratio")
        layout.prop(br, "use_planar")

        layout.prop(br, "gradient_scaling_mask_use")
        if br.advanced:
            if br.gradient_scaling_mask_use:
                layout.prop_search(br, "gradient_scaling_mask_name", bpy.data, "images")
            layout.prop(br, "detail_enhancement_use")
            if br.detail_enhancement_use:
                # layout.prop(br,'detail_enhancement_freq')
                layout.prop(br, "detail_enhancement_amount")
                # print(dir(layout))
                # layout.prop(s.view_settings.curve_mapping,"curves")
                # layout.label('Frequency scaling:')
                # s.view_settings.curve_mapping.clip_max_y=2

                # layout.template_curve_mapping(s.view_settings, "curve_mapping")

        # layout.prop(br,'scale_down_before_use')
        # if br.scale_down_before_use:
        # 	layout.prop(br,'scale_down_before')
        box = layout.box()
        col = box.column()
        col.scale_y = 1.2
        col.operator("scene.calculate_bas_relief", text="Calculate Relief", icon="RNDCURVE")
