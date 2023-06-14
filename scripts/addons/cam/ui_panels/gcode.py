
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel


class CAM_GCODE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation g-code options panel"""
    bl_label = "CAM g-code options "
    bl_idname = "WORLD_PT_CAM_GCODE"
    panel_interface_level = 1

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'output_header')

                if ao.output_header:
                    layout.prop(ao, 'gcode_header')
                layout.prop(ao, 'output_trailer')
                if ao.output_trailer:
                    layout.prop(ao, 'gcode_trailer')
                layout.prop(ao, 'enable_dust')
                if ao.enable_dust:
                    layout.prop(ao, 'gcode_start_dust_cmd')
                    layout.prop(ao, 'gcode_stop_dust_cmd')
                layout.prop(ao, 'enable_hold')
                if ao.enable_hold:
                    layout.prop(ao, 'gcode_start_hold_cmd')
                    layout.prop(ao, 'gcode_stop_hold_cmd')
                layout.prop(ao, 'enable_mist')
                if ao.enable_mist:
                    layout.prop(ao, 'gcode_start_mist_cmd')
                    layout.prop(ao, 'gcode_stop_mist_cmd')

            else:
                layout.label(text='Enable Show experimental features')
                layout.label(text='in Blender CAM Addon preferences')



