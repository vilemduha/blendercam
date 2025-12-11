### IDC_90°_¾in_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.75 * correction
d.cutter_flutes = 2
d.cutter_description = 'The Big Stiffy series 90-degree v-bit CNC router bit with 1/4 shank is larger, and cuts deeper, than the typical 90 deg v bit. The extra body size lets you maximize your carve time while also leaving a clean cut.'

d.cutter_tip_angle = 90







            