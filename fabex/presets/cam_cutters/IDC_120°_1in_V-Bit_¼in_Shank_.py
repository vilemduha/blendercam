### IDC_120°_1in_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 1 * correction
d.cutter_flutes = 2
d.cutter_description = 'The Big Stiffy series 120-degree v-bit for CNC routers is the bit to use when you want wider, shallower cuts, and get your job done fast and clean. With a 1/4 shank, it is the go-to v carving bit for home-based CNCers when it comes to larger projects. '

d.cutter_tip_angle = 120







            