### IDC_¹⁄₁₆in_Acrylic_O_Flute.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.0625 * correction
d.cutter_flutes = 1
d.cutter_description = 'This is your 1/16 O-flute bit to add the amazingly fine details to your LED-lit acrylic projects youll be making on your CNC router. Get the fine detail with this smaller bit so that sign really stands out.'









            