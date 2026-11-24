"""Fabex 'blank.py'

Empty panel in Sidebar > CNC
"""

from typing import ClassVar

from bpy.types import Panel


class CAM_BLANK_Panel(Panel):
    """CAM Blank Panel"""

    bl_idname = "CAM_PT_blank"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"
    bl_options: ClassVar = {"HIDE_HEADER"}

    def draw(self, context):
        pass
