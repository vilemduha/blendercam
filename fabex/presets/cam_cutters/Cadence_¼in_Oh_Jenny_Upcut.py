### Cadence_¼in_Oh_Jenny_Upcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Introducing the “Oh, Jenny Up-Cut” extended-life 1/4 up-cut O-Flute bit for your CNC woodworking projects. Revered by CNC woodworking experts, the “Oh, Jenny Up-Cut” is a high-performing O-flute CNC wood bit that delivers a superior finish with every cut.'









            