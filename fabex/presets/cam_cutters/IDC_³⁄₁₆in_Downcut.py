### IDC_³⁄₁₆in_Downcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.1875 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 3/16 CNC router bit… The Silver Bullet of CNC router bits. Thats because its used to do both 1/8 and 1/4 work, saving the need for 2 different size bits.'









            