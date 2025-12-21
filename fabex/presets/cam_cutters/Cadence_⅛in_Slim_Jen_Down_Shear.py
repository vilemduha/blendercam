### Cadence_⅛in_Slim_Jen_Down_Shear.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.125 * correction
d.cutter_flutes = 2
d.cutter_description = 'Announcing the “Slim Jen” extended-wear 1/8 down cut bit (a.k.a. down bit, down cut bit, down shear bit) for your CNC woodworking projects. Expertly designed for CNC woodworking pros, the “Slim Jen” reduces splintering to achieve your professional-grade finishes every time.'









            