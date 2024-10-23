"""CNC CAM 'area.py'

'CAM Operation Area' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel
from ...simple import strInUnits


class CAM_AREA_Panel(CAMButtonsPanel, Panel):
    """CAM Operation Area Panel"""

    bl_label = "CAM Operation Area"
    bl_idname = "WORLD_PT_CAM_OPERATION_AREA"

    def draw(self, context):
        layout = self.layout
        if self.op is not None:
            # Use Layers
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(self.op, "use_layers")
            if self.op.use_layers:
                row.prop(self.op, "stepdown")

                # First Down
                if self.level >= 1 and self.op.strategy in ["CUTOUT", "POCKET", "MEDIAL_AXIS"]:
                    row = col.row(align=True)
                    row.label(text="")
                    row.prop(self.op, "first_down")

            # Max Z
            if self.level >= 1:
                col = layout.column(align=True)
                col.prop(self.op, "maxz")
                col.prop(self.op.movement, "free_height")
                if self.op.maxz > self.op.movement.free_height:
                    col.label(text="!ERROR! COLLISION!")
                    col.label(text="Depth Start > Free Movement Height")
                    col.label(text="!ERROR! COLLISION!")

            # Min Z
            if self.level >= 1:
                if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
                    if self.op.strategy == "CURVE":
                        col.label(text="Cannot Use Depth from Object Using Curves")

                    row = col.row(align=True)
                    row.label(text="Set Max Depth from")
                    row.prop(self.op, "minz_from", text="")
                    if self.op.minz_from == "CUSTOM":
                        row.prop(self.op, "minz")

                else:
                    col.prop(self.op, "source_image_scale_z")
                    col.prop(self.op, "source_image_size_x")
                    if self.op.source_image_name != "":
                        i = bpy.data.images[self.op.source_image_name]
                        if i is not None:
                            size_x = self.op.source_image_size_x / i.size[0]
                            size_y = int(x_size * i.size[1] * 1000000) / 1000
                            col.label(text="Image Size on Y Axis: " + strInUnits(size_y, 8))
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
                    col.prop(self.op, "ambient_behaviour")
                    if self.op.ambient_behaviour == "AROUND":
                        col.prop(self.op, "ambient_radius")
                    col.prop(self.op, "ambient_cutter_restrict")

            # Draw Limit Curve
            if self.level >= 1:
                if self.op.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS"]:
                    col.prop(self.op, "use_limit_curve")
                    if self.op.use_limit_curve:
                        col.prop_search(self.op, "limit_curve", bpy.data, "objects")
