"""Fabex '__init__.py' © 2012 Vilem Novak

Import Modules, Register and Unregister  Classes
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
from .operators import (
    register as ops_register,
    unregister as ops_unregister,
)
from .properties import (
    register as props_register,
    unregister as props_unregister,
)
from .properties.operation_props import CAM_OPERATION_Properties
from .preferences import CamAddonPreferences
from .ui import (
    register as ui_register,
    unregister as ui_unregister,
)
from .utilities.addon_utils import (
    on_blender_startup,
    keymap_register,
    keymap_unregister,
    on_engine_change,
)
from .utilities.thread_utils import timer_update

classes = (
    FABEX_ENGINE,
    CamAddonPreferences,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    props_register()
    ops_register()
    ui_register()
    keymap_register()

    # CAM_OPERATION_Properties - last to allow dependencies to register before it
    bpy.utils.register_class(CAM_OPERATION_Properties)

    bpy.types.Scene.cam_operations = CollectionProperty(type=CAM_OPERATION_Properties)

    bpy.types.Scene.engine_check = object()

    subscribe_to = bpy.types.RenderSettings, "engine"

    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=bpy.types.Scene.engine_check,
        args=(),
        notify=on_engine_change,
    )

    for panel in get_panels():
        panel.COMPAT_ENGINES.add("FABEX_RENDER")

    bpy.app.handlers.frame_change_pre.append(timer_update)
    bpy.app.handlers.load_post.append(on_blender_startup)


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)

    ui_unregister()
    ops_unregister()
    props_unregister()
    keymap_unregister()

    bpy.utils.unregister_class(CAM_OPERATION_Properties)

    del bpy.types.Scene.cam_operations

    for panel in get_panels():
        if "FABEX_RENDER" in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove("FABEX_RENDER")
