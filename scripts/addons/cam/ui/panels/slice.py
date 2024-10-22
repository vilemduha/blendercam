"""CNC CAM 'slice.py'

'Slice Model to Plywood Sheets' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_SLICE_Panel(CAMButtonsPanel, Panel):
    """CAM Slicer Panel"""
    bl_label = "Slice Model to Plywood Sheets"
    bl_idname = "WORLD_PT_CAM_SLICE"
    panel_interface_level = 2

    COMPAT_ENGINES = {'CNCCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        settings = scene.cam_slice

        layout.operator("object.cam_slice_objects")
        layout.prop(settings, 'slice_distance')
        layout.prop(settings, 'slice_above0')
        layout.prop(settings, 'slice_3d')
        layout.prop(settings, 'indexes')
