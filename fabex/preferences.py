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
from bpy.types import AddonPreferences

from . import __package__ as base_package
from .utilities.version_utils import (
    opencamlib_version,
    shapely_version,
    get_numba_version,
    get_llvmlite_version,
)


class CamAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package,
    # or 'base_package' in this case
    bl_idname = base_package

    op_preset_update: BoolProperty(
        name="Have the Operation Presets Been Updated",
        default=False,
    )

    wireframe_color: EnumProperty(
        name="Wire Color Source",
        description="Wireframe color comes from Object, Theme or a Random color",
        items=[
            (
                "OBJECT",
                "Object",
                "Show object color on wireframe",
            ),
            (
                "THEME",
                "Theme",
                "Show Scene wireframes with the theme's wire color",
            ),
            (
                "RANDOM",
                "Random",
                "Show random object color on wireframe",
            ),
        ],
        default="OBJECT",
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

    default_simulation_material: EnumProperty(
        name="Simulation Shader",
        items=[
            (
                "GLASS",
                "Glass",
                "Glass or Clear Acrylic-type Material",
            ),
            (
                "METAL",
                "Metal",
                "Metallic Material",
            ),
            (
                "PLASTIC",
                "Plastic",
                "Plastic-type Material",
            ),
            (
                "WOOD",
                "Wood",
                "Wood Grain-type Material",
            ),
        ],
        default="WOOD",
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

        names = context.scene.cam_names
        machine = context.scene.cam_machine
        material = context.scene.cam_material

        col = layout.column(align=True)

        # User Interface Dropdown
        header, panel = col.panel("UI", default_closed=True)
        header.label(text="User Interface", icon="DESKTOP")
        if panel:
            col = panel.column(align=True)
            col.label(text="User Panel Layout")
            col.prop(context.scene.interface, "main_location", text="Main")
            col.prop(context.scene.interface, "operation_location", text="Operation")
            col.prop(context.scene.interface, "tools_location", text="Tools")
            col = panel.column(align=True)
            col.label(text="Warning Popups", icon="WINDOW")
            col.prop(self, "show_popups")

        # Colors Dropdown
        header, panel = col.panel("Colors", default_closed=True)
        header.label(text="Colors", icon="COLOR")
        if panel:
            col = panel.column(align=True)
            col.label(text="Viewport")
            col.prop(self, "wireframe_color")
            col.prop(machine, "wire_color", text="Machine Color")
            col.prop(material, "wire_color", text="Material Color")
            col.prop(machine, "path_color", text="Path Color")

        # Settings Dropdown
        header, panel = col.panel("Settings", default_closed=True)
        header.label(text="Settings", icon="TOOL_SETTINGS")
        if panel:
            col = panel.column(align=True)
            col.label(text="Naming System", icon="FONT_DATA")

            col_box = col.box()
            col_box.active = False
            column = col_box.column(align=True)
            column.label(
                text="Assign custom names to Paths, Operations, Chains, Simulations and Files",
            )

            row = col.row(align=True)
            row.alignment = "LEFT"
            row.label(text="Separator:")
            row.prop(names, "separator", text="")

            col_box = col.box()
            col_box.active = False
            column = col_box.column(align=True)
            column.label(text="A separator is placed between each name item below")
            column.label(text="(none) or blank items will be ignored")
            column.label(text="Placeholder values  added if data cannot be accessed")
            column.label(
                text="File Extensions added automatically based on Machine Post Processor",
            )

            squish = 0.7

            row = col.row(align=True)
            row.alignment = "RIGHT"
            row.label(text="Path:")
            row = row.row(align=True)
            row.scale_x = squish
            row.alignment = "LEFT"
            row.prop(names, "path_prefix", text="")
            row.prop(names, "path_main_1", text="")
            row.prop(names, "path_main_2", text="")
            row.prop(names, "path_main_3", text="")
            row.prop(names, "path_suffix", text="")
            row = col.row(align=True)
            row.alignment = "RIGHT"
            row.label(text="Operation:")
            row = row.row(align=True)
            row.scale_x = squish
            row.alignment = "LEFT"
            row.prop(names, "operation_prefix", text="")
            row.prop(names, "operation_main_1", text="")
            row.prop(names, "operation_main_2", text="")
            row.prop(names, "operation_main_3", text="")
            row.prop(names, "operation_suffix", text="")
            row = col.row(align=True)
            row.alignment = "RIGHT"
            row.label(text="Chain:")
            row = row.row(align=True)
            row.scale_x = squish
            row.alignment = "LEFT"
            row.prop(names, "chain_prefix", text="")
            row.prop(names, "chain_main_1", text="")
            row.prop(names, "chain_main_2", text="")
            row.prop(names, "chain_main_3", text="")
            row.prop(names, "chain_suffix", text="")
            row = col.row(align=True)
            row.alignment = "RIGHT"
            row.label(text="Simulation:")
            row = row.row(align=True)
            row.scale_x = squish
            row.alignment = "LEFT"
            row.prop(names, "simulation_prefix", text="")
            row.prop(names, "simulation_main_1", text="")
            row.prop(names, "simulation_main_2", text="")
            row.prop(names, "simulation_main_3", text="")
            row.prop(names, "simulation_suffix", text="")
            if not names.link_names:
                row = col.row(align=True)
                row.alignment = "RIGHT"
                row.label(text="File:")
                row = row.row(align=True)
                row.scale_x = squish
                row.alignment = "LEFT"
                row.prop(names, "file_prefix", text="")
                row.prop(names, "file_main_1", text="")
                row.prop(names, "file_main_2", text="")
                row.prop(names, "file_main_3", text="")
                row.prop(names, "file_suffix", text="")

            row = col.row(align=True)
            row.prop(names, "link_names")

            col.label(text="Export", icon="FILE_FOLDER")
            col.prop(names, "default_export_location")

            col.label(text="Simulation", icon="SHADING_TEXTURE")
            col.prop(self, "default_simulation_material", text="Material Shader")

        # Logs Dropdown
        header, panel = col.panel("Log", default_closed=True)
        header.label(text="Logs", icon="DOCUMENTS")

        if panel:
            col = panel.column(align=True)
            row = col.row()
            row.operator("scene.cam_open_log_folder", icon="FILEBROWSER")
            row.operator("scene.cam_purge_logs", icon="TRASH")

        # Library Dropdown
        header, panel = col.panel("Lib", default_closed=True)
        header.label(text="Library", icon="ASSET_MANAGER")

        if panel:
            col = panel.column(align=True)

            row = col.row(align=True)
            row.alignment = "CENTER"
            l_col = row.column(align=True)
            l_col.alignment = "RIGHT"
            r_col = row.column(align=True)
            r_col.alignment = "LEFT"

            # OpenCAMLib Version
            ocl_version = opencamlib_version()
            if ocl_version is None:
                l_col.label(text="OpenCAMLib is not Installed")
            else:
                l_col.label(text=f"OpenCAMLib")
                r_col.label(text=f"v{ocl_version}")
            # Shapely Version
            shape_version = shapely_version()
            if shape_version is None:
                l_col.label(text="Shapely is not Installed")
            else:
                l_col.label(text=f"Shapely")
                r_col.label(text=f"v{shape_version}")
            # Numba Version
            numba_version = get_numba_version()
            if numba_version is None:
                l_col.label(text="Numba is not Installed")
            else:
                l_col.label(text=f"Numba")
                r_col.label(text=f"v{numba_version}")
            # LLVMLite Version
            llvmlite_version = get_llvmlite_version()
            if llvmlite_version is None:
                l_col.label(text="LLVMLite is not Installed")
            else:
                l_col.label(text=f"LLVMLite")
                r_col.label(text=f"v{llvmlite_version}")
