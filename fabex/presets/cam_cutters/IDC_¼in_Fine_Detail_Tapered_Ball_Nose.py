### IDC_¼in_Fine_Detail_Tapered_Ball_Nose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'This bit is excellent for almost any size 3D carve. The benefit…it saves time while still holding great detail in your CNC woodworking 3D projects.  The taper ball nose endmill is the most common router bit for CNC routers when designing finely detailed 3D carvings on your CNC router.'

d.cutter_tip_angle = 20



d.ball_radius = 0.045 * correction



            