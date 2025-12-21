### IDC_60°_¾in_V-Bit_¼in_Shank_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.75 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 60 degree v bit ‘Super Shear for CNC routers is the bit when speed matters as much as the carving quality. This 60 degree bit is part of the Big Stiffy series, a set of bits designed to virtually eliminate uneven carves due to chatter. '

d.cutter_tip_angle = 60







            