### Cadence_¼in_Uptown_Jenny_Extended_Reach_Upcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Welcome the “Uptown Jenny” professional-grade 1/4 Extended Reach up-cut bit for your CNC woodworking projects. Designed for expert CNC woodworkers in mind, the extended-reach “Uptown Jenny” delivers the same high-quality performance as the standard 1/4 “Uptown Jenny” but with greater tool length tailored to your needs.'









            