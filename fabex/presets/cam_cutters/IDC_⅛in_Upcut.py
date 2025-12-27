### IDC_⅛in_Upcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'The 1/8 up cutting drilling endmill CNC router bit is designed with a special double-bevel tip that allows for drilling, as well as side cutting. The fast spiral classifies it as a fast-action bit, designed to remove a lot of material at high speeds.'









            