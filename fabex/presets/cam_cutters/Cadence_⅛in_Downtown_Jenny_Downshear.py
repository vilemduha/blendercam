### Cadence_⅛in_Downtown_Jenny_Downshear.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'Say hello to the “Downtown Jenny”, an 1/8 heavy-duty down-cut bit for your CNC router. Trusted by CNC woodworking professionals, the 1/8 “Downtown Jenny” is designed for your shallow cuts on a mix of hard and softwoods.'









            