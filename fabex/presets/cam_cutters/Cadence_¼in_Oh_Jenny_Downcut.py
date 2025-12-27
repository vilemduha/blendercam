### Cadence_¼in_Oh_Jenny_Downcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Meet the “Oh, Jenny Down-Cut” heavy-duty 1/4 down-cut O-Flute bit for your CNC woodworking projects. Praised by CNC woodworking professionals, the high-performance “Oh, Jenny Down-Cut” maintains professional-grade cutting precision, better chip control, and greater stability.'









            