
import bpy
from cam.ui_panels.buttons_panel import CAMButtonsPanel

# Operations panel
# This panel displays the list of operations created by the user
# Functionnalities are:
# - list Operations
# - create/delete/duplicate/reorder operations
# - display preset operations
#
# For each operation, generate the corresponding gcode and export the gcode file


class CAM_OPERATIONS_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operations panel"""
    bl_label = "CAM operations"
    bl_idname = "WORLD_PT_CAM_OPERATIONS"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    # Main draw function
    def draw(self, context):
        self.context = context
        self.draw_operations_list()

        # FIXME: is this ever used ?
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if (not self.has_operations()): return
        ao = self.active_operation()
        if ao is None: return

        self.draw_presets()

        self.draw_output_buttons()

        layout = self.layout
        sub = layout.column()
        sub.active = not ao.computing

        # Draw operation name and filename
        sub.prop(ao, 'name')
        sub.prop(ao, 'filename')

        self.draw_operation_source()
        self.draw_operation_options()


    # Draw the list of operations and the associated buttons:
    # create, delete, duplicate, reorder
    def draw_operations_list(self):
        row = self.layout.row()
        row.template_list("CAM_UL_operations", '', self.scene, "cam_operations", self.scene, 'cam_active_operation')
        col = row.column(align=True)
        col.operator("scene.cam_operation_add", icon='ADD', text="")
        col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
        col.operator("scene.cam_operation_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'


    # Draw the list of preset operations, and preset add and remove buttons
    def draw_presets(self):
        row = self.layout.row(align=True)
        row.menu("CAM_OPERATION_MT_presets", text=bpy.types.CAM_OPERATION_MT_presets.bl_label)
        row.operator("render.cam_preset_operation_add", text="", icon='ADD')
        row.operator("render.cam_preset_operation_add", text="", icon='REMOVE').remove_active = True


    # Draw buttons "Calculate path & export Gcode", "Export Gcode ", and "Simulate this operation"
    def draw_output_buttons(self):
        layout = self.layout
        ao = self.active_operation()

        # FIXME This does not seem to work - there is never a "Computing" label displayed
        # while an operation is being calculated
        if ao.computing:
            row = layout.row(align=True)
            row.label(text='computing')
            row.operator('object.kill_calculate_cam_paths_background', text="", icon='CANCEL')
        else:
            if ao.valid:
                layout.operator("object.calculate_cam_path", text="Calculate path & export Gcode")
                if ao.name is not None:
                    name = "cam_path_{}".format(ao.name)
                    if self.scene.objects.get(name) is not None:
                        layout.operator("object.cam_export", text="Export Gcode ")
                layout.operator("object.cam_simulate", text="Simulate this operation")
            else:
                layout.label(text="operation invalid, can't compute")


    # Draw a list of objects which will be used as the source of the operation
    # FIXME Right now, cameras or lights may be used, which crashes
    # The user should only be able to choose meshes and curves
    def draw_operation_source(self):
        layout = self.layout
        ao = self.active_operation()

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

    # Draw Operation options:
    # Remove redundant points (optimizes operation)
    # Use modifiers of the object
    # Hide all other paths
    # Parent path to object (?)

    def draw_operation_options(self):
        layout = self.layout
        ao = self.active_operation()

        # TODO This should be in some optimization menu
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
