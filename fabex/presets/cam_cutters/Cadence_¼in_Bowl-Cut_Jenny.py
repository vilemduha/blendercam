### Cadence_¼in_Bowl-Cut_Jenny.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BULLNOSE'
d.cutter_diameter = 0.5 * correction
d.cutter_flutes = 2
d.cutter_description = 'Experience the “Bowl Cut Jenny” professional-grade 1/2 bowl and tray up-cut bit for CNC routers. Favored among CNC woodworkers, the “Bowl Cut Jenny” is designed to achieve precise cuts and smoothly contoured profiles at higher feed rates for enhanced productivity. '







d.bull_corner_radius = 0.1875 * correction

            