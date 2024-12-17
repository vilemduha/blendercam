"""Fabex 'preferences.py'

Class to store all Addon preferences.
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import (
    AddonPreferences,
)

from .utilities.version_utils import opencamlib_version, shapely_version


class CamAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    op_preset_update: BoolProperty(
        name="Have the Operation Presets Been Updated",
        default=False,
    )

    default_interface_level: EnumProperty(
        name="Interface Level in New File",
        description="Choose visible options",
        items=[
            (
                "0",
                "Basic",
                "Only show Essential Options",
            ),
            (
                "1",
                "Advanced",
                "Show Advanced Options",
            ),
            (
                "2",
                "Complete",
                "Show All Options",
            ),
            (
                "3",
                "Experimental",
                "Show Experimental Options",
            ),
        ],
        default="3",
    )

    default_shading: EnumProperty(
        name="Viewport Shading in New File",
        description="Choose viewport shading preset",
        items=[
            (
                "DEFAULT",
                "Default",
                "Standard viewport shading",
            ),
            (
                "DELUXE",
                "Deluxe",
                "Cavity, Curvature, Depth of Field, Shadows & Object Colors",
            ),
            (
                "CLEAN_DEFAULT",
                "Clean Default",
                "Standard viewport shading with no overlays",
            ),
            (
                "CLEAN_DELUXE",
                "Clean Deluxe",
                "Deluxe shading with no overlays",
            ),
            (
                "PREVIEW",
                "Preview",
                "HDRI Lighting Preview",
            ),
        ],
        default="DEFAULT",
    )

    default_layout: EnumProperty(
        name="Panel Layout",
        description="Presets for all panel locations",
        items=[
            (
                "CLASSIC",
                "Classic",
                "Properties Area holds most panels, Tools holds the rest",
            ),
            (
                "MODERN",
                "Modern",
                "Properties holds Main panels, Sidebar holds Operation panels, Tools holds Tools",
            ),
            (
                "USER",
                "User",
                "Define your own locations for panels",
            ),
        ],
        default="MODERN",
    )

    default_main_location: EnumProperty(
        name="Main Panels",
        description="Location for Chains, Operations, Material, Machine, Pack, Slice Panels",
        items=[
            (
                "PROPERTIES",
                "Properties",
                "Default panel location is the Render tab of the Properties Area",
            ),
            (
                "SIDEBAR",
                "Sidebar (N-Panel)",
                "Common location for addon UI, press N to show/hide",
            ),
            (
                "TOOLS",
                "Tools (T-Panel)",
                "Blender's Tool area, press T to show/hide",
            ),
        ],
        default="PROPERTIES",
    )

    default_operation_location: EnumProperty(
        name="Operation Panels",
        description="Location for Setup, Area, Cutter, Feedrate, Optimisation, Movement, G-code",
        items=[
            (
                "PROPERTIES",
                "Properties",
                "Default panel location is the Render tab of the Properties Area",
            ),
            (
                "SIDEBAR",
                "Sidebar (N-Panel)",
                "Common location for addon UI, press N to show/hide",
            ),
            (
                "TOOLS",
                "Tools (T-Panel)",
                "Blender's Tool area, press T to show/hide",
            ),
        ],
        default="SIDEBAR",
    )

    default_tools_location: EnumProperty(
        name="Tools Panels",
        description="Location for Curve Tools, Curve Creators, Info",
        items=[
            (
                "PROPERTIES",
                "Properties",
                "Default panel location is the Render tab of the Properties Area",
            ),
            (
                "SIDEBAR",
                "Sidebar (N-Panel)",
                "Common location for addon UI, press N to show/hide",
            ),
            (
                "TOOLS",
                "Tools (T-Panel)",
                "Blender's Tool area, press T to show/hide",
            ),
        ],
        default="TOOLS",
    )

    user_main_location: EnumProperty(
        name="Main Panels",
        items=[
            (
                "PROPERTIES",
                "Properties",
                "Default panel location is the Render tab of the Properties Area",
            ),
            (
                "SIDEBAR",
                "Sidebar (N-Panel)",
                "Common location for addon UI, press N to show/hide",
            ),
            (
                "TOOLS",
                "Tools (T-Panel)",
                "Blender's Tool area, press T to show/hide",
            ),
        ],
        default="PROPERTIES",
    )

    user_operation_location: EnumProperty(
        name="Operation Panels",
        items=[
            (
                "PROPERTIES",
                "Properties",
                "Default panel location is the Render tab of the Properties Area",
            ),
            (
                "SIDEBAR",
                "Sidebar (N-Panel)",
                "Common location for addon UI, press N to show/hide",
            ),
            (
                "TOOLS",
                "Tools (T-Panel)",
                "Blender's Tool area, press T to show/hide",
            ),
        ],
        default="SIDEBAR",
    )

    user_tools_location: EnumProperty(
        name="Tools Panels",
        items=[
            (
                "PROPERTIES",
                "Properties",
                "Default panel location is the Render tab of the Properties Area",
            ),
            (
                "SIDEBAR",
                "Sidebar (N-Panel)",
                "Common location for addon UI, press N to show/hide",
            ),
            (
                "TOOLS",
                "Tools (T-Panel)",
                "Blender's Tool area, press T to show/hide",
            ),
        ],
        default="TOOLS",
    )

    default_machine_preset: StringProperty(
        name="Machine Preset in New File",
        description="So that machine preset choice persists between files",
        default="",
    )

    show_popups: BoolProperty(
        name="Show Warning Popups",
        description="Shows a Popup window when there is a warning",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        col = box.column(align=True)
        col.label(text="User Interface", icon="DESKTOP")
        col.label(text="User Panel Layout")
        col.prop(context.scene.interface, "main_location", text="Main")
        col.prop(context.scene.interface, "operation_location", text="Operation")
        col.prop(context.scene.interface, "tools_location", text="Tools")
        col = box.column(align=True)
        col.label(text="Warning Popups", icon="WINDOW")
        col.prop(self, "show_popups")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Library", icon="ASSET_MANAGER")
        # OpenCAMLib Version
        ocl_version = opencamlib_version()
        if ocl_version is None:
            col.label(text="OpenCAMLib is not Installed")
        else:
            col.label(text=f"OpenCAMLib v{ocl_version}")
        # Shapely Version
        shape_version = shapely_version()
        if shape_version is None:
            col.label(text="Shapely is not Installed")
        else:
            col.label(text=f"Shapely v{shape_version}")
