### IDC_Widget_Works_Diamond_Engraver.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'VCARVE'
d.cutter_diameter = 0.5 * correction
d.cutter_flutes = 1
d.cutter_description = 'Create stunningly precise detailed engravings with the Widgetworks diamond drag engraving bit on multiple materials, including plastics (like acrylic), brass, aluminum, steel, glass, and even granite.'

d.cutter_tip_angle = 120







            