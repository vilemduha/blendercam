import bpy

d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

d.post_processor = "GRBL"
s.system = "METRIC"
d.use_position_definitions = False
d.starting_position = (0.0, 0.0, 0.0)
d.mtc_position = (0.0, 0.0, 0.0)
d.ending_position = (0.0, 0.0, 0.0)
d.working_area = (0.800000011920929, 0.5600000023841858, 0.09000000357627869)
d.feedrate_min = 9.999999747378752e-06
d.feedrate_max = 2.0
d.feedrate_default = 1.5
d.spindle_min = 5000.0
d.spindle_max = 25000.0
d.spindle_default = 20000.0
d.axis_4 = False
d.axis_5 = False
d.collet_size = 9.999999747378752e-06
d.output_tool_change = True
d.output_block_numbers = False
d.output_tool_definitions = True
d.output_G43_on_tool_change = False
