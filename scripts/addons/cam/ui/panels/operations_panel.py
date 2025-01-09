"""Fabex 'operations.py'

'CAM Operations' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_OPERATIONS_Panel(CAMParentPanel, Panel):
    """CAM Operations Panel"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bl_label = "[ Operations ]"
    bl_idname = "FABEX_PT_CAM_OPERATIONS"
    panel_interface_level = 0
    always_show_panel = True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Presets
        if self.level >= 1:
            row = layout.row(align=True)
            row.menu("CAM_OPERATION_MT_presets", text=bpy.types.CAM_OPERATION_MT_presets.bl_label)
            row.operator("render.cam_preset_operation_add", text="", icon="ADD")
            row.operator(
                "render.cam_preset_operation_add", text="", icon="REMOVE"
            ).remove_active = True

        # Operations List
        # create, delete, duplicate, reorder
        row = layout.row()
        row.template_list(
            "CAM_UL_operations",
            "",
            bpy.context.scene,
            "cam_operations",
            bpy.context.scene,
            "cam_active_operation",
        )
        box = row.box()
        col = box.column(align=True)
        col.scale_x = col.scale_y = 1.05
        col.operator("scene.cam_operation_add", icon="ADD", text="")
        col.operator("scene.cam_operation_copy", icon="COPYDOWN", text="")
        col.operator("scene.cam_operation_remove", icon="REMOVE", text="")
        col.separator()
        col.operator("scene.cam_operation_move", icon="TRIA_UP", text="").direction = "UP"
        col.operator("scene.cam_operation_move", icon="TRIA_DOWN", text="").direction = "DOWN"

        if self.op is None:
            return

        # Calculate Path
        if self.op.max_z > self.op.movement.free_height:
            box = layout.box()
            col = box.column(align=True)
            col.alert = True
            col.label(text="! ERROR ! COLLISION !", icon="ERROR")
            col.label(text="Depth Start > Free Movement Height")
            col.label(text="! ERROR ! COLLISION !", icon="ERROR")
            layout.prop(self.op.movement, "free_height")

        if not self.op.valid:
            layout.label(text="Select a Valid Object to Calculate the Path.")
        # will be disabled if not valid
        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 1.2
        col.operator(
            "object.calculate_cam_path", text="Calculate Path & Export Gcode", icon="FILE_CACHE"
        )

        # Export Gcode
        if self.level >= 1:
            if self.op.valid:
                if self.op.name is not None:
                    name = f"cam_path_{self.op.name}"
                    if bpy.context.scene.objects.get(name) is not None:
                        col.operator("object.cam_export", text="Export Gcode", icon="EXPORT")

                # Simulate Op
                col.operator(
                    "object.cam_simulate", text="Simulate This Operation", icon="MESH_GRID"
                )

        box = layout.box()
        col = box.column(align=True)
        # Op Name
        col.prop(self.op, "name")
        # Op Filename
        col.prop(self.op, "filename")
        # Op Source
        col.prop(self.op, "geometry_source")

        if self.op.strategy == "CURVE":
            if self.op.geometry_source == "OBJECT":
                col.prop_search(self.op, "object_name", bpy.data, "objects")
            elif self.op.geometry_source == "COLLECTION":
                col.prop_search(self.op, "collection_name", bpy.data, "collections")
        else:
            if self.op.geometry_source == "OBJECT":
                col.prop_search(self.op, "object_name", bpy.data, "objects")
                if self.op.enable_a_axis:
                    col.prop(self.op, "rotation_a")
                if self.op.enable_b_axis:
                    col.prop(self.op, "rotation_b")

            elif self.op.geometry_source == "COLLECTION":
                col.prop_search(self.op, "collection_name", bpy.data, "collections")
            else:
                col.prop_search(self.op, "source_image_name", bpy.data, "images")

        if self.op.strategy in ["CARVE", "PROJECTED_CURVE"]:
            col.prop_search(self.op, "curve_source", bpy.data, "objects")
            if self.op.strategy == "PROJECTED_CURVE":
                col.prop_search(self.op, "curve_target", bpy.data, "objects")
