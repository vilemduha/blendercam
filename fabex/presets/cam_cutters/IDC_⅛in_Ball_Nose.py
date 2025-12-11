### IDC_⅛in_Ball_Nose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'This “Straight 8” 1/8 solid carbide ball-nose endmill bit is your alternate 3D carving bit when you want speed in your CNC router project.'









            