import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Gcode(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation G-code    ∴"

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
        column.prop(operation, 'output_header')
        if operation.output_header:
            column.prop(operation, 'gcode_header')

        column.prop(operation, 'output_trailer')
        if operation.output_trailer:
            column.prop(operation, 'gcode_trailer')

        # Right
        box = pie.box()
        column = box.column(align=True)
        column.prop(operation, 'enable_dust')
        if operation.enable_dust:
            column.prop(operation, 'gcode_start_dust_cmd')
            column.prop(operation, 'gcode_stop_dust_cmd')

        column.prop(operation, 'enable_hold')
        if operation.enable_hold:
            column.prop(operation, 'gcode_start_hold_cmd')
            column.prop(operation, 'gcode_stop_hold_cmd')

        column.prop(operation, 'enable_mist')
        if operation.enable_mist:
            column.prop(operation, 'gcode_start_mist_cmd')
            column.prop(operation, 'gcode_stop_mist_cmd')

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
