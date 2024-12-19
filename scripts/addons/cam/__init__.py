"""Fabex '__init__.py' © 2012 Vilem Novak

Import Modules, Register and Unregister Classes
"""

# Python Standard Library
import subprocess
import sys

# pip Wheels
import shapely
import opencamlib

# Blender Library
import bpy
from bpy.props import (
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

# Relative Imports - from 'cam' module
from .engine import (
    FABEX_ENGINE,
    get_panels,
)

from .operators import register as ops_register, unregister as ops_unregister

from .properties import register as props_register, unregister as props_unregister
from .properties.chain_props import CAM_CHAIN_Properties
from .properties.machine_props import CAM_MACHINE_Properties
from .properties.operation_props import CAM_OPERATION_Properties

from .preferences import CamAddonPreferences

from .ui import register as ui_register, unregister as ui_unregister
from .ui.panels.interface import CAM_INTERFACE_Properties

from .utilities.addon_utils import check_operations_on_load
from .utilities.operation_utils import update_operation
from .utilities.thread_utils import timer_update

classes = (
    # .engine
    FABEX_ENGINE,
    # .preferences
    CamAddonPreferences,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    props_register()
    ops_register()
    ui_register()

    # .cam_operation - last to allow dependencies to register before it
    bpy.utils.register_class(CAM_OPERATION_Properties)

    bpy.app.handlers.frame_change_pre.append(timer_update)
    bpy.app.handlers.load_post.append(check_operations_on_load)
    # bpy.types.INFO_HT_header.append(header_info)

    scene = bpy.types.Scene

    scene.cam_active_chain = IntProperty(
        name="CAM Active Chain",
        description="The selected chain",
    )
    scene.cam_active_operation = IntProperty(
        name="CAM Active Operation",
        description="The selected operation",
        update=update_operation,
    )
    scene.cam_chains = CollectionProperty(
        type=CAM_CHAIN_Properties,
    )
    scene.gcode_output_type = StringProperty(
        name="Gcode Output Type",
        default="",
    )
    scene.cam_machine = PointerProperty(
        type=CAM_MACHINE_Properties,
    )
    scene.cam_operations = CollectionProperty(
        type=CAM_OPERATION_Properties,
    )
    scene.cam_text = StringProperty()
    scene.interface = PointerProperty(
        type=CAM_INTERFACE_Properties,
    )

    for panel in get_panels():
        panel.COMPAT_ENGINES.add("FABEX_RENDER")

    wm = bpy.context.window_manager
    addon_kc = wm.keyconfigs.addon

    km = addon_kc.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new(
        "wm.call_menu_pie",
        "C",
        "PRESS",
        alt=True,
    )
    kmi.properties.name = "VIEW3D_MT_PIE_CAM"
    kmi.active = True


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)

    ui_unregister()
    ops_unregister()
    props_unregister()

    bpy.utils.unregister_class(CAM_OPERATION_Properties)

    scene = bpy.types.Scene

    # cam chains are defined hardly now.
    del scene.cam_chains
    del scene.cam_active_chain
    del scene.cam_operations
    del scene.cam_active_operation
    del scene.cam_machine
    del scene.gcode_output_type
    del scene.cam_text

    for panel in get_panels():
        if "FABEX_RENDER" in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove("FABEX_RENDER")

    wm = bpy.context.window_manager
    active_kc = wm.keyconfigs.active

    for key in active_kc.keymaps["Object Mode"].keymap_items:
        if key.idname == "wm.call_menu" and key.properties.name == "VIEW3D_MT_PIE_CAM":
            active_kc.keymaps["Object Mode"].keymap_items.remove(key)
