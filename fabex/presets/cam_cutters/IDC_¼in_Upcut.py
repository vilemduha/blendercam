### IDC_¼in_Upcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 1/4 up bit, the hog-it-out machine of CNC router bits! This is your first go-to bit with your CNC router when you want to just get material out of the way'









            