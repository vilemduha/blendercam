"""Fabex 'interface.py'

'Interface' properties and panel in Properties > Render
"""

import bpy
from bpy.props import EnumProperty
from bpy.types import PropertyGroup

from ..ui.panels.area_panel import CAM_AREA_Panel
from ..ui.panels.basrelief import BASRELIEF_Panel
from ..ui.panels.chains_panel import CAM_CHAINS_Panel
from ..ui.panels.curve_create_panel import VIEW3D_PT_tools_create
from ..ui.panels.curve_tools_panel import VIEW3D_PT_tools_curvetools
from ..ui.panels.cutter_panel import CAM_CUTTER_Panel
from ..ui.panels.feedrate_panel import CAM_FEEDRATE_Panel
from ..ui.panels.gcode_panel import CAM_GCODE_Panel
from ..ui.panels.info_panel import CAM_INFO_Panel
from ..ui.panels.machine_panel import CAM_MACHINE_Panel
from ..ui.panels.material_panel import CAM_MATERIAL_Panel
from ..ui.panels.movement_panel import CAM_MOVEMENT_Panel
from ..ui.panels.op_properties_panel import CAM_OPERATION_PROPERTIES_Panel
from ..ui.panels.operations_panel import CAM_OPERATIONS_Panel
from ..ui.panels.optimisation_panel import CAM_OPTIMISATION_Panel
from ..ui.panels.pack_panel import CAM_PACK_Panel
from ..ui.panels.slice_panel import CAM_SLICE_Panel


def update_interface(self, context):
    # set default for new files
    addon_prefs = context.preferences.addons["bl_ext.user_default.fabex"].preferences
    addon_prefs.default_interface_level = context.scene.interface.level
    bpy.ops.wm.save_userpref()


def update_shading(self, context):
    view3d = [a.spaces[0] for a in context.screen.areas if a.type == "VIEW_3D"][0]
    shading = view3d.shading
    overlay = view3d.overlay

    if context.scene.interface.shading == "DEFAULT":
        shading.type = "SOLID"
        shading.color_type = "MATERIAL"
        shading.show_shadows = False
        shading.show_cavity = False
        shading.use_dof = False
        overlay.show_overlays = True
        overlay.show_floor = True
        overlay.show_axis_x = True
        overlay.show_axis_y = True

    elif context.scene.interface.shading == "DELUXE":
        shading.type = "SOLID"
        shading.color_type = "OBJECT"
        shading.show_shadows = True
        shading.show_cavity = True
        shading.cavity_type = "BOTH"
        shading.use_dof = True
        overlay.show_overlays = True
        overlay.show_floor = True
        overlay.show_axis_x = True
        overlay.show_axis_y = True

    elif context.scene.interface.shading == "CLEAN_DEFAULT":
        shading.type = "SOLID"
        shading.color_type = "MATERIAL"
        shading.show_shadows = False
        shading.show_cavity = False
        shading.use_dof = False
        overlay.show_overlays = True
        overlay.show_floor = False
        overlay.show_axis_x = False
        overlay.show_axis_y = False

    elif context.scene.interface.shading == "CLEAN_DELUXE":
        shading.type = "SOLID"
        shading.color_type = "OBJECT"
        shading.show_shadows = True
        shading.show_cavity = True
        shading.cavity_type = "BOTH"
        shading.use_dof = True
        overlay.show_overlays = True
        overlay.show_floor = False
        overlay.show_axis_x = False
        overlay.show_axis_y = False

    elif context.scene.interface.shading == "PREVIEW":
        shading.type = "MATERIAL"
        shading.studio_light = "interior.exr"
        overlay.show_overlays = False

    addon_prefs = context.preferences.addons["bl_ext.user_default.fabex"].preferences
    addon_prefs.default_shading = context.scene.interface.shading
    bpy.ops.wm.save_userpref()


def update_layout(self, context):
    # Layout preset dicts to fill out panel bl_ attributes
    properties = {
        "space": "PROPERTIES",
        "region": "WINDOW",
        "context": "render",
        "category": "",
    }

    sidebar = {
        "space": "VIEW_3D",
        "region": "UI",
        "context": "",
        "category": "CNC",
    }

    tools = {
        "space": "VIEW_3D",
        "region": "TOOLS",
        "context": "objectmode",
        "category": "",
    }

    # Unregister all permanent panels
    try:
        unregister_classes = [
            bpy.types.FABEX_PT_CAM_OPERATION_AREA,
            bpy.types.FABEX_PT_CAM_CHAINS,
            bpy.types.FABEX_PT_CAM_CUTTER,
            bpy.types.FABEX_PT_CAM_FEEDRATE,
            bpy.types.FABEX_PT_CAM_GCODE,
            bpy.types.FABEX_PT_CAM_INFO,
            bpy.types.FABEX_PT_CAM_MACHINE,
            bpy.types.FABEX_PT_CAM_MATERIAL,
            bpy.types.FABEX_PT_CAM_MOVEMENT,
            bpy.types.FABEX_PT_CAM_OPERATION,
            bpy.types.FABEX_PT_CAM_OPERATIONS,
            bpy.types.FABEX_PT_CAM_OPTIMISATION,
            bpy.types.VIEW3D_PT_tools_curvetools,
            bpy.types.VIEW3D_PT_tools_create,
        ]

        for cls in unregister_classes:
            bpy.utils.unregister_class(cls)

    except AttributeError:
        pass

    main_classes = [
        CAM_CHAINS_Panel,
        CAM_OPERATIONS_Panel,
        CAM_MATERIAL_Panel,
        CAM_MACHINE_Panel,
    ]
    operation_classes = [
        CAM_OPERATION_PROPERTIES_Panel,
        CAM_AREA_Panel,
        CAM_CUTTER_Panel,
        CAM_FEEDRATE_Panel,
        CAM_GCODE_Panel,
        CAM_MOVEMENT_Panel,
        CAM_OPTIMISATION_Panel,
    ]
    tools_classes = [
        VIEW3D_PT_tools_curvetools,
        VIEW3D_PT_tools_create,
        CAM_INFO_Panel,
    ]

    # Create 3 empty lists to hold the classes we want to assign to each area
    properties_area_classes = []
    sidebar_area_classes = []
    tools_area_classes = []

    addon_prefs = context.preferences.addons["bl_ext.user_default.fabex"].preferences

    panel_layout = context.scene.interface.layout

    main_location = context.scene.interface.main_location
    operation_location = context.scene.interface.operation_location
    tools_location = context.scene.interface.tools_location

    if panel_layout == "CLASSIC":
        main_location = "PROPERTIES"
        operation_location = "PROPERTIES"
        tools_location = "TOOLS"

    elif panel_layout == "MODERN":
        main_location = "PROPERTIES"
        operation_location = "SIDEBAR"
        tools_location = "TOOLS"

    elif panel_layout == "USER":
        main_location = addon_prefs.user_main_location
        operation_location = addon_prefs.user_operation_location
        tools_location = addon_prefs.user_tools_location

    # Assign Panels to their location
    # Main Panels
    if main_location == "PROPERTIES":
        for cls in main_classes:
            properties_area_classes.append(cls)
    elif main_location == "SIDEBAR":
        for cls in main_classes:
            sidebar_area_classes.append(cls)
    elif main_location == "TOOLS":
        for cls in main_classes:
            tools_area_classes.append(cls)

    # Operation Panels
    if operation_location == "PROPERTIES":
        for cls in operation_classes:
            properties_area_classes.append(cls)
    elif operation_location == "SIDEBAR":
        for cls in operation_classes:
            sidebar_area_classes.append(cls)
    elif operation_location == "TOOLS":
        for cls in operation_classes:
            tools_area_classes.append(cls)

    # Tools Panels
    if tools_location == "PROPERTIES":
        for cls in tools_classes:
            properties_area_classes.append(cls)
    elif tools_location == "SIDEBAR":
        for cls in tools_classes:
            sidebar_area_classes.append(cls)
    elif tools_location == "TOOLS":
        for cls in tools_classes:
            tools_area_classes.append(cls)

    # Re-register the panels in their new areas
    # Properties Area
    for cls in properties_area_classes:
        cls.bl_space_type = properties["space"]
        cls.bl_region_type = properties["region"]
        cls.bl_context = properties["context"]
        cls.bl_category = properties["category"]
        bpy.utils.register_class(cls)

    # Sidebar (N-Panel) Area
    for cls in sidebar_area_classes:
        cls.bl_space_type = sidebar["space"]
        cls.bl_region_type = sidebar["region"]
        cls.bl_context = sidebar["context"]
        cls.bl_category = sidebar["category"]
        bpy.utils.register_class(cls)

    # Tools (T-Panel) Area
    for cls in tools_area_classes:
        cls.bl_space_type = tools["space"]
        cls.bl_region_type = tools["region"]
        cls.bl_context = tools["context"]
        cls.bl_category = tools["category"]
        bpy.utils.register_class(cls)

    # Update Preferences with current settings and save
    addon_prefs.default_layout = panel_layout

    addon_prefs.default_main_location = main_location
    addon_prefs.default_operation_location = operation_location
    addon_prefs.default_tools_location = tools_location

    bpy.ops.wm.save_userpref()


def update_user_layout(self, context):
    # Update the settings for the User layout preset
    main_location = context.scene.interface.main_location
    operation_location = context.scene.interface.operation_location
    tools_location = context.scene.interface.tools_location

    addon_prefs = context.preferences.addons["bl_ext.user_default.fabex"].preferences
    addon_prefs.user_main_location = main_location
    addon_prefs.user_operation_location = operation_location
    addon_prefs.user_tools_location = tools_location

    bpy.ops.wm.save_userpref()


class CAM_INTERFACE_Properties(PropertyGroup):
    level: EnumProperty(
        name="Interface",
        description="Choose visible options",
        items=[
            ("0", "Basic", "Only show essential options", "", 0),
            ("1", "Advanced", "Show advanced options", "", 1),
            ("2", "Complete", "Show all options", "", 2),
            ("3", "Experimental", "Show experimental options", "EXPERIMENTAL", 3),
        ],
        default="0",
        update=update_interface,
    )

    shading: EnumProperty(
        name="Shading",
        description="Choose viewport shading preset",
        items=[
            ("DEFAULT", "Default", "Standard viewport shading"),
            ("DELUXE", "Deluxe", "Cavity, Curvature, Depth of Field, Shadows & Object Colors"),
            ("CLEAN_DEFAULT", "Clean Default", "Standard viewport shading with no overlays"),
            ("CLEAN_DELUXE", "Clean Deluxe", "Deluxe shading with no overlays"),
            ("PREVIEW", "Preview", "HDRI Lighting Preview"),
        ],
        default="DEFAULT",
        update=update_shading,
    )

    layout: EnumProperty(
        name="Layout",
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
        update=update_layout,
    )

    main_location: EnumProperty(
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
        update=update_user_layout,
    )

    operation_location: EnumProperty(
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
        update=update_user_layout,
    )

    tools_location: EnumProperty(
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
        update=update_user_layout,
    )


def draw_interface(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    if context.engine == "FABEX_RENDER":
        col = layout.column()
        col.prop(context.scene.interface, "level")
        col.prop(context.scene.interface, "layout")
        col.prop(context.scene.interface, "shading")
