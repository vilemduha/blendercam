"""BlenderCAM 'operations.py'

'CAM Operations' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel

# Operations panel
# This panel displays the list of operations created by the user
# Functionnalities are:
# - list Operations
# - create/delete/duplicate/reorder operations
# - display preset operations
#
# For each operation, generate the corresponding gcode and export the gcode file


class CAM_OPERATIONS_Panel(CAMButtonsPanel, Panel):
    """CAM Operations Panel"""
    bl_label = "CAM Operations"
    bl_idname = "WORLD_PT_CAM_OPERATIONS"
    always_show_panel = True
    panel_interface_level = 0

    prop_level = {
        'draw_presets': 1,
        'draw_operations_list': 0,
        'draw_calculate_path': 0,
        'draw_export_gcode': 1,
        'draw_simulate_op': 1,
        'draw_op_name': 1,
        'draw_op_filename': 0,
        'draw_operation_source': 0
    }

    # Draw the list of operations and the associated buttons:
    # create, delete, duplicate, reorder
    def draw_operations_list(self):
        row = self.layout.row()
        row.template_list("CAM_UL_operations", '', bpy.context.scene,
                          "cam_operations", bpy.context.scene, 'cam_active_operation')
        col = row.column(align=True)
        col.operator("scene.cam_operation_add", icon='ADD', text="")
        col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
        col.operator("scene.cam_operation_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

    # Draw the list of preset operations, and preset add and remove buttons

    def draw_presets(self):
        if not self.has_correct_level():
            return
        row = self.layout.row(align=True)
        row.menu("CAM_OPERATION_MT_presets", text=bpy.types.CAM_OPERATION_MT_presets.bl_label)
        row.operator("render.cam_preset_operation_add", text="", icon='ADD')
        row.operator("render.cam_preset_operation_add", text="", icon='REMOVE').remove_active = True

    def draw_calculate_path(self):
        if not self.has_correct_level():
            return
        if self.op.maxz > self.op.movement.free_height:
            self.layout.label(text='!ERROR! COLLISION!')
            self.layout.label(text='Depth Start > Free Movement Height')
            self.layout.label(text='!ERROR! COLLISION!')
            self.layout.prop(self.op.movement, 'free_height')

        if not self.op.valid:
            self.layout.label(text="Select a Valid Object to Calculate the Path.")
        # will be disable if not valid
        self.layout.operator("object.calculate_cam_path", text="Calculate Path & Export Gcode")

    def draw_export_gcode(self):
        if not self.has_correct_level():
            return
        if self.op.valid:
            if self.op.name is not None:
                name = f"cam_path_{self.op.name}"
                if bpy.context.scene.objects.get(name) is not None:
                    self.layout.operator("object.cam_export", text="Export Gcode ")

    def draw_simulate_op(self):
        if not self.has_correct_level():
            return
        if self.op.valid:
            self.layout.operator("object.cam_simulate", text="Simulate This Operation")

    def draw_op_name(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'name')

    def draw_op_filename(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'filename')

    # Draw a list of objects which will be used as the source of the operation
    # FIXME Right now, cameras or lights may be used, which crashes
    # The user should only be able to choose meshes and curves

    def draw_operation_source(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op, 'geometry_source')

        if self.op.strategy == 'CURVE':
            if self.op.geometry_source == 'OBJECT':
                self.layout.prop_search(self.op, "object_name", bpy.data, "objects")
            elif self.op.geometry_source == 'COLLECTION':
                self.layout.prop_search(self.op, "collection_name", bpy.data, "collections")
        else:
            if self.op.geometry_source == 'OBJECT':
                self.layout.prop_search(self.op, "object_name", bpy.data, "objects")
                if self.op.enable_A:
                    self.layout.prop(self.op, 'rotation_A')
                if self.op.enable_B:
                    self.layout.prop(self.op, 'rotation_B')

            elif self.op.geometry_source == 'COLLECTION':
                self.layout.prop_search(self.op, "collection_name", bpy.data, "collections")
            else:
                self.layout.prop_search(self.op, "source_image_name", bpy.data, "images")

        if self.op.strategy in ['CARVE', 'PROJECTED_CURVE']:
            self.layout.prop_search(self.op, "curve_object", bpy.data, "objects")
            if self.op.strategy == 'PROJECTED_CURVE':
                self.layout.prop_search(self.op, "curve_object1", bpy.data, "objects")

    def draw(self, context):
        self.context = context

        self.draw_presets()
        self.draw_operations_list()

        if self.op is None:
            return

        self.draw_calculate_path()
        self.draw_export_gcode()
        self.draw_simulate_op()
        self.draw_op_name()
        self.draw_op_filename()
        self.draw_operation_source()
