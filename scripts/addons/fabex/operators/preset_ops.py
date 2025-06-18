"""Fabex 'preset_managers.py'

Operators and Menus for CAM Machine, Cutter and Operation Presets.
"""

import bpy
from bl_operators.presets import AddPresetBase
from bpy.types import (
    Operator,
)


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
        "o.curve_source",
        "o.curve_target",
        "o.limit_curve",
        "o.use_limit_curve",
        "o.feedrate",
        "o.plunge_feedrate",
        "o.distance_along_paths",
        "o.distance_between_paths",
        "o.max",
        "o.min",
        "o.min_z_from",
        "o.min_z",
        "o.skin",
        "o.spindle_rpm",
        "o.use_layers",
        "o.carve_depth",
        "o.update_offset_image_tag",
        "o.slice_detail",
        "o.drill_type",
        "o.dont_merge",
        "o.update_silhouette_tag",
        "o.inverse",
        "o.waterline_fill",
        "o.strategy",
        "o.update_z_buffer_image_tag",
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
        "o.enable_a_axis",
        "o.enable_b_axis",
        "o.a_along_x",
        "o.rotation_a",
        "o.rotation_b",
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
        "s.length_unit",
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
        "d.axis_4",
        "d.axis_5",
        "d.collet_size",
        "d.output_tool_change",
        "d.output_block_numbers",
        "d.output_tool_definitions",
        "d.output_G43_on_tool_change",
    ]

    preset_subdir = "cam_machines"
