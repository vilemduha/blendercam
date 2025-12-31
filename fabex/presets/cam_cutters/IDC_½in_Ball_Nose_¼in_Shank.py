### IDC_½in_Ball_Nose_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.5 * correction
d.cutter_flutes = 2
d.cutter_description = 'This Big Stiffy series 1/4 radius ball nose bit (1/2 inch diameter) for CNC routers is excellent for juice grooves on cutting boards. Also great for radius accent work when carving signs on your CNC router'









            