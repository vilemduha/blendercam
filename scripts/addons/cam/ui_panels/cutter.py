
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel


class CAM_CUTTER_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM cutter panel"""
    bl_label = " "
    bl_idname = "WORLD_PT_CAM_CUTTER"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}


    # Displays percentage of the cutter which is engaged with the material
    # Displays a warning for engagements greater than 50%
    def EngagementDisplay(self, operat, layout):
        ao = operat

        if ao.cutter_type == 'BALLCONE':
            if ao.dist_between_paths > ao.ball_radius:
                layout.label(text="CAUTION: CUTTER ENGAGEMENT")
                layout.label(text="GREATER THAN 50%")
            layout.label(text="Cutter engagement: " + str(round(100 * ao.dist_between_paths / ao.ball_radius, 1)) + "%")
        else:
            if ao.dist_between_paths > ao.cutter_diameter / 2:
                layout.label(text="CAUTION: CUTTER ENGAGEMENT")
                layout.label(text="GREATER THAN 50%")
            layout.label(text="Cutter Engagement: " + str(round(100 * ao.dist_between_paths / ao.cutter_diameter, 1)) + "%")

    def draw_header(self, context):
        self.layout.menu("CAM_CUTTER_MT_presets", text="CAM Cutter")

    def draw(self, context):
        layout = self.layout
        d = bpy.context.scene
        if len(d.cam_operations) > 0:
            ao = d.cam_operations[d.cam_active_operation]

            if ao:
                # cutter preset
                row = layout.row(align=True)
                row.menu("CAM_CUTTER_MT_presets", text=bpy.types.CAM_CUTTER_MT_presets.bl_label)
                row.operator("render.cam_preset_cutter_add", text="", icon='ADD')
                row.operator("render.cam_preset_cutter_add", text="", icon='REMOVE').remove_active = True
                layout.prop(ao, 'cutter_id')
                layout.prop(ao, 'cutter_type')
                if ao.cutter_type == 'VCARVE':
                    layout.prop(ao, 'cutter_tip_angle')
                if ao.cutter_type == 'BALLCONE':
                    layout.prop(ao, 'ball_radius')
                    self.EngagementDisplay(ao, layout)
                    layout.prop(ao, 'cutter_tip_angle')
                    layout.label(text='Cutter diameter = shank diameter')
                if ao.cutter_type == 'CYLCONE':
                    layout.prop(ao, 'cylcone_diameter')
                    self.EngagementDisplay(ao, layout)
                    layout.prop(ao, 'cutter_tip_angle')
                    layout.label(text='Cutter diameter = shank diameter')
                if ao.cutter_type == 'BULLNOSE':
                    layout.prop(ao, 'bull_corner_radius')
                    self.EngagementDisplay(ao, layout)
                    layout.label(text='Cutter diameter = shank diameter')

                if ao.cutter_type == 'LASER':
                    layout.prop(ao, 'Laser_on')
                    layout.prop(ao, 'Laser_off')
                    layout.prop(ao, 'Laser_cmd')
                    layout.prop(ao, 'Laser_delay')

                if ao.cutter_type == 'PLASMA':
                    layout.prop(ao, 'Plasma_on')
                    layout.prop(ao, 'Plasma_off')
                    layout.prop(ao, 'Plasma_delay')
                    layout.prop(ao, 'Plasma_dwell')
                    layout.prop(ao, 'lead_in')
                    layout.prop(ao, 'lead_out')

                if ao.cutter_type == 'CUSTOM':
                    if ao.use_exact:
                        layout.label(text='Warning - only convex shapes are supported. ', icon='COLOR_RED')
                        layout.label(text='If your custom cutter is concave,')
                        layout.label(text='switch exact mode off.')

                    layout.prop_search(ao, "cutter_object_name", bpy.data, "objects")

                layout.prop(ao, 'cutter_diameter')
                if ao.strategy == "POCKET" or ao.strategy == "PARALLEL" or ao.strategy == "CROSS" \
                        or ao.strategy == "WATERLINE":
                    self.EngagementDisplay(ao, layout)
                if ao.cutter_type != "LASER":
                    layout.prop(ao, 'cutter_flutes')
                layout.prop(ao, 'cutter_description')
