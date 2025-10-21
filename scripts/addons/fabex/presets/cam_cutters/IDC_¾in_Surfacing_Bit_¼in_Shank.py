### IDC_¾in_Surfacing_Bit_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.75 * correction
d.cutter_flutes = 4
d.cutter_description = 'This 3/4-inch surfacing bit, for 1/8 collet CNC routers, is designed for use in desktop CNC routers and is used to surface or flatten your raw wood, or flatten your CNC router spoilboard (also called a spoiler board, or waste board), as well as slab flattening.'









            