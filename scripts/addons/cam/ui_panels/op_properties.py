
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel


class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation properties panel"""
    bl_label = "CAM operation setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"
    panel_interface_level = 0

    prop_level = {
        'draw_cutter_engagement': 0,
        'draw_machine_axis': 2,
        'draw_strategy': 0
    }


    # Displays percentage of the cutter which is engaged with the material
    # Displays a warning for engagements greater than 50%
    def draw_cutter_engagement(self):
        if not self.has_correct_level(): return

        if self.op.cutter_type in ['BALLCONE']:
            engagement = round(100 * self.op.dist_between_paths / self.op.ball_radius, 1)
        else:
            engagement = round(100 * self.op.dist_between_paths / self.op.cutter_diameter, 1)

        if engagement > 50:
            self.layout.label(text="Warning: High cutter engagement")

        self.layout.label(text=f"Cutter engagement: {engagement}%")

    def draw_machine_axis(self):
        if not self.has_correct_level(): return
        self.layout.prop(self.op, 'machine_axes')

    def draw_strategy(self):
        if not self.has_correct_level(): return
        if self.op.machine_axes == '4':
            self.layout.prop(self.op, 'strategy4axis')
            if self.op.strategy4axis == 'INDEXED':
                self.layout.prop(self.op, 'strategy')
            self.layout.prop(self.op, 'rotary_axis_1')
        elif self.op.machine_axes == '5':
            self.layout.prop(self.op, 'strategy5axis')
            if self.op.strategy5axis == 'INDEXED':
                self.layout.prop(self.op, 'strategy')
            self.layout.prop(self.op, 'rotary_axis_1')
            self.layout.prop(self.op, 'rotary_axis_2')
        else:
            self.layout.prop(self.op, 'strategy')


    def draw(self, context):
        self.context = context

        self.draw_machine_axis()
        self.draw_strategy()




        if self.op.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'OUTLINEFILL']:
            self.layout.prop(self.op.movement, 'insideout')

        if self.op.strategy in ['CUTOUT', 'CURVE']:
            if self.op.strategy == 'CUTOUT':
                self.layout.prop(self.op, 'cut_type')
                self.layout.label(text="Overshoot works best with curve")
                self.layout.label(text="having C remove doubles")
                self.layout.prop(self.op, 'straight')
                self.layout.prop(self.op, 'profile_start')
                self.layout.label(text="Lead in / out not fully working")
                self.layout.prop(self.op, 'lead_in')
                self.layout.prop(self.op, 'lead_out')

            self.layout.prop(self.op, 'enable_A')
            if self.op.enable_A:
                self.layout.prop(self.op, 'rotation_A')
                self.layout.prop(self.op, 'A_along_x')
                if self.op.A_along_x:
                    self.layout.label(text='A || X - B || Y')
                else:
                    self.layout.label(text='A || Y - B ||X')

            self.layout.prop(self.op, 'enable_B')
            if self.op.enable_B:
                self.layout.prop(self.op, 'rotation_B')

            self.layout.prop(self.op, 'outlines_count')
            if self.op.outlines_count > 1:
                self.layout.prop(self.op, 'dist_between_paths')
                self.draw_cutter_engagement()
                self.layout.prop(self.op.movement, 'insideout')
            self.layout.prop(self.op, 'dont_merge')

        elif self.op.strategy == 'WATERLINE':
            self.layout.label(text="OCL doesn't support fill areas")
            if not self.op.optimisation.use_opencamlib:
                self.layout.prop(self.op, 'slice_detail')
                self.layout.prop(self.op, 'waterline_fill')
                if self.op.waterline_fill:
                    self.layout.prop(self.op, 'dist_between_paths')
                    self.draw_cutter_engagement()
                    self.layout.prop(self.op, 'waterline_project')

        elif self.op.strategy == 'CARVE':
            self.layout.prop(self.op, 'carve_depth')
            self.layout.prop(self.op, 'dist_along_paths')
        elif self.op.strategy == 'MEDIAL_AXIS':
            self.layout.prop(self.op, 'medial_axis_threshold')
            self.layout.prop(self.op, 'medial_axis_subdivision')
            self.layout.prop(self.op, 'add_pocket_for_medial')
            self.layout.prop(self.op, 'add_mesh_for_medial')
        elif self.op.strategy == 'DRILL':
            self.layout.prop(self.op, 'drill_type')
            self.layout.prop(self.op, 'enable_A')
            if self.op.enable_A:
                self.layout.prop(self.op, 'rotation_A')
                self.layout.prop(self.op, 'A_along_x')
                if self.op.A_along_x:
                    self.layout.label(text='A || X - B || Y')
                else:
                    self.layout.label(text='A || Y - B ||X')
            self.layout.prop(self.op, 'enable_B')
            if self.op.enable_B:
                self.layout.prop(self.op, 'rotation_B')

        elif self.op.strategy == 'POCKET':
            self.layout.prop(self.op, 'pocket_option')
            self.layout.prop(self.op, 'pocketToCurve')
            self.layout.prop(self.op, 'dist_between_paths')
            self.draw_cutter_engagement()
            self.layout.prop(self.op, 'enable_A')
            if self.op.enable_A:
                self.layout.prop(self.op, 'rotation_A')
                self.layout.prop(self.op, 'A_along_x')
                if self.op.A_along_x:
                    self.layout.label(text='A || X - B || Y')
                else:
                    self.layout.label(text='A || Y - B ||X')
            self.layout.prop(self.op, 'enable_B')
            if self.op.enable_B:
                self.layout.prop(self.op, 'rotation_B')
        else:
            self.layout.prop(self.op, 'dist_between_paths')
            self.draw_cutter_engagement()
            self.layout.prop(self.op, 'dist_along_paths')
            if self.op.strategy == 'PARALLEL' or self.op.strategy == 'CROSS':
                self.layout.prop(self.op, 'parallel_angle')
                self.layout.prop(self.op, 'enable_A')
            if self.op.enable_A:
                self.layout.prop(self.op, 'rotation_A')
                self.layout.prop(self.op, 'A_along_x')
                if self.op.A_along_x:
                    self.layout.label(text='A || X - B || Y')
                else:
                    self.layout.label(text='A || Y - B ||X')
            self.layout.prop(self.op, 'enable_B')
            if self.op.enable_B:
                self.layout.prop(self.op, 'rotation_B')

            self.layout.prop(self.op, 'inverse')

        if self.op.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
            self.layout.prop(self.op, 'use_bridges')
            if self.op.use_bridges:
                self.layout.prop(self.op, 'bridges_width')
                self.layout.prop(self.op, 'bridges_height')

                self.layout.prop_search(self.op, "bridges_collection_name", bpy.data, "collections")
                self.layout.prop(self.op, 'use_bridge_modifiers')
            self.layout.operator("scene.cam_bridges_add", text="Autogenerate bridges")

        if self.op.strategy == 'WATERLINE':
                self.layout.label(text="Waterline roughing strategy")
                self.layout.label(text="needs a skin margin")
        self.layout.prop(self.op, 'skin')

        if self.op.machine_axes == '3':
            self.layout.prop(self.op, 'array')
            if self.op.array:
                self.layout.prop(self.op, 'array_x_count')
                self.layout.prop(self.op, 'array_x_distance')
                self.layout.prop(self.op, 'array_y_count')
                self.layout.prop(self.op, 'array_y_distance')
