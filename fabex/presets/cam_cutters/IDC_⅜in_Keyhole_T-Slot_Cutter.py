### IDC_⅜in_Keyhole_T-Slot_Cutter.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.375 * correction
d.cutter_flutes = 2
d.cutter_description = 'This keyhole t-slot cutter is designed for deeper slot depths when your wall-hanging wood projects are extra heavy. Keyhole t-slot cutters for CNC routers are used to cut slots in wood projects when you want them to be flush to the wall.'









            