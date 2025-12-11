### IDC_¼in_Acrylic_O_Flute.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'END'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 1
d.cutter_description = 'Your 1/4 0-flute bit is here! 0-flute bits are the go-to bits for all things acrylic and HDPE with CNC routers. If you havent created LED-lit acrylic projects, its definitely time.'









            