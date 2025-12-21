### Cadence_Skinny_Jenny.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLCONE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Experience the “Skinny Jenny” top-tier 1/16” tapered ball nose endmill for your CNC routers. Preferred by CNC woodworking masters, the “Skinny Jenny” is designed to maximize your cutting precision and performance while minimizing your tool deflection, chatter, and wear.'

d.cutter_tip_angle = 10







            