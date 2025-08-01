### Cadence_¼in_The_Jenny_Compression.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Introducing the “Jenny” premium 1/4 compression bit designed for CNC woodworkers. A staple in any CNC woodworking shop, the “Jenny” offers precision cutting performance over an extended life cycle.'









            