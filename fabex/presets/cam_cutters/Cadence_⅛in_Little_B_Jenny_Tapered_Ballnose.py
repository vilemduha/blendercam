### Cadence_⅛in_Little_B_Jenny_Tapered_Ballnose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Get to know the “Little B Jenny” high-performance 1/8 tapered ball nose endmill for CNC routers. Favored by CNC woodworking professionals like you, the “Little B Jenny” boasts increased rigidity for your finer woodworking features and precision work.'

d.cutter_tip_angle = 6.8



d.ball_radius = 0.0625 * correction



            