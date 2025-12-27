### IDC_¼in_Downcut_Ballnose.py ###

import bpy
d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

correction = 0.0254

d.cutter_type = 'BALLNOSE'
d.cutter_diameter = 0.25 * correction
d.cutter_flutes = 2
d.cutter_description = 'Great for starting out with the first pass of a 3D carving project, this 1/4 downcut ball nose combines a ball nose and a downcut to give you a perfect finish while minimizing tearout.'









            