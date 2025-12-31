### IDC_⅛in_Compression.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 1/8 compression endmill bit (also known as an up/down bit) is a unique bit for CNC routers. It allows you to cut finer details and will perfectly cut out your project while leaving both the top and bottom edges of your project clean (eliminates tear-out on top and bottom).'









            