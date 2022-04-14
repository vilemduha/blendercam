# blender CAM ui.py (c) 2012 Vilem Novak
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****
import sys
import bpy
from bpy.types import UIList, Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       PointerProperty,
                       FloatProperty,
                       )

from bpy.types import (Panel, Menu, Operator, PropertyGroup, )

from cam import gcodeimportparser, simple
from cam.simple import *

from cam.ui_panels.buttons_panel  import CAMButtonsPanel
from cam.ui_panels.info           import CAM_INFO_Panel
from cam.ui_panels.operations     import CAM_OPERATIONS_Panel
from cam.ui_panels.cutter         import CAM_CUTTER_Panel
from cam.ui_panels.machine        import CAM_MACHINE_Panel
from cam.ui_panels.material       import CAM_MATERIAL_Panel
from cam.ui_panels.chains         import CAM_UL_operations, CAM_UL_chains, CAM_CHAINS_Panel
from cam.ui_panels.op_properties  import CAM_OPERATION_PROPERTIES_Panel
from cam.ui_panels.movement       import CAM_MOVEMENT_Panel


class CAM_UL_orientations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.label(text=item.name, translate=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)



class CAM_FEEDRATE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM feedrate panel"""
    bl_label = "CAM feedrate"
    bl_idname = "WORLD_PT_CAM_FEEDRATE"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'feedrate')
                layout.prop(ao, 'do_simulation_feedrate')
                layout.prop(ao, 'plunge_feedrate')
                layout.prop(ao, 'plunge_angle')
                layout.prop(ao, 'spindle_rpm')


class CAM_OPTIMISATION_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM optimisation panel"""
    bl_label = "CAM optimisation"
    bl_idname = "WORLD_PT_CAM_OPTIMISATION"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'optimize')
                if ao.optimize:
                    layout.prop(ao, 'optimize_threshold')
                if ao.geometry_source == 'OBJECT' or ao.geometry_source == 'COLLECTION':
                    exclude_exact = ao.strategy in ['MEDIAL_AXIS', 'POCKET', 'WATERLINE', 'CUTOUT', 'DRILL', 'PENCIL',
                                                    'CURVE']
                    if not exclude_exact:
                        if not ao.use_exact:
                            layout.prop(ao, 'use_exact')
                            layout.label(text="Exact mode must be set for opencamlib to work ")

                        if "ocl" in sys.modules:
                            layout.label(text="Opencamlib is available ")
                            layout.prop(ao, 'use_opencamlib')
                        else:
                            layout.label(text="Opencamlib is NOT available ")
                            layout.prop(ao, 'exact_subdivide_edges')

                    if exclude_exact or not ao.use_exact:
                        layout.prop(ao, 'pixsize')
                        layout.prop(ao, 'imgres_limit')

                        sx = ao.max.x - ao.min.x
                        sy = ao.max.y - ao.min.y
                        resx = int(sx / ao.pixsize)
                        resy = int(sy / ao.pixsize)
                        l = 'resolution: ' + str(resx) + ' x ' + str(resy)
                        layout.label(text=l)

                layout.prop(ao, 'simulation_detail')
                layout.prop(ao, 'circle_detail')


class CAM_AREA_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation area panel"""
    bl_label = "CAM operation area "
    bl_idname = "WORLD_PT_CAM_OPERATION_AREA"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'use_layers')
                if ao.use_layers:
                    layout.prop(ao, 'stepdown')

                layout.prop(ao, 'ambient_behaviour')
                if ao.ambient_behaviour == 'AROUND':
                    layout.prop(ao, 'ambient_radius')

                layout.prop(ao, 'maxz')  # experimental
                if ao.maxz > ao.free_movement_height:
                    layout.prop(ao, 'free_movement_height')
                    layout.label(text='Depth start > Free movement')
                    layout.label(text='POSSIBLE COLLISION')
                if ao.geometry_source in ['OBJECT', 'COLLECTION']:
                    if ao.strategy == 'CURVE':
                        layout.label(text="cannot use depth from object using CURVES")

                    if not ao.minz_from_ob:
                        if not ao.minz_from_material:
                            layout.prop(ao, 'minz')
                        layout.prop(ao, 'minz_from_material')
                    if not ao.minz_from_material:
                        layout.prop(ao, 'minz_from_ob')
                else:
                    layout.prop(ao, 'source_image_scale_z')
                    layout.prop(ao, 'source_image_size_x')
                    if ao.source_image_name != '':
                        i = bpy.data.images[ao.source_image_name]
                        if i is not None:
                            sy = int((ao.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000

                            layout.label(text='image size on y axis: ' + strInUnits(sy, 8))
                            layout.separator()
                    layout.prop(ao, 'source_image_offset')
                    col = layout.column(align=True)
                    col.prop(ao, 'source_image_crop', text='Crop source image')
                    if ao.source_image_crop:
                        col.prop(ao, 'source_image_crop_start_x', text='start x')
                        col.prop(ao, 'source_image_crop_start_y', text='start y')
                        col.prop(ao, 'source_image_crop_end_x', text='end x')
                        col.prop(ao, 'source_image_crop_end_y', text='end y')
                layout.prop(ao, 'use_limit_curve')
                if ao.use_limit_curve:
                    layout.prop_search(ao, "limit_curve", bpy.data, "objects")
                layout.prop(ao, "ambient_cutter_restrict")


class CAM_GCODE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation g-code options panel"""
    bl_label = "CAM g-code options "
    bl_idname = "WORLD_PT_CAM_GCODE"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'output_header')

                if ao.output_header:
                    layout.prop(ao, 'gcode_header')
                layout.prop(ao, 'output_trailer')
                if ao.output_trailer:
                    layout.prop(ao, 'gcode_trailer')
                layout.prop(ao, 'enable_dust')
                if ao.enable_dust:
                    layout.prop(ao, 'gcode_start_dust_cmd')
                    layout.prop(ao, 'gcode_stop_dust_cmd')
                layout.prop(ao, 'enable_hold')
                if ao.enable_hold:
                    layout.prop(ao, 'gcode_start_hold_cmd')
                    layout.prop(ao, 'gcode_stop_hold_cmd')

            else:
                layout.label(text='Enable Show experimental features')
                layout.label(text='in Blender CAM Addon preferences')


class CAM_PACK_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM material panel"""
    bl_label = "Pack curves on sheet"
    bl_idname = "WORLD_PT_CAM_PACK"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        settings = scene.cam_pack
        layout.label(text='warning - algorithm is slow.')
        layout.label(text='only for curves now.')

        layout.operator("object.cam_pack_objects")
        layout.prop(settings, 'sheet_fill_direction')
        layout.prop(settings, 'sheet_x')
        layout.prop(settings, 'sheet_y')
        layout.prop(settings, 'distance')
        layout.prop(settings, 'tolerance')
        layout.prop(settings, 'rotate')
        if settings.rotate:
            layout.prop(settings, 'rotate_angle')


class CAM_SLICE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM slicer panel"""
    bl_label = "Slice model to plywood sheets"
    bl_idname = "WORLD_PT_CAM_SLICE"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        settings = scene.cam_slice

        layout.operator("object.cam_slice_objects")
        layout.prop(settings, 'slice_distance')
        layout.prop(settings, 'slice_above0')
        layout.prop(settings, 'slice_3d')
        layout.prop(settings, 'indexes')


# panel containing all tools

class VIEW3D_PT_tools_curvetools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_boolean")
        layout.operator("object.convex_hull")
        layout.operator("object.curve_intarsion")
        layout.operator("object.curve_overcuts")
        layout.operator("object.curve_overcuts_b")
        layout.operator("object.silhouete")
        layout.operator("object.silhouete_offset")
        layout.operator("object.curve_remove_doubles")
        layout.operator("object.mesh_get_pockets")


class VIEW3D_PT_tools_create(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Creators"
    bl_option = 'DEFAULT_CLOSED'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_plate")
        layout.operator("object.curve_drawer")
        layout.operator("object.curve_mortise")
        layout.operator("object.curve_interlock")
        layout.operator("object.curve_puzzle")
        layout.operator("object.sine")
        layout.operator("object.lissajous")
        layout.operator("object.hypotrochoid")
        layout.operator("object.customcurve")
        layout.operator("object.curve_hatch")
        layout.operator("object.curve_gear")
        layout.operator("object.curve_flat_cone")

# Gcode import panel---------------------------------------------------------------
# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------


class CustomPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Import Gcode"
    bl_idname = "OBJECT_PT_importgcode"

    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT',
                                'EDIT_MESH'}  # with this poll addon is visibly even when no object is selected

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        isettings = scene.cam_import_gcode
        layout.prop(isettings, 'output')
        layout.prop(isettings, "split_layers")

        layout.prop(isettings, "subdivide")
        col = layout.column(align=True)
        col = col.row(align=True)
        col.split()
        col.label(text="Segment length")

        col.prop(isettings, "max_segment_size")
        col.enabled = isettings.subdivide
        col.separator()

        col = layout.column()
        col.scale_y = 2.0
        col.operator("wm.gcode_import")


class WM_OT_gcode_import(Operator, ImportHelper):
    """Import Gcode, travel lines don't get drawn"""
    bl_idname = "wm.gcode_import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Gcode"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        print(self.filepath)
        return gcodeimportparser.import_gcode(context, self.filepath)
