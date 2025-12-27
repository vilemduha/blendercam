### Cadence_¼in_GrooVee_60°_VBit.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.375 * correction
d.cutter_flutes = 2
d.cutter_description = 'Discover the “60-Degree GrooVee Jenny” extended-life 3/8 60-degree down-cut V-bit for your CNC woodworking projects. Favored by seasoned CNC woodworking pros, the “60-Degree GrooVee Jenny” is the worlds first 60-degree V-bit that offers exceptional performance matched only by an extended tool lifecycle.'

d.cutter_tip_angle = 60







            