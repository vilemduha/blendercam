### Axiom_Iconic_8.py ###
            
import bpy
d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

d.post_processor = 'Axiom_HHC'
d.unit_system = 'INCHES'
d.use_position_definitions = False
d.starting_position = (0.0, 0.0, 0.0)
d.mtc_position = (0.0, 0.0, 0.0)
d.ending_position = (0.0, 0.0, 0.0)
d.working_area = (24.0, 48.0, 3.9)
d.feedrate_min = 400
d.feedrate_max = 200
d.feedrate_default = 1
d.spindle_min = 24000
d.spindle_max = 12000
d.spindle_default = 8000
d.axis4 = False
d.axis5 = False
d.collet_size = 0.25
d.output_tool_change = True
d.output_block_numbers = False
d.output_tool_definitions = True
d.output_g43_on_tool_change = False

        