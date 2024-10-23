"""CNC CAM 'pie_setup.py'

'Operation Setup' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Setup(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation Setup    ∴"

    def draw(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]
        material = operation.material

        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column(align=True)
        column.prop(operation, 'machine_axes')
        if operation.machine_axes == '4':
            column.prop(operation, 'strategy4axis')
            if operation.strategy4axis == 'INDEXED':
                column.prop(operation, 'strategy')
            column.prop(operation, 'rotary_axis_1')
        elif operation.machine_axes == '5':
            column.prop(operation, 'strategy5axis')
            if operation.strategy5axis == 'INDEXED':
                column.prop(operation, 'strategy')
            column.prop(operation, 'rotary_axis_1')
            column.prop(operation, 'rotary_axis_2')
        else:
            column.prop(operation, 'strategy')
        column.prop(operation, 'cut_type')
        column.prop(operation, 'straight')

        column.prop(operation, 'enable_A')
        if operation.enable_A:
            column.prop(operation, 'rotation_A')
            column.prop(operation, 'A_along_x')
            if operation.A_along_x:
                column.label(text='A || X - B || Y')
            else:
                column.label(text='A || Y - B ||X')
        column.prop(operation, 'enable_B')
        if operation.enable_B:
            column.prop(operation, 'rotation_B')

        # Right
        box = pie.box()
        column = box.column(align=True)
        if operation.cutter_type in ['BALLCONE']:
            engagement = round(100 * operation.dist_between_paths / operation.ball_radius, 1)
        else:
            engagement = round(100 * operation.dist_between_paths / operation.cutter_diameter, 1)

        if engagement > 50:
            column.label(text="Warning: High Cutter Engagement")
        column.label(text=f"Cutter Engagement: {engagement}%")

        column.prop(operation, 'profile_start')
        column.prop(operation, 'lead_in')
        column.prop(operation, 'lead_out')
        column.prop(operation, 'outlines_count')
        if operation.outlines_count > 1:
            column.prop(operation, 'dist_between_paths')
            self.draw_cutter_engagement()
            column.prop(operation.movement, 'insideout')
        column.prop(operation, 'dont_merge')

        # Bottom
        box = pie.box()
        column = box.column(align=True)
        if operation.strategy in ['CUTOUT']:
            pass
            # self.draw_cutout_type()
#            self.draw_overshoot()
#            self.draw_startpoint()
#            self.draw_lead_in_out()

        if operation.strategy in ['CUTOUT', 'CURVE']:
            pass
#            self.draw_enable_A_B_axis()
#            self.draw_outlines()
#            self.draw_merge()

        if operation.strategy in ['WATERLINE']:
            column.label(text="OCL Doesn't Support Fill Areas")
            if not operation.optimisation.use_opencamlib:
                column.prop(operation, 'slice_detail')
                column.prop(operation, 'waterline_fill')
                if operation.waterline_fill:
                    column.prop(operation, 'dist_between_paths')
                    column.prop(operation, 'waterline_project')
            column.label(text="Waterline needs a skin margin")

        if operation.strategy in ['CARVE']:
            column.prop(operation, 'carve_depth')
            column.prop(operation, 'dist_along_paths')

        if operation.strategy in ['MEDIAL_AXIS']:
            column.prop(operation, 'medial_axis_threshold')
            column.prop(operation, 'medial_axis_subdivision')
            column.prop(operation, 'add_pocket_for_medial')
            column.prop(operation, 'add_mesh_for_medial')

        if operation.strategy in ['DRILL']:
            column.prop(operation, 'drill_type')
#            self.draw_enable_A_B_axis()

        if operation.strategy in ['POCKET']:
            column.prop(operation, 'pocket_option')
            column.prop(operation, 'pocketToCurve')
            column.prop(operation, 'dist_between_paths')
#            self.draw_cutter_engagement()
#            self.draw_enable_A_B_axis()

        if operation.strategy not in [
            'CUTOUT',
            'CURVE',
            'WATERLINE',
            'CARVE',
            'MEDIAL_AXIS',
            'DRILL',
            'POCKET',
        ]:
            column.prop(operation, 'dist_between_paths')
#            self.draw_cutter_engagement()
            column.prop(operation, 'dist_along_paths')
            if operation.strategy in ['PARALLEL', 'CROSS']:
                column.prop(operation, 'parallel_angle')
#                self.draw_enable_A_B_axis()
            column.prop(operation, 'inverse')

        if operation.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
            column.prop(operation, 'use_bridges')
            if operation.use_bridges:
                column.prop(operation, 'bridges_width')
                column.prop(operation, 'bridges_height')
                column.prop_search(operation, "bridges_collection_name", bpy.data, "collections")
                column.prop(operation, 'use_bridge_modifiers')
            column.operator("scene.cam_bridges_add", text="Autogenerate Bridges / Tabs")

        column.prop(operation, 'skin')

        if operation.machine_axes == '3':
            column.prop(operation, 'array')
            if operation.array:
                column.prop(operation, 'array_x_count')
                column.prop(operation, 'array_x_distance')
                column.prop(operation, 'array_y_count')
                column.prop(operation, 'array_y_distance')

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = 'NONE'
        box.operator(
            "wm.call_menu_pie",
            text='',
            icon='BACK'
        ).name = 'VIEW3D_MT_PIE_Operation'
