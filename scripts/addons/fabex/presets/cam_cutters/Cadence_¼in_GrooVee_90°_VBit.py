### Cadence_¼in_GrooVee_90°_VBit.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.375 * correction
d.cutter_flutes = 2
d.cutter_description = 'Behold the “90-Degree GrooVee Jenny” high-performance 3/8 90-degree down-cut V-bit for CNC woodworking routers. Preferred by CNC woodworking experts, the “90-Degree GrooVee Jenny” is the worlds first 90-degree V-bit optimized for premium performance and faster project completion.'

d.cutter_tip_angle = 90







            