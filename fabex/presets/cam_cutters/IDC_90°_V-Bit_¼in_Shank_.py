### IDC_90°_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'The only 90-degree v-bit with a knife-edge actually cuts instead of scraping material away. The 90-degree next-generation “Blade” design leaves superior v grooves that virtually ends post-sanding of your v-cuts.'

d.cutter_tip_angle = 90







            