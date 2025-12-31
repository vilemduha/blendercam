### IDC_Extended_⅛in_Downcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'This long 1/8 CNC router bit gives you more creative ability to design and cut thicker projects you otherwise couldnt do. And you can design with more detail due to the smaller bit diameter. Think keepsake boxes and Aztec calendars with much more detail and depth!'









            