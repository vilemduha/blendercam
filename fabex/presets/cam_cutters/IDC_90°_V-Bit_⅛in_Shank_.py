### IDC_90°_V-Bit_⅛in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 1
d.cutter_description = 'Made of micro-grain carbide steel, this series of bits are designed to cut your carves cleanly and hold up for a much longer over regular 1/8 shank v-bits.  90 degree v-bit – Your go-to v-bit for most v-carvings'

d.cutter_tip_angle = 90







            