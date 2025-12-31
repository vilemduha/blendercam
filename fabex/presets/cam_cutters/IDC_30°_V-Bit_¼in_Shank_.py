### IDC_30°_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 1
d.cutter_description = 'This is the best CNC router bit for wood when it comes to carving. The 30-degree next-generation “Blade” design actually carves the material, not scrape it like standard v-bits.'

d.cutter_tip_angle = 30







            