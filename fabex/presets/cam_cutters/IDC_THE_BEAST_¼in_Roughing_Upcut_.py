### IDC_THE_BEAST_¼in_Roughing_Upcut_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 3
d.cutter_description = 'If youre tired of spending hours while you wait on your CNC router to remove material from your CNC woodworking projects, then youve come to the right bit.  Welcome to the aptly nicknamed BEAST, a 1/4 hyper-speed CNC router bit from IDC Woodcraft, the ultimate solution for lightning-fast material removal.'









            