
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel


class CAM_MOVEMENT_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM movement panel"""
    bl_label = "CAM movement"
    bl_idname = "WORLD_PT_CAM_MOVEMENT"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'movement_type')

                if ao.movement_type in ['BLOCK', 'SPIRAL', 'CIRCLES']:
                    layout.prop(ao, 'movement_insideout')

                layout.prop(ao, 'spindle_rotation_direction')
                layout.prop(ao, 'free_movement_height')
                if ao.maxz > ao.free_movement_height:
                    layout.label(text='Depth start > Free movement')
                    layout.label(text='POSSIBLE COLLISION')
                layout.prop(ao, 'useG64')
                if ao.useG64:
                    layout.prop(ao, 'G64')
                if ao.strategy == 'PARALLEL' or ao.strategy == 'CROSS':
                    if not ao.ramp:
                        layout.prop(ao, 'parallel_step_back')
                if ao.strategy == 'CUTOUT' or ao.strategy == 'POCKET' or ao.strategy == 'MEDIAL_AXIS':
                    layout.prop(ao, 'first_down')

                if ao.strategy == 'POCKET':
                    layout.prop(ao, 'helix_enter')
                    if ao.helix_enter:
                        layout.prop(ao, 'ramp_in_angle')
                        layout.prop(ao, 'helix_diameter')
                    layout.prop(ao, 'retract_tangential')
                    if ao.retract_tangential:
                        layout.prop(ao, 'retract_radius')
                        layout.prop(ao, 'retract_height')

                layout.prop(ao, 'ramp')
                if ao.ramp:
                    layout.prop(ao, 'ramp_in_angle')
                    layout.prop(ao, 'ramp_out')
                    if ao.ramp_out:
                        layout.prop(ao, 'ramp_out_angle')

                layout.prop(ao, 'stay_low')
                if ao.stay_low:
                    layout.prop(ao, 'merge_dist')
                if ao.cutter_type != 'BALLCONE':
                    layout.prop(ao, 'protect_vertical')
                if ao.protect_vertical:
                    layout.prop(ao, 'protect_vertical_limit')
