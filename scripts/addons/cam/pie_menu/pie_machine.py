"""BlenderCAM 'pie_machine.py'

'Machine Settings' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Machine(Menu):
    bl_label = "∴    Machine Settings    ∴"

    def draw(self, context):
        scene = context.scene
        machine = scene.cam_machine

        layout = self.layout
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column()
        column.emboss = 'RADIAL_MENU'
        column.menu("CAM_MACHINE_MT_presets", text='Presets', icon='RIGHTARROW')
        column.emboss = 'NORMAL'
        column.prop(machine, 'post_processor')
        column.prop(machine, 'eval_splitting')
        if machine.eval_splitting:
            column.prop(machine, 'split_limit')
        column.prop(scene.unit_settings, 'system')
        column.prop(machine, 'working_area')
        column = box.column(align=True)
        column.prop(machine, 'feedrate_min')
        column.prop(machine, 'feedrate_max')
        column.prop(machine, 'feedrate_default')
        column.prop(machine, 'spindle_min')
        column.prop(machine, 'spindle_max')
        column.prop(machine, 'spindle_start_time')
        column.prop(machine, 'spindle_default')

        # Right
        box = pie.box()
        column = box.column(align=True)
        column.prop(machine, 'output_tool_definitions')
        column.prop(machine, 'output_tool_change')
        if machine.output_tool_change:
            column.prop(machine, 'output_g43_on_tool_change')
        column.prop(machine, 'axis4')
        column.prop(machine, 'axis5')
        column = box.column()
        column.prop(machine, 'collet_size')
        column.prop(machine, 'hourly_rate')

        # Bottom
        pie_column = pie.column()
        pie_column.separator(factor=12)
        box = pie_column.box()
        column = box.column(align=True)
        column.prop(machine, 'use_position_definitions')
        if machine.use_position_definitions:
            column.prop(machine, 'starting_position')
            column.prop(machine, 'mtc_position')
            column.prop(machine, 'ending_position')
        column.prop(machine, 'output_block_numbers')
        if machine.output_block_numbers:
            column.prop(machine, 'start_block_number')
            column.prop(machine, 'block_number_increment')
        pie_column.separator(factor=15)

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = 'NONE'
        box.operator(
            "wm.call_menu_pie",
            text='',
            icon='HOME'
        ).name = 'VIEW3D_MT_PIE_CAM'
