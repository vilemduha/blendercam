### IDC_1in_Ball_Nose_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 1 * correction
d.cutter_flutes = 2
d.cutter_description = 'Affectionately named “Big Balls” by other CNCers, the Big Stiffy series 1/2 radius ball nose bit (1 inch diameter) for CNC routers (also known as a “bull nose”) is for bigger radius accent work when you want your job done fast and clean.'









            