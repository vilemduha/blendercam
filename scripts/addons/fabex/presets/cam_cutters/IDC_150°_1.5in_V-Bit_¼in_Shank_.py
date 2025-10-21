### IDC_150°_1.5in_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 1.5 * correction
d.cutter_flutes = 2
d.cutter_description = '150 degree v grooving bit is perfect for the CNCer who want to make a pizza peel and v-carved signs that need to be seen. It is the perfect shape to cut the taper on your pizza peel.'

d.cutter_tip_angle = 150







            