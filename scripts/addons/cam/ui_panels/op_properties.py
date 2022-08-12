
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel


class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation properties panel"""
    bl_label = "CAM operation setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"

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


    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                if use_experimental:
                    layout.prop(ao, 'machine_axes')
                if ao.machine_axes == '3':
                    layout.prop(ao, 'strategy')
                elif ao.machine_axes == '4':
                    layout.prop(ao, 'strategy4axis')
                    if ao.strategy4axis == 'INDEXED':
                        layout.prop(ao, 'strategy')
                    layout.prop(ao, 'rotary_axis_1')

                elif ao.machine_axes == '5':
                    layout.prop(ao, 'strategy5axis')
                    if ao.strategy5axis == 'INDEXED':
                        layout.prop(ao, 'strategy')
                    layout.prop(ao, 'rotary_axis_1')
                    layout.prop(ao, 'rotary_axis_2')

                if ao.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'OUTLINEFILL']:
                    layout.prop(ao, 'movement_insideout')

                if ao.strategy in ['CUTOUT', 'CURVE']:
                    if ao.strategy == 'CUTOUT':
                        layout.prop(ao, 'cut_type')
                        layout.label(text="Overshoot works best with curve")
                        layout.label(text="having C remove doubles")
                        layout.prop(ao, 'straight')
                        layout.prop(ao, 'profile_start')
                        layout.label(text="Lead in / out not fully working")
                        layout.prop(ao, 'lead_in')
                        layout.prop(ao, 'lead_out')
                    layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')

                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')

                    layout.prop(ao, 'outlines_count')
                    if ao.outlines_count > 1:
                        layout.prop(ao, 'dist_between_paths')
                        self.EngagementDisplay(ao, layout)
                        layout.prop(ao, 'movement_insideout')
                    layout.prop(ao, 'dont_merge')

                elif ao.strategy == 'WATERLINE':
                    layout.label(text="OCL doesn't support fill areas")
                    if not ao.use_opencamlib:
                        layout.prop(ao, 'slice_detail')
                        layout.prop(ao, 'waterline_fill')
                        if ao.waterline_fill:
                            layout.prop(ao, 'dist_between_paths')
                            self.EngagementDisplay(ao, layout)
                            layout.prop(ao, 'waterline_project')
                elif ao.strategy == 'CARVE':
                    layout.prop(ao, 'carve_depth')
                    layout.prop(ao, 'dist_along_paths')
                elif ao.strategy == 'MEDIAL_AXIS':
                    layout.prop(ao, 'medial_axis_threshold')
                    layout.prop(ao, 'medial_axis_subdivision')
                    layout.prop(ao, 'add_pocket_for_medial')
                    layout.prop(ao, 'add_mesh_for_medial')
                elif ao.strategy == 'DRILL':
                    layout.prop(ao, 'drill_type')
                    layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')
                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')

                elif ao.strategy == 'POCKET':
                    layout.prop(ao, 'pocket_option')
                    layout.prop(ao, 'pocketToCurve')
                    layout.prop(ao, 'dist_between_paths')
                    self.EngagementDisplay(ao, layout)
                    layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')
                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')
                else:
                    layout.prop(ao, 'dist_between_paths')
                    self.EngagementDisplay(ao, layout)
                    layout.prop(ao, 'dist_along_paths')
                    if ao.strategy == 'PARALLEL' or ao.strategy == 'CROSS':
                        layout.prop(ao, 'parallel_angle')
                        layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')
                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')

                    layout.prop(ao, 'inverse')
                if ao.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
                    layout.prop(ao, 'use_bridges')
                    if ao.use_bridges:
                        layout.prop(ao, 'bridges_width')
                        layout.prop(ao, 'bridges_height')

                        layout.prop_search(ao, "bridges_collection_name", bpy.data, "collections")
                        layout.prop(ao, 'use_bridge_modifiers')
                    layout.operator("scene.cam_bridges_add", text="Autogenerate bridges")
            if ao.strategy == 'WATERLINE':
                    layout.label(text="Waterline roughing strategy")
                    layout.label(text="needs a skin margin")
            layout.prop(ao, 'skin')

            if ao.machine_axes == '3':
                layout.prop(ao, 'array')
                if ao.array:
                    layout.prop(ao, 'array_x_count')
                    layout.prop(ao, 'array_x_distance')
                    layout.prop(ao, 'array_y_count')
                    layout.prop(ao, 'array_y_distance')
