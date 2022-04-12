
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel


class CAM_OPERATIONS_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operations panel"""
    bl_label = "CAM operations"
    bl_idname = "WORLD_PT_CAM_OPERATIONS"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.template_list("CAM_UL_operations", '', self.scene, "cam_operations", self.scene, 'cam_active_operation')
        col = row.column(align=True)
        col.operator("scene.cam_operation_add", icon='ADD', text="")
        col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
        col.operator("scene.cam_operation_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if (not self.has_operations()): return
        ao = self.active_operation()
        if ao is None: return

        row = layout.row(align=True)
        row.menu("CAM_OPERATION_MT_presets", text=bpy.types.CAM_OPERATION_MT_presets.bl_label)
        row.operator("render.cam_preset_operation_add", text="", icon='ADD')
        row.operator("render.cam_preset_operation_add", text="", icon='REMOVE').remove_active = True

        if not ao.computing:
            if ao.valid:
                layout.operator("object.calculate_cam_path", text="Calculate path & export Gcode")
                if ao.name is not None:
                    name = "cam_path_{}".format(ao.name)
                    if self.scene.objects.get(name) is not None:
                        layout.operator("object.cam_export", text="Export Gcode ")
                layout.operator("object.cam_simulate", text="Simulate this operation")
            else:
                layout.label(text="operation invalid, can't compute")
        else:
            row = layout.row(align=True)
            row.label(text='computing')
            row.operator('object.kill_calculate_cam_paths_background', text="", icon='CANCEL')

        sub = layout.column()
        sub.active = not ao.computing

        sub.prop(ao, 'name')
        sub.prop(ao, 'filename')

        layout.prop(ao, 'geometry_source')

        if ao.strategy == 'CURVE':
            if ao.geometry_source == 'OBJECT':
                layout.prop_search(ao, "object_name", bpy.data, "objects")
            elif ao.geometry_source == 'COLLECTION':
                layout.prop_search(ao, "collection_name", bpy.data, "collections")
        else:
            if ao.geometry_source == 'OBJECT':
                layout.prop_search(ao, "object_name", bpy.data, "objects")
                if ao.enable_A:
                    layout.prop(ao, 'rotation_A')
                if ao.enable_B:
                    layout.prop(ao, 'rotation_B')

            elif ao.geometry_source == 'COLLECTION':
                layout.prop_search(ao, "collection_name", bpy.data, "collections")
            else:
                layout.prop_search(ao, "source_image_name", bpy.data, "images")


        if ao.strategy in ['CARVE', 'PROJECTED_CURVE']:
            layout.prop_search(ao, "curve_object", bpy.data, "objects")
            if ao.strategy == 'PROJECTED_CURVE':
                layout.prop_search(ao, "curve_object1", bpy.data, "objects")

        layout.prop(ao, 'remove_redundant_points')
        if ao.remove_redundant_points:
            layout.label(text='Revise your Code before running!')
            layout.label(text='Quality will suffer if tolerance')
            layout.label(text='is high')
            layout.prop(ao, 'simplify_tol')
        if ao.geometry_source in ['OBJECT', 'COLLECTION']:
            layout.prop(ao, 'use_modifiers')
        layout.prop(ao, 'hide_all_others')
        layout.prop(ao, 'parent_path_to_object')
