"""Fabex 'preset_managers.py'

Operators and Menus for CAM Machine, Cutter and Operation Presets.
"""

import bpy
from bl_operators.presets import AddPresetBase
from bpy.types import (
    Menu,
    Operator,
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


class AddPresetCamCutter(AddPresetBase, Operator):
    """Add a Cutter Preset"""

    bl_idname = "render.cam_preset_cutter_add"
    bl_label = "Add Cutter Preset"
    preset_menu = "CAM_CUTTER_MT_presets"

    preset_defines = [
        "d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"
    ]

    preset_values = [
        "d.cutter_id",
        "d.cutter_type",
        "d.cutter_diameter",
        "d.cutter_length",
        "d.cutter_flutes",
        "d.cutter_tip_angle",
        "d.cutter_description",
    ]

    preset_subdir = "cam_cutters"


class AddPresetCamOperation(AddPresetBase, Operator):
    """Add an Operation Preset"""

    bl_idname = "render.cam_preset_operation_add"
    bl_label = "Add Operation Preset"
    preset_menu = "CAM_OPERATION_MT_presets"

    preset_defines = [
        "from pathlib import Path",
        "bpy.ops.scene.cam_operation_add()",
        "scene = bpy.context.scene",
        "o = scene.cam_operations[scene.cam_active_operation]",
        "o.name = f'OP_{o.object_name}_{scene.cam_active_operation + 1}_{Path(__file__).stem}'",
    ]

    preset_values = [
        "o.info.duration",
        "o.info.chipload",
        "o.info.warnings",
        "o.material.estimate_from_model",
        "o.material.size",
        "o.material.radius_around_model",
        "o.material.origin",
        "o.movement.stay_low",
        "o.movement.free_height",
        "o.movement.insideout",
        "o.movement.spindle_rotation",
        "o.movement.type",
        "o.movement.useG64",
        "o.movement.G64",
        "o.movement.parallel_step_back",
        "o.movement.protect_vertical",
        "o.source_image_name",
        "o.source_image_offset",
        "o.source_image_size_x",
        "o.source_image_crop",
        "o.source_image_crop_start_x",
        "o.source_image_crop_start_y",
        "o.source_image_crop_end_x",
        "o.source_image_crop_end_y",
        "o.source_image_scale_z",
        "o.optimisation.optimize",
        "o.optimisation.optimize_threshold",
        "o.optimisation.use_exact",
        "o.optimisation.exact_subdivide_edges",
        "o.optimisation.simulation_detail",
        "o.optimisation.pixsize",
        "o.optimisation.circle_detail",
        "o.cut_type",
        "o.cutter_tip_angle",
        "o.cutter_id",
        "o.cutter_diameter",
        "o.cutter_type",
        "o.cutter_flutes",
        "o.cutter_length",
        "o.ambient_behaviour",
        "o.ambient_radius",
        "o.curve_object",
        "o.curve_object1",
        "o.limit_curve",
        "o.use_limit_curve",
        "o.feedrate",
        "o.plunge_feedrate",
        "o.dist_along_paths",
        "o.dist_between_paths",
        "o.max",
        "o.min",
        "o.minz_from",
        "o.minz",
        "o.skin",
        "o.spindle_rpm",
        "o.use_layers",
        "o.carve_depth",
        "o.update_offsetimage_tag",
        "o.slice_detail",
        "o.drill_type",
        "o.dont_merge",
        "o.update_silhouete_tag",
        "o.inverse",
        "o.waterline_fill",
        "o.strategy",
        "o.update_zbufferimage_tag",
        "o.stepdown",
        "o.path_object_name",
        "o.pencil_threshold",
        "o.geometry_source",
        "o.object_name",
        "o.parallel_angle",
        "o.output_header",
        "o.gcode_header",
        "o.output_trailer",
        "o.gcode_trailer",
        "o.use_modifiers",
        "o.enable_A",
        "o.enable_B",
        "o.A_along_x",
        "o.rotation_A",
        "o.rotation_B",
        "o.straight",
    ]

    preset_subdir = "cam_operations"


class AddPresetCamMachine(AddPresetBase, Operator):
    """Add a Cam Machine Preset"""

    bl_idname = "render.cam_preset_machine_add"
    bl_label = "Add Machine Preset"
    preset_menu = "CAM_MACHINE_MT_presets"

    preset_defines = ["d = bpy.context.scene.cam_machine", "s = bpy.context.scene.unit_settings"]
    preset_values = [
        "d.post_processor",
        "s.system",
        "d.use_position_definitions",
        "d.starting_position",
        "d.mtc_position",
        "d.ending_position",
        "d.working_area",
        "d.feedrate_min",
        "d.feedrate_max",
        "d.feedrate_default",
        "d.spindle_min",
        "d.spindle_max",
        "d.spindle_default",
        "d.axis4",
        "d.axis5",
        "d.collet_size",
        "d.output_tool_change",
        "d.output_block_numbers",
        "d.output_tool_definitions",
        "d.output_g43_on_tool_change",
    ]

    preset_subdir = "cam_machines"
