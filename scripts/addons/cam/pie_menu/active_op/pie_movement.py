import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Movement(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation Movement    ∴"

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
        if operation.strategy in ['POCKET']:
            column.prop(operation.movement, 'helix_enter')
            if operation.movement.helix_enter:
                column.prop(operation.movement, 'ramp_in_angle')
                column.prop(operation.movement, 'helix_diameter')

        column.prop(operation.movement, 'ramp')
        if operation.movement.ramp:
            column.prop(operation.movement, 'ramp_in_angle')
            column.prop(operation.movement, 'ramp_out')
            if operation.movement.ramp_out:
                column.prop(operation.movement, 'ramp_out_angle')

        # Right
        box = pie.box()
        column = box.column(align=True)
        if operation.strategy in ['POCKET']:
            column.prop(operation.movement, 'retract_tangential')
            if operation.movement.retract_tangential:
                column.prop(operation.movement, 'retract_radius')
                column.prop(operation.movement, 'retract_height')

        column.prop(operation.movement, 'stay_low')
        if operation.movement.stay_low:
            column.prop(operation.movement, 'merge_dist')

        if operation.cutter_type not in ['BALLCONE']:
            column.prop(operation.movement, 'protect_vertical')
            if operation.movement.protect_vertical:
                column.prop(operation.movement, 'protect_vertical_limit')

        # Bottom
        box = pie.box()
        column = box.column(align=True)
        column.prop(operation.movement, 'type')
        if operation.movement.type in ['BLOCK', 'SPIRAL', 'CIRCLES']:
            column.prop(operation.movement, 'insideout')

        column.prop(operation.movement, 'spindle_rotation')

        column.prop(operation.movement, 'free_height')
        if operation.maxz > operation.movement.free_height:
            column.label(text='Depth Start > Free Movement')
            column.label(text='POSSIBLE COLLISION')

        # if self.context.scene.cam_machine.post_processor not in G64_INCOMPATIBLE_MACHINES:
        #     column.prop(operation.movement, 'useG64')
        #     if operation.movement.useG64:
        #         column.prop(operation.movement, 'G64')

        if operation.strategy in ['PARALLEL', 'CROSS']:
            if not operation.movement.ramp:
                column.prop(operation.movement, 'parallel_step_back')

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
