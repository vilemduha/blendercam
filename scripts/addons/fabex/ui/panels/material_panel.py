"""Fabex 'material.py'

'CAM Material' properties and panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_MATERIAL_Panel(CAMParentPanel, Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bl_label = "[ Material ]"
    bl_idname = "FABEX_PT_CAM_MATERIAL"
    panel_interface_level = 0

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Estimate from Image
        if self.op.geometry_source not in ["OBJECT", "COLLECTION"]:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Size")
            col.label(text="Estimated from Image")

        # Estimate from Object
        if self.level >= 1:
            if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
                box = layout.box()
                col = box.column(align=True)
                col.label(text="Size")
                row = col.row()
                row.use_property_split = False
                row.prop(self.op.material, "estimate_from_model", text="Size from Model")
                if self.op.material.estimate_from_model:
                    col.prop(self.op.material, "radius_around_model", text="Additional Radius")
                else:
                    col.prop(self.op.material, "origin")
                    col.prop(self.op.material, "size")

        # Axis Alignment
        if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Position")
            row = col.row()
            row.use_property_split = False
            row.prop(self.op.material, "center_x")
            row = col.row()
            row.use_property_split = False
            row.prop(self.op.material, "center_y")
            col.prop(self.op.material, "z_position")

            box = layout.box()
            col = box.column()
            col.scale_y = 1.2
            col.operator(
                "object.material_cam_position", text="Position Object", icon="ORIENTATION_LOCAL"
            )
