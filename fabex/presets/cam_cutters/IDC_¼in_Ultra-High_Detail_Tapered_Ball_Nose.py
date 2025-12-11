### IDC_¼in_Ultra-High_Detail_Tapered_Ball_Nose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Get extremely fine detail in your amazing 3D carves with this taper ball nose endmill router bit for CNC routers. It is designed to give you extremely fine detailed carvings on your CNC router.'

d.cutter_tip_angle = 20



d.ball_radius = 0.015 * correction



            