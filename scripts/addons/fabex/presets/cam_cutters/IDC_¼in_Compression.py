### IDC_¼in_Compression.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 1/4 compression endmill bit is a unique bit for CNC routers. It allows you to cut out your project while leaving both the top and bottom edges of your project clean (eliminates tear-out).'









            