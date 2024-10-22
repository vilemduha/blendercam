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
    panel_interface_level = 0

    prop_level = {
        "draw_use_layers": 0,
        "draw_maxz": 1,
        "draw_minz": 1,
        "draw_ambient": 1,
        "draw_limit_curve": 1,
        "draw_first_down": 1,
    }

    def draw_use_layers(self):
        if not self.has_correct_level():
            return
        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.prop(self.op, "use_layers")
        if self.op.use_layers:
            row.prop(self.op, "stepdown")
            self.draw_first_down(col)

    def draw_first_down(self, col):
        if not self.has_correct_level():
            return
        if self.op.strategy in ["CUTOUT", "POCKET", "MEDIAL_AXIS"]:
            row = col.row(align=True)
            row.label(text="")
            row.prop(self.op, "first_down")

    def draw_maxz(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, "maxz")
        self.layout.prop(self.op.movement, "free_height")
        if self.op.maxz > self.op.movement.free_height:
            self.layout.label(text="!ERROR! COLLISION!")
            self.layout.label(text="Depth Start > Free Movement Height")
            self.layout.label(text="!ERROR! COLLISION!")

    def draw_minz(self):
        if not self.has_correct_level():
            return
        if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
            if self.op.strategy == "CURVE":
                self.layout.label(text="Cannot Use Depth from Object Using Curves")

            row = self.layout.row(align=True)
            row.label(text="Set Max Depth from")
            row.prop(self.op, "minz_from", text="")
            if self.op.minz_from == "CUSTOM":
                self.layout.prop(self.op, "minz")

        else:
            self.layout.prop(self.op, "source_image_scale_z")
            self.layout.prop(self.op, "source_image_size_x")
            if self.op.source_image_name != "":
                i = bpy.data.images[self.op.source_image_name]
                if i is not None:
                    sy = int((self.op.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000
                    self.layout.label(text="Image Size on Y Axis: " + strInUnits(sy, 8))
                    self.layout.separator()
            self.layout.prop(self.op, "source_image_offset")
            col = self.layout.column(align=True)
            col.prop(self.op, "source_image_crop", text="Crop Source Image")
            if self.op.source_image_crop:
                col.prop(self.op, "source_image_crop_start_x", text="Start X")
                col.prop(self.op, "source_image_crop_start_y", text="Start Y")
                col.prop(self.op, "source_image_crop_end_x", text="End X")
                col.prop(self.op, "source_image_crop_end_y", text="End Y")

    def draw_ambient(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS"]:
            self.layout.prop(self.op, "ambient_behaviour")
            if self.op.ambient_behaviour == "AROUND":
                self.layout.prop(self.op, "ambient_radius")
            self.layout.prop(self.op, "ambient_cutter_restrict")

    def draw_limit_curve(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ["BLOCK", "SPIRAL", "CIRCLES", "PARALLEL", "CROSS"]:
            self.layout.prop(self.op, "use_limit_curve")
            if self.op.use_limit_curve:
                self.layout.prop_search(self.op, "limit_curve", bpy.data, "objects")

    def draw(self, context):
        self.context = context

        self.draw_use_layers()
        self.draw_maxz()
        self.draw_minz()
        self.draw_ambient()
        self.draw_limit_curve()
