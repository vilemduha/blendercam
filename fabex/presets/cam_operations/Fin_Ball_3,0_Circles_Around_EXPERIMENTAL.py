from pathlib import Path

import bpy

bpy.ops.scene.cam_operation_add()

scene = bpy.context.scene
o = scene.cam_operations[scene.cam_active_operation]
o.strategy = "CIRCLES"

o.ambient_behaviour = "AROUND"
o.ambient_radius = 0.01
o.carve_depth = 0.001
o.optimisation.circle_detail = 64
o.curve_source = ""
o.cut_type = "OUTSIDE"
o.cutter_diameter = 0.003
o.cutter_length = 25.0
o.cutter_tip_angle = 60.0
o.cutter_type = "BALLNOSE"
o.distance_along_paths = 0.0002
o.distance_between_paths = 0.00015
o.dont_merge = False
o.feedrate = scene.cam_machine.feedrate_max or 3.0
o.filename = o.name = f"{scene.cam_names.operation_name_full}_{Path(__file__).stem}"
o.movement.free_height = 0.01
o.geometry_source = "OBJECT"
o.inverse = False
o.limit_curve = None
o.material.estimate_from_model = True
o.material.origin = (0.0, 0.0, 0.0)
o.material.radius_around_model = 0.003
o.material.size = (0.2, 0.2, 0.1)
o.min_z = -0.128119
o.movement.type = "MEANDER"
o.optimisation.optimize = True
o.optimisation.optimize_threshold = 5e-05
o.parallel_angle = 0.0
o.optimisation.pixsize = 0.0001
o.plunge_feedrate = 30.0
o.movement.protect_vertical = True
o.skin = 0.0
o.slice_detail = 0.001
o.source_image_name = ""
o.source_image_offset = (0.0, 0.0, 0.0)
o.source_image_scale_z = 1.0
o.source_image_size_x = 0.1
o.movement.stay_low = True
o.stepdown = 0.01
o.update_offset_image_tag = False
o.update_silhouette_tag = True
o.update_z_buffer_image_tag = False
o.use_layers = False
o.use_limit_curve = False
o.waterline_fill = True
