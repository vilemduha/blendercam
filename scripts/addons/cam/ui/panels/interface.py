"""Fabex 'interface.py'

'Interface' properties and panel in Properties > Render
"""

import bpy
from bpy.props import EnumProperty
from bpy.types import Panel, PropertyGroup

from .buttons_panel import CAMButtonsPanel


def update_interface(self, context):
    # set default for new files
    addon_prefs = context.preferences.addons["bl_ext.user_default.fabex"].preferences
    addon_prefs.default_interface_level = context.scene.interface.level
    bpy.ops.wm.save_userpref()


class CAM_INTERFACE_Properties(PropertyGroup):
    level: EnumProperty(
        name="Interface",
        description="Choose visible options",
        items=[
            ("0", "Basic", "Only show essential options"),
            ("1", "Advanced", "Show advanced options"),
            ("2", "Complete", "Show all options"),
            ("3", "Experimental", "Show experimental options"),
        ],
        default="0",
        update=update_interface,
    )


# class CAM_INTERFACE_Panel(CAMButtonsPanel, Panel):
#     bl_label = "Interface"
#     bl_idname = "WORLD_PT_CAM_INTERFACE"
#     bl_options = {"HIDE_HEADER"}
#     panel_interface_level = 0
#     always_show_panel = True

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         col = layout.column()
#         col.prop(context.scene.interface, "level")
