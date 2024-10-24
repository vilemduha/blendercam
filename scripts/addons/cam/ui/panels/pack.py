"""CNC CAM 'pack.py'

'Pack Curves on Sheet' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_PACK_Panel(CAMButtonsPanel, Panel):
    """CAM Pack Panel"""

    bl_label = "Pack Curves on Sheet"
    bl_idname = "WORLD_PT_CAM_PACK"
    panel_interface_level = 2

    def draw(self, context):
        if self.level >= 2:
            layout = self.layout
            scene = bpy.context.scene
            settings = scene.cam_pack
            layout.operator("object.cam_pack_objects")
            layout.prop(settings, "sheet_fill_direction")
            layout.prop(settings, "sheet_x")
            layout.prop(settings, "sheet_y")
            layout.prop(settings, "distance")
            layout.prop(settings, "tolerance")
            layout.prop(settings, "rotate")
            if settings.rotate:
                layout.prop(settings, "rotate_angle")
