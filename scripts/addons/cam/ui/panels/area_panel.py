"""Fabex 'area.py'

'CAM Operation Area' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_AREA_Panel(CAMParentPanel, Panel):
    """CAM Operation Area Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Operation Area ]"
    bl_idname = "FABEX_PT_CAM_OPERATION_AREA"
    panel_interface_level = 0

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        main = layout.column(align=True)

        # Free Height
        box = main.box()
        col = box.column(align=True)
        col.label(text="Z Clearance", icon="CON_FLOOR")
        col.prop(self.op.movement, "free_height")
        if self.op.max_z > self.op.movement.free_height:
            box = col.box()
            col = box.column(align=True)
            col.alert = True
            col.label(text="! POSSIBLE COLLISION !", icon="ERROR")
            col.label(text="Depth Start > Free Movement")

        # Max Z
        if self.level >= 1:
            box = main.box()
            col = box.column(align=True)
            col.label(text="Operation Depth")
            col.prop(self.op, "max_z", text="Start")
            # col.prop(self.op.movement, "free_height")
            if self.op.max_z > self.op.movement.free_height:
                box = col.box()
                box.alert = True
                sub = box.column(align=True)
                sub.label(text="! ERROR ! COLLISION !", icon="ERROR")
                sub.label(text="Depth Start > Free Movement Height")
                sub.label(text="! ERROR ! COLLISION !", icon="ERROR")

        # Min Z
        if self.level >= 1:
            if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
                if self.op.strategy == "CURVE":
                    box = col.box()
                    box.alert = True
                    box.label(text="Cannot Use Depth from Object Using Curves", icon="ERROR")
                depth = self.op.min_z_from
                if depth == "MATERIAL":
                    icon = depth
                elif depth == "OBJECT":
                    icon = "OBJECT_DATA"
                else:
                    icon = "USER"
                col.prop(self.op, "min_z_from", text="Max", icon=icon)
                if self.op.min_z_from == "CUSTOM":
                    col.prop(self.op, "min_z")

            else:
                col.prop(self.op, "source_image_scale_z")
                col.prop(self.op, "source_image_size_x")
                if self.op.source_image_name != "":
                    col.prop(self.op, "source_image_size_y")
                    col.separator()
                col.prop(self.op, "source_image_offset")
                col.prop(self.op, "source_image_crop", text="Crop Source Image")
                if self.op.source_image_crop:
                    col.prop(self.op, "source_image_crop_start_x", text="Start X")
                    col.prop(self.op, "source_image_crop_start_y", text="Start Y")
                    col.prop(self.op, "source_image_crop_end_x", text="End X")
                    col.prop(self.op, "source_image_crop_end_y", text="End Y")

        # Draw Ambient
        if self.level >= 1:
            if self.op.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS"]:
                box = main.box()
                col = box.column(align=True)
                col.label(text="Ambient")
                col.prop(self.op, "ambient_behaviour", text="Surfaces")
                if self.op.ambient_behaviour == "AROUND":
                    col.prop(self.op, "ambient_radius")
                row = col.row()
                row.use_property_split = False
                row.prop(self.op, "ambient_cutter_restrict")

        # Draw Limit Curve
        if self.level >= 1:
            if self.op.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS", "WATERLINE"]:
                main.use_property_split = False
                col = main.column(align=False)
                header, panel = col.panel("limit", default_closed=True)
                header.prop(self.op, "use_limit_curve", text="Limit Curve")
                if panel:
                    panel.enabled = self.op.use_limit_curve
                    col = panel.column(align=True)
                    col.use_property_split = True
                    col.prop_search(self.op, "limit_curve", bpy.data, "objects", text="Curve")

        # Use Layers
        main.use_property_split = False
        header, panel = main.panel("layers", default_closed=False)
        header.prop(self.op, "use_layers", text="Layers")
        if panel:
            panel.enabled = self.op.use_layers
            col = panel.column(align=True)
            col.use_property_split = True
            col.prop(self.op, "stepdown", text="Layer Height")
            # First Down
            if self.level >= 1 and self.op.strategy in ["CUTOUT", "POCKET", "MEDIAL_AXIS"]:
                row = col.row()
                row.use_property_split = False
                row.prop(self.op, "first_down")
