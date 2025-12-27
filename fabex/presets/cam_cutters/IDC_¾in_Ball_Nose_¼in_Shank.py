### IDC_¾in_Ball_Nose_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.75 * correction
d.cutter_flutes = 2
d.cutter_description = 'This Big Stiffy series 3/4 ball nose router bit (3/8 inch cutting radius) for CNC routers is your all-purpose accent bit. And it is excellent for broader juice grooves on larger cutting boards.'









            