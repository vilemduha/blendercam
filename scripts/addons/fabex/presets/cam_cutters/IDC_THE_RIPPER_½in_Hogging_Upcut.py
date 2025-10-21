### IDC_THE_RIPPER_½in_Hogging_Upcut.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.5 * correction
d.cutter_flutes = 3
d.cutter_description = 'Introducing the 1/2 RIPPER Roughing CNC Router Bit by IDC Woodcraft – Built for Professional CNC woodworkers and CNC routers!   Unlock unprecedented levels of productivity. This 1/2 RIPPER Roughing CNC Router Bit is the ultimate tool for serious CNC woodworking and industrial power users who want speed.'









            