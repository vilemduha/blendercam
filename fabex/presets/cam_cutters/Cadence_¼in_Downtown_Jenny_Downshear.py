### Cadence_¼in_Downtown_Jenny_Downshear.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Get ready for the “Downtown Jenny” long-lasting 1/4 down-cut bit for your CNC woodworking projects. Revered by expert CNC woodworkers, the 1/4 “Downtown Jenny” is designed for your superior control and refined cuts to achieve professional-grade finishes.'









            