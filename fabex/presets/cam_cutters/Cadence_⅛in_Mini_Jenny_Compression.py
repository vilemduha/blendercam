### Cadence_⅛in_Mini_Jenny_Compression.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'Welcome to the “Mini Jenny” extreme-duty 1/8 compression bit for CNC routers. Favored by professional CNC woodworkers, the “Mini Jenny” is designed to give you an extra-long life cycle while maintaining clean, precise cuts over its entire working life. '









            