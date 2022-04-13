
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

class CAM_MACHINE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM machine panel"""
    bl_label = " "
    bl_idname = "WORLD_PT_CAM_MACHINE"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw_header(self, context):
        self.layout.menu("CAM_MACHINE_MT_presets", text="CAM Machine")

    def draw(self, context):
        layout = self.layout
        s = bpy.context.scene
        us = s.unit_settings

        ao = s.cam_machine

        if ao:
            use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

            # machine preset
            row = layout.row(align=True)
            row.menu("CAM_MACHINE_MT_presets", text=bpy.types.CAM_MACHINE_MT_presets.bl_label)
            row.operator("render.cam_preset_machine_add", text="", icon='ADD')
            row.operator("render.cam_preset_machine_add", text="", icon='REMOVE').remove_active = True
            layout.prop(ao, 'post_processor')
            layout.prop(ao, 'eval_splitting')
            if ao.eval_splitting:
                layout.prop(ao, 'split_limit')

            layout.prop(us, 'system')

            layout.prop(ao, 'use_position_definitions')
            if ao.use_position_definitions:
                layout.prop(ao, 'starting_position')
                layout.prop(ao, 'mtc_position')
                layout.prop(ao, 'ending_position')
            layout.prop(ao, 'working_area')
            layout.prop(ao, 'feedrate_min')
            layout.prop(ao, 'feedrate_max')
            layout.prop(ao, 'feedrate_default')
            # TODO: spindle default and feedrate default should become part of the cutter definition...
            layout.prop(ao, 'spindle_min')
            layout.prop(ao, 'spindle_max')
            layout.prop(ao, 'spindle_start_time')
            layout.prop(ao, 'spindle_default')
            layout.prop(ao, 'output_tool_definitions')
            layout.prop(ao, 'output_tool_change')
            if ao.output_tool_change:
                layout.prop(ao, 'output_g43_on_tool_change')

            if use_experimental:
                layout.prop(ao, 'axis4')
                layout.prop(ao, 'axis5')
                layout.prop(ao, 'collet_size')

                layout.prop(ao, 'output_block_numbers')
                if ao.output_block_numbers:
                    layout.prop(ao, 'start_block_number')
                    layout.prop(ao, 'block_number_increment')
            layout.prop(ao, 'hourly_rate')
