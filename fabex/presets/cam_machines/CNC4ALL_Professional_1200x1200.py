### CNC4ALL_Professional_1200x1200.py ###

import bpy

d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

s.system, s.length_unit = ("METRIC", "MILLIMETERS")

d.post_processor = "MACH3"
d.unit_system = "MILLIMETERS"
d.use_position_definitions = False
d.starting_position = (0.0, 0.0, 0.0)
d.mtc_position = (0.0, 0.0, 0.0)
d.ending_position = (0.0, 0.0, 0.0)
d.working_area = (1.2, 1.2, 0.15)
d.feedrate_min = 0.1
d.feedrate_max = 8.0
d.feedrate_default = 8.0
d.spindle_min = 0
d.spindle_max = 24000
d.spindle_default = 12000
d.axis_4 = False
d.axis_5 = False
d.collet_size = 0.25
d.output_tool_change = True
d.output_block_numbers = False
d.output_tool_definitions = True
d.output_G43_on_tool_change = False
