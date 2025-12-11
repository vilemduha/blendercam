### IDC_⅛in_Acrylic_O_Flute.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 1
d.cutter_description = 'This is your 1/8 bit to create those amazing LED-lit acrylic projects youve been wanting to make. Get the fine detail with this smaller bit so that sign really stands out. '









            