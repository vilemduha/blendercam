"""Fabex 'pie_area.py'

'Operation Area' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Area(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation Area    ∴"

    def draw(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]
        material = operation.material

        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column(align=True)
        col = column.column(align=True)
        row = col.row(align=True)
        row.prop(operation, "use_layers")
        if operation.use_layers:
            row.prop(operation, "stepdown")

        if operation.strategy in ["CUTOUT", "POCKET", "MEDIAL_AXIS"]:
            row = col.row(align=True)
            row.label(text="")
            row.prop(operation, "first_down")

        # Right
        box = pie.box()
        column = box.column(align=True)
        if operation.geometry_source in ["OBJECT", "COLLECTION"]:
            if operation.strategy == "CURVE":
                column.label(text="Cannot Use Depth from Object Using Curves")

            row = column.row(align=True)
            row.label(text="Max Depth from")
            row.prop(operation, "minz_from", text="")
            if operation.minz_from == "CUSTOM":
                column.prop(operation, "minz")

        else:
            column.prop(operation, "source_image_scale_z")
            column.prop(operation, "source_image_size_x")
            if operation.source_image_name != "":
                i = bpy.data.images[operation.source_image_name]
                if i is not None:
                    sy = (
                        int((operation.source_image_size_x / i.size[0]) * i.size[1] * 1000000)
                        / 1000
                    )
                    column.label(text="Image Size on Y Axis: " + strInUnits(sy, 8))
                    column.separator()
            column.prop(operation, "source_image_offset")
            col = column.column(align=True)
            col.prop(operation, "source_image_crop", text="Crop Source Image")
            if operation.source_image_crop:
                col.prop(operation, "source_image_crop_start_x", text="start x")
                col.prop(operation, "source_image_crop_start_y", text="start y")
                col.prop(operation, "source_image_crop_end_x", text="end x")
                col.prop(operation, "source_image_crop_end_y", text="end y")

        # Bottom
        box = pie.box()
        column = box.column(align=True)
        if operation.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS"]:
            column.prop(operation, "ambient_behaviour")
            if operation.ambient_behaviour == "AROUND":
                column.prop(operation, "ambient_radius")
            column.prop(operation, "ambient_cutter_restrict")

        if operation.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS"]:
            column.prop(operation, "use_limit_curve")
            if operation.use_limit_curve:
                column.prop_search(operation, "limit_curve", bpy.data, "objects")

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="BACK").name = "VIEW3D_MT_PIE_Operation"
