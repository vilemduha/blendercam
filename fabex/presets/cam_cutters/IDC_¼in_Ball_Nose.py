### IDC_¼in_Ball_Nose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'The bit most CNCers forget about…This 1/4 ball-nose endmill bit is the bit to use to ‘soften down those features that look too sharp on your CNC router projects.'









            