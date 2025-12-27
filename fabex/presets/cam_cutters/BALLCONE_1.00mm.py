import bpy

d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

d.cutter_type = "BALLCONE"
d.ball_radius = 0.001
d.ball_cone_flute = 0.03
d.cutter_diameter = 0.006
d.cutter_length = 25.0
d.cutter_tip_angle = 60.0
