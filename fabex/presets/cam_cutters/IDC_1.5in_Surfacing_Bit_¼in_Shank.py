### IDC_1.5in_Surfacing_Bit_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 1.5 * correction
d.cutter_flutes = 4
d.cutter_description = 'This 1-1/2 inch surfacing bit, designed for super-smooth cuts, is used in your CNC router to surface or flatten your CNC router spoilboard (also called a spoiler board, or waste board), as well as slab flattening, and prepping your CNC router project surfaces.'









            