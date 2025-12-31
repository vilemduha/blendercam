### IDC_Long_¼in_Downcut_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'This long 1/4 CNC router bit gives you a full 1-3/4 cut! Great for guitar bodies, keepsake boxes, and unusually thick CNC router wood projects, such as deep 3D carvings or recessed work. '









            