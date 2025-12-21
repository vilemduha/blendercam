### IDC_⅛in_Downcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 1/8 down bit is the 2nd workhorse of CNC router bits (just behind the 1/4) This will be your go-to bit to hit the stuff a 1/4 cant reach. '









            