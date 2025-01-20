"""Fabex 'basrelief.py'

Module to allow the creation of reliefs from Images or View Layers.
(https://en.wikipedia.org/wiki/Relief#Bas-relief_or_low_relief)
"""

import time

import numpy

import bpy

from bpy.types import Operator
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from ..constants import PRECISION

from ..bas_relief import (
    problem_areas,
    render_scene,
    relief,
    ReliefError,
)


class DoBasRelief(Operator):
    """Calculate Bas Relief"""

    bl_idname = "scene.calculate_bas_relief"
    bl_label = "Calculate Bas Relief"
    bl_options = {"REGISTER", "UNDO"}

    processes = []

    # Bas Relief Properties
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
    width_mm: IntProperty(
        name="Desired Width in mm",
        default=200,
        min=5,
        max=4000,
    )
    height_mm: IntProperty(
        name="Desired Height in mm",
        default=150,
        min=5,
        max=4000,
    )
    thickness_mm: IntProperty(
        name="Thickness in mm",
        default=15,
        min=5,
        max=100,
    )

    justify_x: EnumProperty(
        name="X",
        items=[
            ("1", "Left", "", 0),
            ("-0.5", "Centered", "", 1),
            ("-1", "Right", "", 2),
        ],
        default="-1",
    )
    justify_y: EnumProperty(
        name="Y",
        items=[
            ("1", "Bottom", "", 0),
            ("-0.5", "Centered", "", 2),
            ("-1", "Top", "", 1),
        ],
        default="-1",
    )
    justify_z: EnumProperty(
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
        description="Initial depth map is taken to this power. Higher = sharper relief",
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
        description="Set lower for flatter relief, and when using planar constraint",
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

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        """Execute the relief rendering process based on the provided context.

        This function retrieves the scene and its associated bas relief
        settings. It checks if an image source is being used and sets the view
        layer name accordingly. The function then attempts to render the scene
        and generate the relief. If any errors occur during these processes,
        they are reported, and the operation is canceled.

        Args:
            context: The context in which the function is executed.

        Returns:
            dict: A dictionary indicating the result of the operation, either
        """

        if not self.use_image_source and self.view_layer_name == "":
            self.view_layer_name = bpy.context.view_layer.name

        try:
            render_scene(
                self.width_mm,
                self.height_mm,
                self.bit_diameter,
                self.pass_per_radius,
                not self.use_image_source,
                self.view_layer_name,
            )
        except ReliefError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        except RuntimeError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        try:
            relief(self)
        except ReliefError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        return {"FINISHED"}

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

        scene = context.scene

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Source")
        if self.use_image_source:
            col.prop_search(self, "source_image_name", bpy.data, "images")
        else:
            col.prop_search(self, "view_layer_name", context.scene, "view_layers")
        col.prop(self, "use_image_source")
        col.prop(self, "depth_exponent")
        col.prop(self, "advanced")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Parameters")
        col.prop(self, "bit_diameter", text="Ball End Diameter (mm)")
        col.prop(self, "pass_per_radius")
        col.prop(self, "widthmm", text="Desired Width (mm)")
        col.prop(self, "heightmm", text="Desired Height (mm)")
        col.prop(self, "thicknessmm", text="Thickness (mm)")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Justification")
        col.prop(self, "justifyx")
        col.prop(self, "justifyy")
        col.prop(self, "justifyz")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Silhouette")
        col.prop(self, "silhouette_threshold", text="Threshold")
        col.prop(self, "recover_silhouettes")
        if self.recover_silhouettes:
            col.prop(self, "silhouette_scale", text="Scale")
            if self.advanced:
                col.prop(self, "silhouette_exponent", text="Square Exponent")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Iterations")
        if self.advanced:
            col.prop(self, "smooth_iterations", text="Smooth")
        col.prop(self, "vcycle_iterations", text="V-Cycle")
        col.prop(self, "linbcg_iterations", text="LINBCG")

        if self.advanced:
            layout.prop(self, "min_gridsize")
        layout.prop(self, "decimate_ratio")
        layout.prop(self, "use_planar")

        layout.prop(self, "gradient_scaling_mask_use")
        if self.advanced:
            if self.gradient_scaling_mask_use:
                layout.prop_search(self, "gradient_scaling_mask_name", bpy.data, "images")
            layout.prop(self, "detail_enhancement_use")
            if self.detail_enhancement_use:
                layout.prop(self, "detail_enhancement_amount")


class ProblemAreas(Operator):
    """Find Bas Relief Problem Areas"""

    bl_idname = "scene.problemareas_bas_relief"
    bl_label = "Problem Areas Bas Relief"
    bl_options = {"REGISTER", "UNDO"}

    processes = []

    # @classmethod
    # def poll(cls, context):
    # 	return context.active_object is not None

    def execute(self, context):
        """Execute the operation related to the bas relief settings in the current
        scene.

        This method retrieves the current scene from the Blender context and
        accesses the bas relief settings. It then calls the `problemAreas`
        function to perform operations related to those settings. The method
        concludes by returning a status indicating that the operation has
        finished successfully.

        Args:
            context (bpy.context): The current Blender context, which provides access

        Returns:
            dict: A dictionary with a status key indicating the operation result,
            specifically {'FINISHED'}.
        """

        s = bpy.context.scene
        br = s.basreliefsettings
        problem_areas(br)
        return {"FINISHED"}
