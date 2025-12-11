### IDC_1in_Surfacing_Bit_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 1 * correction
d.cutter_flutes = 4
d.cutter_description = 'This ultra-smooth cutting 1 inch surfacing bit is built for higher performance than the standard 3-flute 1 surfacing bit you commonly find. Used in your CNC router to surface or flatten your CNC router spoilboard, as well as slab flattening.'









            