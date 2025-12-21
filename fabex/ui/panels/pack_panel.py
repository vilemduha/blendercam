"""Fabex 'pack.py'

'Pack Curves on Sheet' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_PACK_Panel(CAMParentPanel, Panel):
    """CAM Pack Panel"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bl_label = "[ Pack ]"
    bl_idname = "FABEX_PT_CAM_PACK"
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
        settings = scene.cam_pack
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Sheet Size")
        col.prop(settings, "sheet_x", text="X")
        col.prop(settings, "sheet_y", text="Y")
        col.prop(settings, "sheet_fill_direction")
        col = layout.column(align=True)
        col.prop(settings, "distance")
        col.prop(settings, "tolerance")
        header, panel = col.panel_prop(settings, "rotate")
        header.label(text="Rotation")
        if panel:
            col = panel.column(align=True)
            col.prop(settings, "rotate_angle", text="Placement Angle Step")

        box_2 = layout.box()
        col = box_2.column()
        col.scale_y = 1.2
        col.operator("object.cam_pack_objects", icon="FCURVE")
