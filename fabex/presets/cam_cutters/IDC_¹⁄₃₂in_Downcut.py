### IDC_¹⁄₃₂in_Downcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.03125 * correction
d.cutter_flutes = 2
d.cutter_description = 'The micro-detail 1/32 down-cutting endmill bit is the CNCers magic to refined CNC router projects. Solid carbide.'









            