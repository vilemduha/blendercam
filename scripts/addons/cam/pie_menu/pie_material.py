import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Material(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Material Size & Position    ∴"

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        if len(scene.cam_operations) > 0:
            operation = scene.cam_operations[scene.cam_active_operation]
            material = operation.material

            # Left
            box = pie.box()
            column = box.column(align=True)
            if operation.geometry_source in ['OBJECT', 'COLLECTION']:
                column.prop(material, 'estimate_from_model')
            if material.estimate_from_model:
                column.prop(material, 'radius_around_model', text='Additional Radius')
            else:
                column.prop(material, 'origin')
                column.prop(material, 'size')

            # Right
            box = pie.box()
            column = box.column(align=True)
            if operation.geometry_source in ['OBJECT', 'COLLECTION']:
                column.prop(material, 'center_x')
                column.prop(material, 'center_y')
                column.prop(material, 'z_position')
                column.operator("object.material_cam_position", text="Position Object")

        else:
            pie.separator()
            pie.separator()

        # Bottom
        row = pie.row()
        row.label(text='')

        # Top
        box = pie.box()
        column = box.column(align=True)
        column.scale_y = 2
        column.scale_x = 2
        column.emboss = 'NONE'
        column.operator(
            "wm.call_menu_pie",
            text='',
            icon='HOME'
        ).name = 'VIEW3D_MT_PIE_CAM'
