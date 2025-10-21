### Cadence_Big_B_Jenny_Ballnose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Discover the “Big B Jenny” high-endurance 1/4 ball nose end mill for your CNC woodworking projects. Widely acclaimed by seasoned CNC woodworking professionals, the “Big B Jenny” is designed for smooth, precise curves and is well-suited to intricate detail work on your projects.'









            