"""Fabex 'preset_menus.py'

Operators and Menus for CAM Machine, Cutter and Operation Presets.
"""

import bpy
from bpy.types import (
    Menu,
)


class CAM_CUTTER_MT_presets(Menu):
    bl_label = "Cutter Presets"
    preset_subdir = "cam_cutters"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class CAM_OPERATION_MT_presets(Menu):
    bl_label = "Operation Presets"
    preset_subdir = "cam_operations"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class CAM_MACHINE_MT_presets(Menu):
    bl_label = "Machine Presets"
    preset_subdir = "cam_machines"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset

    @classmethod
    def post_cb(cls, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        name = cls.bl_label
        filepath = bpy.utils.preset_find(name, cls.preset_subdir, display_name=True, ext=".py")
        addon_prefs.default_machine_preset = filepath
        bpy.ops.wm.save_userpref()
