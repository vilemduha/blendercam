### IDC_60°_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'The Blade series v-bits are excellent for inlay work. This 60-degree v-bit (1/4 shank) for CNC routers is designed to leave an ultra-smooth cut so your CNC woodworking projects look awesome right off the machine.'

d.cutter_tip_angle = 60







            