### Cadence_¼in_Uptown_Jenny_Downshear.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Meet the “Uptown Jenny” a precision-engineered 1/4 up-cut bit for your CNC woodworking projects. Trusted by CNC woodworking hobbyists and professionals, the “Uptown Jenny” is designed for all your high-performance woodworking applications that require efficient chip evacuation and splinter-free cuts.'









            