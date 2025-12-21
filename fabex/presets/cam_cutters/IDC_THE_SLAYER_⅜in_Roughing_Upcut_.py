### IDC_THE_SLAYER_⅜in_Roughing_Upcut_.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.375 * correction
d.cutter_flutes = 3
d.cutter_description = 'This bit unlocks unprecedented levels of productivity. The SLAYER is designed to remove material up to 8 times faster than your standard endmills. This is the ultimate tool for serious CNC woodworking and industrial power users who want speed.  Nicknamed the Slayer at IDC Woodcraft, this roughing router bit dominates in efficiency and durability, making it perfect for high-volume, and large-scale CNC router woodworking projects where performance and speed are paramount.'









            