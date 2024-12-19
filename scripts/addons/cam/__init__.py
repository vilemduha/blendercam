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
from bpy.props import CollectionProperty

# Relative Imports - from 'cam' module
from .engine import (
    FABEX_ENGINE,
    get_panels,
)
from .operators import register as ops_register, unregister as ops_unregister
from .properties import register as props_register, unregister as props_unregister
from .properties.operation_props import CAM_OPERATION_Properties
from .preferences import CamAddonPreferences
from .ui import register as ui_register, unregister as ui_unregister
from .utilities.addon_utils import check_operations_on_load
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

    # CAM_OPERATION_Properties - last to allow dependencies to register before it
    bpy.utils.register_class(CAM_OPERATION_Properties)

    bpy.app.handlers.frame_change_pre.append(timer_update)
    bpy.app.handlers.load_post.append(check_operations_on_load)

    scene = bpy.types.Scene
    scene.cam_operations = CollectionProperty(
        type=CAM_OPERATION_Properties,
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
    del scene.cam_operations

    for panel in get_panels():
        if "FABEX_RENDER" in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove("FABEX_RENDER")

    wm = bpy.context.window_manager
    active_kc = wm.keyconfigs.active

    for key in active_kc.keymaps["Object Mode"].keymap_items:
        if key.idname == "wm.call_menu" and key.properties.name == "VIEW3D_MT_PIE_CAM":
            active_kc.keymaps["Object Mode"].keymap_items.remove(key)
