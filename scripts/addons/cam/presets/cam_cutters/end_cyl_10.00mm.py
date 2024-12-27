import bpy

d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

d.cutter_type = "END"
d.cutter_diameter = 0.010
d.cutter_length = 25.0
d.cutter_tip_angle = 60.0
