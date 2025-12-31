### MillRight_Power_Route_Max.py ###

import bpy

d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

s.system, s.length_unit = ("IMPERIAL", "INCHES")

d.post_processor = "GRBL"
d.unit_system = "INCHES"
d.use_position_definitions = False
d.starting_position = (0.0, 0.0, 0.0)
d.mtc_position = (0.0, 0.0, 0.0)
d.ending_position = (0.0, 0.0, 0.0)
d.working_area = (1.27, 1.27, 0.1397)
d.feedrate_min = 0.0254
d.feedrate_max = 10.16
d.feedrate_default = 5.08
d.spindle_min = 6000
d.spindle_max = 24000
d.spindle_default = 12000
d.axis_4 = False
d.axis_5 = False
d.collet_size = 0.5
d.output_tool_change = True
d.output_block_numbers = False
d.output_tool_definitions = True
d.output_G43_on_tool_change = False
