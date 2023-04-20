
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
        self.draw_operations_list()

        # FIXME: is this ever used ?
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if (not self.has_operations()): return
        if self.active_op is None: return

        self.draw_presets()
        self.draw_output_buttons()

        sub = self.layout.column()
        sub.active = not self.active_op.computing

        # Draw operation name and filename
        sub.prop(self.active_op, 'name')
        sub.prop(self.active_op, 'filename')

        self.draw_operation_source()
        self.draw_operation_options()


    # Draw the list of operations and the associated buttons:
    # create, delete, duplicate, reorder
    def draw_operations_list(self):
        row = self.layout.row()
        row.template_list("CAM_UL_operations", '', bpy.context.scene, "cam_operations", bpy.context.scene, 'cam_active_operation')
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
        # FIXME This does not seem to work - there is never a "Computing" label displayed
        # while an operation is being calculated
        if self.active_op.computing:
            row = self.layout.row(align=True)
            row.label(text='computing')
            row.operator('object.kill_calculate_cam_paths_background', text="", icon='CANCEL')
        else:
            if self.active_op.valid:
                self.layout.operator("object.calculate_cam_path", text="Calculate path & export Gcode")
                if self.active_op.name is not None:
                    name = "cam_path_{}".format(self.active_op.name)
                    if bpy.context.scene.objects.get(name) is not None:
                        self.layout.operator("object.cam_export", text="Export Gcode ")
                self.layout.operator("object.cam_simulate", text="Simulate this operation")
            else:
                self.layout.label(text="operation invalid, can't compute")


    # Draw a list of objects which will be used as the source of the operation
    # FIXME Right now, cameras or lights may be used, which crashes
    # The user should only be able to choose meshes and curves
    def draw_operation_source(self):

        self.layout.prop(self.active_op, 'geometry_source')

        if self.active_op.strategy == 'CURVE':
            if self.active_op.geometry_source == 'OBJECT':
                self.layout.prop_search(self.active_op, "object_name", bpy.data, "objects")
            elif self.active_op.geometry_source == 'COLLECTION':
                self.layout.prop_search(self.active_op, "collection_name", bpy.data, "collections")
        else:
            if self.active_op.geometry_source == 'OBJECT':
                self.layout.prop_search(self.active_op, "object_name", bpy.data, "objects")
                if self.active_op.enable_A:
                    self.layout.prop(self.active_op, 'rotation_A')
                if self.active_op.enable_B:
                    self.layout.prop(self.active_op, 'rotation_B')

            elif self.active_op.geometry_source == 'COLLECTION':
                self.layout.prop_search(self.active_op, "collection_name", bpy.data, "collections")
            else:
                self.layout.prop_search(self.active_op, "source_image_name", bpy.data, "images")

        if self.active_op.strategy in ['CARVE', 'PROJECTED_CURVE']:
            self.layout.prop_search(self.active_op, "curve_object", bpy.data, "objects")
            if self.active_op.strategy == 'PROJECTED_CURVE':
                self.layout.prop_search(self.active_op, "curve_object1", bpy.data, "objects")

    # Draw Operation options:
    # Remove redundant points (optimizes operation)
    # Use modifiers of the object
    # Hide all other paths
    # Parent path to object (?)

    def draw_operation_options(self):

        # TODO This should be in some optimization menu
        if self.active_op.strategy != 'DRILL':
            self.layout.prop(self.active_op, 'remove_redundant_points')

        if self.active_op.remove_redundant_points:
            self.layout.label(text='Revise your Code before running!')
            self.layout.label(text='Quality will suffer if tolerance')
            self.layout.label(text='is high')
            self.layout.prop(self.active_op, 'simplify_tol')

        if self.active_op.geometry_source in ['OBJECT', 'COLLECTION']:
            self.layout.prop(self.active_op, 'use_modifiers')
        self.layout.prop(self.active_op, 'hide_all_others')
        self.layout.prop(self.active_op, 'parent_path_to_object')
