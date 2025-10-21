### Cadence_¼in_GrooVee_30°_VBit.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Discover the “30-Degree GrooVee Jenny” long-lasting 1/4 30-degree down-cut V-bit for CNC routers. Crafted for skilled CNC woodworking masters like you, the “30-Degree GrooVee Jenny” is the worlds first 30-degree V-bit designed for longevity and unmatched performance.'

d.cutter_tip_angle = 30







            