### IDC_¼in_Downcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 1/4 down bit, the workhorse of CNC router bits! This will be your first go-to bit with your CNC router. You will want to make sure its a good one.'









            