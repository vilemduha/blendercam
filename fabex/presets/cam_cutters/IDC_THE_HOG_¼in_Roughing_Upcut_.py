### IDC_THE_HOG_¼in_Roughing_Upcut_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 3
d.cutter_description = 'The 1/4 roughing endmill bit (hogging bit) is the bit when you need to remove massive amounts of material at one time from your CNC router project before you do your finish cuts.'









            