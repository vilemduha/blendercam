"""Fabex 'pie_pack_slice_relief.py'

'Pack, Slice and Bas Relief' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_PackSliceRelief(Menu):
    bl_label = "∴    Pack | Slice | Bas Relief    ∴"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column(align=True)
        box = column.box()
        box.label(text="Pack", icon="PACKAGE")
        pack_settings = scene.cam_pack
        column.label(text="Warning - Algorithm Is Slow.")
        column.label(text="Only for Curves Now.")
        column.operator("object.cam_pack_objects")
        column.prop(pack_settings, "sheet_fill_direction")
        column.prop(pack_settings, "sheet_x")
        column.prop(pack_settings, "sheet_y")
        column.prop(pack_settings, "distance")
        column.prop(pack_settings, "tolerance")
        column.prop(pack_settings, "rotate")
        if pack_settings.rotate:
            column.prop(pack_settings, "rotate_angle")

        # Right
        box = pie.box()
        column = box.column(align=True)
        box = column.box()
        box.label(text="Slice", icon="ALIGN_JUSTIFY")
        slice_settings = scene.cam_slice
        column.operator("object.cam_slice_objects")
        column.prop(slice_settings, "slice_distance")
        column.prop(slice_settings, "slice_above0")
        column.prop(slice_settings, "slice_3d")
        column.prop(slice_settings, "indexes")

        # Bottom
        column = pie.column()
        column.separator(factor=5)
        box = column.box()
        column = box.column(align=True)
        box = column.box()
        box.label(text="Bas Relief", icon="RNDCURVE")
        relief_settings = scene.basreliefsettings
        column.operator("scene.calculate_bas_relief", text="Calculate Relief")
        column.prop(relief_settings, "advanced")
        column.prop(relief_settings, "use_image_source")
        if relief_settings.use_image_source:
            column.prop_search(relief_settings, "source_image_name", bpy.data, "images")
        else:
            column.prop_search(relief_settings, "view_layer_name", bpy.context.scene, "view_layers")
        column.prop(relief_settings, "depth_exponent")
        column.label(text="Project parameters")
        column.prop(relief_settings, "bit_diameter")
        column.prop(relief_settings, "pass_per_radius")
        column.prop(relief_settings, "widthmm")
        column.prop(relief_settings, "heightmm")
        column.prop(relief_settings, "thicknessmm")

        column.label(text="Justification")
        column.prop(relief_settings, "justifyx")
        column.prop(relief_settings, "justifyy")
        column.prop(relief_settings, "justifyz")

        column.label(text="Silhouette")
        column.prop(relief_settings, "silhouette_threshold")
        column.prop(relief_settings, "recover_silhouettes")
        if relief_settings.recover_silhouettes:
            column.prop(relief_settings, "silhouette_scale")
            if relief_settings.advanced:
                column.prop(relief_settings, "silhouette_exponent")
        # column.template_curve_mapping(relief_settings,'curva')
        if relief_settings.advanced:
            # column.prop(relief_settings,'attenuation')
            column.prop(relief_settings, "min_gridsize")
            column.prop(relief_settings, "smooth_iterations")
        column.prop(relief_settings, "vcycle_iterations")
        column.prop(relief_settings, "linbcg_iterations")
        column.prop(relief_settings, "use_planar")
        column.prop(relief_settings, "decimate_ratio")
        column.prop(relief_settings, "gradient_scaling_mask_use")
        if relief_settings.advanced:
            if relief_settings.gradient_scaling_mask_use:
                column.prop_search(
                    relief_settings, "gradient_scaling_mask_name", bpy.data, "images"
                )
            column.prop(relief_settings, "detail_enhancement_use")
            if relief_settings.detail_enhancement_use:
                # column.prop(relief_settings,'detail_enhancement_freq')
                column.prop(relief_settings, "detail_enhancement_amount")

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"
