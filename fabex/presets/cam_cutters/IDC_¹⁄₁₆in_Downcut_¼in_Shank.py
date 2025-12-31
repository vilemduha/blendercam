### IDC_¹⁄₁₆in_Downcut_¼in_Shank.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.0625 * correction
d.cutter_flutes = 2
d.cutter_description = 'The CNCers seriously fine-detail 1/16 down-cutting endmill bit with a 1/4 shank is the Lets get some detail in this puppy type of bit for your CNC router projects.'









            