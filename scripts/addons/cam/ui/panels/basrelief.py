"""Fabex 'basrelief.py'

'Bas Relief' properties and panel in Properties > Render
"""

import bpy
from bpy.types import Panel


class BASRELIEF_Panel(Panel):
    """Bas Relief Panel"""

    bl_label = "[ Bas Relief ]"
    bl_idname = "FABEX_PT_BASRELIEF"
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

        scene = context.scene

        br = scene.basreliefsettings

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
                layout.prop(br, "detail_enhancement_amount")
        box = layout.box()
        col = box.column()
        col.scale_y = 1.2
        col.operator("scene.calculate_bas_relief", text="Calculate Relief", icon="RNDCURVE")
