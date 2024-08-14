"""BlenderCAM 'pie_feedrate.py'

'Operation Feedrate' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Feedrate(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation Feedrate    ∴"

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
        column.prop(operation, 'feedrate')
        column.prop(operation, 'do_simulation_feedrate')

        # Right
        box = pie.box()
        column = box.column(align=True)
        column.prop(operation, 'plunge_feedrate')
        column.prop(operation, 'plunge_angle')
        column.prop(operation, 'spindle_rpm')

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
