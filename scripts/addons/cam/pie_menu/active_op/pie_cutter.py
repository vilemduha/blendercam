"""BlenderCAM 'pie_cutter.py'

'Operation Cutter' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Cutter(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation Cutter    ∴"

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
        row = column.row(align=True)
        row.menu("CAM_CUTTER_MT_presets", text=bpy.types.CAM_CUTTER_MT_presets.bl_label)
        row.operator("render.cam_preset_cutter_add", text="", icon='ADD')
        row.operator("render.cam_preset_cutter_add", text="", icon='REMOVE').remove_active = True
        column.prop(operation, 'cutter_id')

        column.prop(operation, 'cutter_type')

        if operation.cutter_type in ['BALLCONE']:
            column.prop(operation, 'ball_radius')

        if operation.cutter_type in ['BULLNOSE']:
            column.prop(operation, 'bull_corner_radius')

        if operation.cutter_type in ['CYLCONE']:
            column.prop(operation, 'cylcone_diameter')

        if operation.cutter_type in ['VCARVE', 'BALLCONE', 'BULLNOSE', 'CYLCONE']:
            column.prop(operation, 'cutter_tip_angle')

        if operation.cutter_type in ['LASER']:
            column.prop(operation, 'Laser_on')
            column.prop(operation, 'Laser_off')
            column.prop(operation, 'Laser_cmd')
            column.prop(operation, 'Laser_delay')

        if operation.cutter_type in ['PLASMA']:
            column.prop(operation, 'Plasma_on')
            column.prop(operation, 'Plasma_off')
            column.prop(operation, 'Plasma_delay')
            column.prop(operation, 'Plasma_dwell')
            column.prop(operation, 'lead_in')
            column.prop(operation, 'lead_out')

        if operation.cutter_type in ['CUSTOM']:
            if operation.optimisation.use_exact:
                column.label(
                    text='Warning - only Convex Shapes Are Supported. ', icon='COLOR_RED')
                column.label(text='If Your Custom Cutter Is Concave,')
                column.label(text='Switch Exact Mode Off.')
            column.prop_search(operation, "cutter_object_name", bpy.data, "objects")

        column.prop(operation, 'cutter_diameter')

        if operation.cutter_type not in ['LASER', 'PLASMA']:
            column.prop(operation, 'cutter_flutes')

        column.prop(operation, 'cutter_description')

        # Right
        box = pie.box()
        column = box.column(align=True)
        if operation.cutter_type in ['LASER', 'PLASMA']:
            return
        if operation.strategy in ['CUTOUT']:
            return

        if operation.cutter_type in ['BALLCONE']:
            engagement = round(100 * operation.dist_between_paths / operation.ball_radius, 1)
        else:
            engagement = round(100 * operation.dist_between_paths / operation.cutter_diameter, 1)

        column.label(text=f"Cutter Engagement: {engagement}%")

        if engagement > 50:
            column.label(text="WARNING: CUTTER ENGAGEMENT > 50%")

        # Bottom
        row = pie.row()
        row.label(text='')

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
