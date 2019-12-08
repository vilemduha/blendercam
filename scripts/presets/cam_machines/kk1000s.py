import bpy
d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

d.exporter = 'MACH3'
s.system = 'METRIC'
d.working_area = (0.800000011920929, 0.5600000023841858, 0.09000000357627869)
d.feedrate_min = 9.999999747378752e-06
d.feedrate_max = 2.0
d.feedrate_default = 1.5
d.spindle_min = 5000.0
d.spindle_max = 25000.0
d.spindle_default = 20000.0
d.axis4 = False
d.axis5 = False
d.collet_size = 0.0
