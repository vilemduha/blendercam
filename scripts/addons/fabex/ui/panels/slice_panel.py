"""Fabex 'slice.py'

'Slice Model to Plywood Sheets' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_SLICE_Panel(CAMParentPanel, Panel):
    """CAM Slicer Panel"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bl_label = "[ Slice ]"
    bl_idname = "FABEX_PT_CAM_SLICE"
    bl_options = {"DEFAULT_CLOSED"}
    panel_interface_level = 2
    use_property_split = True

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = bpy.context.scene
        settings = scene.cam_slice
        col = layout.column(align=True)
        col.prop(settings, "slice_distance")
        col.prop(settings, "slice_above_0")
        col.prop(settings, "slice_3d")
        col.prop(settings, "indexes")

        box = layout.box()
        col = box.column()
        col.scale_y = 1.2
        col.operator("object.cam_slice_objects", text="Slice Object", icon="ALIGN_JUSTIFY")
