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


# EXPERIMENTAL=True#False


# Panel definitions
class CAMButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.engine in cls.COMPAT_ENGINES


# Displays percentage of the cutter which is engaged with the material
# Displays a warning for engagements greater than 50%
def EngagementDisplay(operat, layout):
    ao = operat

    if ao.cutter_type == 'BALLCONE':
        if ao.dist_between_paths > ao.ball_radius:
            layout.label(text="CAUTION: CUTTER ENGAGEMENT")
            layout.label(text="GREATER THAN 50%")
        layout.label(text="Cutter engagement: " + str(round(100 * ao.dist_between_paths / ao.ball_radius, 1)) + "%")
    else:
        if ao.dist_between_paths > ao.cutter_diameter / 2:
            layout.label(text="CAUTION: CUTTER ENGAGEMENT")
            layout.label(text="GREATER THAN 50%")
        layout.label(text="Cutter Engagement: " + str(round(100 * ao.dist_between_paths / ao.cutter_diameter, 1)) + "%")


class CAM_CUTTER_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM cutter panel"""
    bl_label = " "
    bl_idname = "WORLD_PT_CAM_CUTTER"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw_header(self, context):
        self.layout.menu("CAM_CUTTER_MT_presets", text="CAM Cutter")

    def draw(self, context):
        layout = self.layout
        d = bpy.context.scene
        if len(d.cam_operations) > 0:
            ao = d.cam_operations[d.cam_active_operation]

            if ao:
                # cutter preset
                row = layout.row(align=True)
                row.menu("CAM_CUTTER_MT_presets", text=bpy.types.CAM_CUTTER_MT_presets.bl_label)
                row.operator("render.cam_preset_cutter_add", text="", icon='ADD')
                row.operator("render.cam_preset_cutter_add", text="", icon='REMOVE').remove_active = True
                layout.prop(ao, 'cutter_id')
                layout.prop(ao, 'cutter_type')
                if ao.cutter_type == 'VCARVE':
                    layout.prop(ao, 'cutter_tip_angle')
                if ao.cutter_type == 'BALLCONE':
                    layout.prop(ao, 'ball_radius')
                    EngagementDisplay(ao, layout)
                    layout.prop(ao, 'cutter_tip_angle')
                    layout.label(text='Cutter diameter = shank diameter')
                if ao.cutter_type == 'CYLCONE':
                    layout.prop(ao, 'cylcone_diameter')
                    EngagementDisplay(ao, layout)
                    layout.prop(ao, 'cutter_tip_angle')
                    layout.label(text='Cutter diameter = shank diameter')
                if ao.cutter_type == 'BULLNOSE':
                    layout.prop(ao, 'bull_corner_radius')
                    EngagementDisplay(ao, layout)
                    layout.label(text='Cutter diameter = shank diameter')

                if ao.cutter_type == 'LASER':
                    layout.prop(ao, 'Laser_on')
                    layout.prop(ao, 'Laser_off')
                    layout.prop(ao, 'Laser_cmd')
                    layout.prop(ao, 'Laser_delay')

                if ao.cutter_type == 'PLASMA':
                    layout.prop(ao, 'Plasma_on')
                    layout.prop(ao, 'Plasma_off')
                    layout.prop(ao, 'Plasma_delay')
                    layout.prop(ao, 'Plasma_dwell')
                    layout.prop(ao, 'lead_in')
                    layout.prop(ao, 'lead_out')

                if ao.cutter_type == 'CUSTOM':
                    if ao.use_exact:
                        layout.label(text='Warning - only convex shapes are supported. ', icon='COLOR_RED')
                        layout.label(text='If your custom cutter is concave,')
                        layout.label(text='switch exact mode off.')

                    layout.prop_search(ao, "cutter_object_name", bpy.data, "objects")

                layout.prop(ao, 'cutter_diameter')
                if ao.strategy == "POCKET" or ao.strategy == "PARALLEL" or ao.strategy == "CROSS" \
                        or ao.strategy == "WATERLINE":
                    EngagementDisplay(ao, layout)
                if ao.cutter_type != "LASER":
                    layout.prop(ao, 'cutter_flutes')
                layout.prop(ao, 'cutter_description')


class CAM_MACHINE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM machine panel"""
    bl_label = " "
    bl_idname = "WORLD_PT_CAM_MACHINE"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw_header(self, context):
        self.layout.menu("CAM_MACHINE_MT_presets", text="CAM Machine")

    def draw(self, context):
        layout = self.layout
        s = bpy.context.scene
        us = s.unit_settings

        ao = s.cam_machine

        if ao:
            use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

            # machine preset
            row = layout.row(align=True)
            row.menu("CAM_MACHINE_MT_presets", text=bpy.types.CAM_MACHINE_MT_presets.bl_label)
            row.operator("render.cam_preset_machine_add", text="", icon='ADD')
            row.operator("render.cam_preset_machine_add", text="", icon='REMOVE').remove_active = True
            layout.prop(ao, 'post_processor')
            layout.prop(ao, 'eval_splitting')
            if ao.eval_splitting:
                layout.prop(ao, 'split_limit')

            layout.prop(us, 'system')

            layout.prop(ao, 'use_position_definitions')
            if ao.use_position_definitions:
                layout.prop(ao, 'starting_position')
                layout.prop(ao, 'mtc_position')
                layout.prop(ao, 'ending_position')
            layout.prop(ao, 'working_area')
            layout.prop(ao, 'feedrate_min')
            layout.prop(ao, 'feedrate_max')
            layout.prop(ao, 'feedrate_default')
            # TODO: spindle default and feedrate default should become part of the cutter definition...
            layout.prop(ao, 'spindle_min')
            layout.prop(ao, 'spindle_max')
            layout.prop(ao, 'spindle_start_time')
            layout.prop(ao, 'spindle_default')
            layout.prop(ao, 'output_tool_definitions')
            layout.prop(ao, 'output_tool_change')
            if ao.output_tool_change:
                layout.prop(ao, 'output_g43_on_tool_change')

            if use_experimental:
                layout.prop(ao, 'axis4')
                layout.prop(ao, 'axis5')
                layout.prop(ao, 'collet_size')

                layout.prop(ao, 'output_block_numbers')
                if ao.output_block_numbers:
                    layout.prop(ao, 'start_block_number')
                    layout.prop(ao, 'block_number_increment')
            layout.prop(ao, 'hourly_rate')


class CAM_MATERIAL_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM material panel"""
    bl_label = "CAM Material size and position"
    bl_idname = "WORLD_PT_CAM_MATERIAL"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao:
                layout.template_running_jobs()
                if ao.geometry_source in ['OBJECT', 'COLLECTION']:
                    layout.prop(ao, 'material_from_model')

                    if ao.material_from_model:
                        layout.prop(ao, 'material_radius_around_model')
                    else:
                        layout.prop(ao, 'material_origin')
                        layout.prop(ao, 'material_size')

                    layout.prop(ao, 'material_center_x')
                    layout.prop(ao, 'material_center_y')
                    layout.prop(ao, 'material_Z')
                    layout.operator("object.cam_position", text="Position object")
                else:
                    layout.label(text='Estimated from image')


class CAM_UL_operations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        operation = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.label(text=item.name, translate=False, icon_value=icon)
            icon = 'LOCKED' if operation.computing else 'UNLOCKED'
            if operation.computing:
                layout.label(text=operation.outtext)  # "computing" )
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class CAM_UL_orientations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.label(text=item.name, translate=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class CAM_UL_chains(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        chain = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.label(text=item.name, translate=False, icon_value=icon)
            icon = 'LOCKED' if chain.computing else 'UNLOCKED'
            if chain.computing:
                layout.label(text="computing")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class CAM_CHAINS_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM chains panel"""
    bl_label = "CAM chains"
    bl_idname = "WORLD_PT_CAM_CHAINS"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        scene = bpy.context.scene

        row.template_list("CAM_UL_chains", '', scene, "cam_chains", scene, 'cam_active_chain')
        col = row.column(align=True)
        col.operator("scene.cam_chain_add", icon='ADD', text="")
        col.operator("scene.cam_chain_remove", icon='REMOVE', text="")

        if len(scene.cam_chains) > 0:
            chain = scene.cam_chains[scene.cam_active_chain]
            row = layout.row(align=True)

            if chain:
                row.template_list("CAM_UL_operations", '', chain, "operations", chain, 'active_operation')
                col = row.column(align=True)
                col.operator("scene.cam_chain_operation_add", icon='ADD', text="")
                col.operator("scene.cam_chain_operation_remove", icon='REMOVE', text="")
                if len(chain.operations) > 0:
                    col.operator("scene.cam_chain_operation_up", icon='TRIA_UP', text="")
                    col.operator("scene.cam_chain_operation_down", icon='TRIA_DOWN', text="")

                if not chain.computing:
                    if chain.valid:
                        pass
                        layout.operator("object.calculate_cam_paths_chain", text="Calculate chain paths & Export Gcode")
                        layout.operator("object.cam_export_paths_chain", text="Export chain gcode")
                        layout.operator("object.cam_simulate_chain", text="Simulate this chain")
                    else:
                        layout.label(text="chain invalid, can't compute")
                else:
                    layout.label(text='chain is currently computing')

                layout.prop(chain, 'name')
                layout.prop(chain, 'filename')


class CAM_OPERATIONS_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operations panel"""
    bl_label = "CAM operations"
    bl_idname = "WORLD_PT_CAM_OPERATIONS"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        scene = bpy.context.scene
        row.template_list("CAM_UL_operations", '', scene, "cam_operations", scene, 'cam_active_operation')
        col = row.column(align=True)
        col.operator("scene.cam_operation_add", icon='ADD', text="")
        col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
        col.operator("scene.cam_operation_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if len(scene.cam_operations) > 0:
            use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental
            ao = scene.cam_operations[scene.cam_active_operation]

            row = layout.row(align=True)
            row.menu("CAM_OPERATION_MT_presets", text=bpy.types.CAM_OPERATION_MT_presets.bl_label)
            row.operator("render.cam_preset_operation_add", text="", icon='ADD')
            row.operator("render.cam_preset_operation_add", text="", icon='REMOVE').remove_active = True

            if ao:
                if not ao.computing:
                    if ao.valid:
                        layout.operator("object.calculate_cam_path", text="Calculate path & export Gcode")
                        if ao.name is not None:
                            name = "cam_path_{}".format(ao.name)
                            if scene.objects.get(name) is not None:
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
                if not ao.strategy == 'CURVE':
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
                else:
                    if ao.geometry_source == 'OBJECT':
                        layout.prop_search(ao, "object_name", bpy.data, "objects")
                    elif ao.geometry_source == 'COLLECTION':
                        layout.prop_search(ao, "collection_name", bpy.data, "collections")

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


class CAM_INFO_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM info panel"""
    bl_label = "CAM info & warnings"
    bl_idname = "WORLD_PT_CAM_INFO"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        self.scene = bpy.context.scene

        self.draw_opencamlib_version()

        if len(self.scene.cam_operations) > 0:
            self.draw_active_op_warnings()
            self.draw_active_op_data()
            self.draw_active_op_money_cost()
        else:
            self.layout.label(text='No CAM operation created')

    def draw_opencamlib_version(self):
        if "ocl" in sys.modules:
            #TODO: Display Opencamlib's version
            self.layout.label(text = "Opencamlib installed")
        else:
            self.layout.label(text = "Opencamlib is not installed")

    def draw_active_op_warnings(self):
        active_op = self.scene.cam_operations[self.scene.cam_active_operation]
        if active_op.warnings != '':
            for line in active_op.warnings.split('\n'):
                self.layout.label(text=line, icon='COLOR_RED')

    def draw_active_op_data(self):
        active_op = self.scene.cam_operations[self.scene.cam_active_operation]
        if not active_op.valid: return
        if not int(active_op.duration*60) > 0: return

        active_op_time_text = "Operation Time: %d s " % int(active_op.duration*60)
        if active_op.duration > 60:
            active_op_time_text += " (%d h %d min)" % (int(active_op.duration / 60), round(active_op.duration % 60))
        elif active_op.duration > 1:
            active_op_time_text += " (%d min)" % round(active_op.duration % 60)

        self.layout.label(text = active_op_time_text)

        self.layout.label(text="Chipload: %s/tooth" % strInUnits(active_op.chipload, 4))


    def draw_active_op_money_cost(self):
        active_op = self.scene.cam_operations[self.scene.cam_active_operation]
        if not active_op.valid: return
        if not int(active_op.duration*60) > 0: return

        self.layout.prop(self.scene.cam_machine, 'hourly_rate')
        if float(self.scene.cam_machine.hourly_rate) < 0.01: return

        cost_per_second = self.scene.cam_machine.hourly_rate / 3600
        active_op_cost = 'Operation cost: $' + str(round((active_op.duration * 60 * cost_per_second), 2))
        self.layout.label(text='Cost per second:' + str(round(cost_per_second, 3)))
        self.layout.label(text=active_op_cost)





class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation properties panel"""
    bl_label = "CAM operation setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                if use_experimental:
                    layout.prop(ao, 'machine_axes')
                if ao.machine_axes == '3':
                    layout.prop(ao, 'strategy')
                elif ao.machine_axes == '4':
                    layout.prop(ao, 'strategy4axis')
                    if ao.strategy4axis == 'INDEXED':
                        layout.prop(ao, 'strategy')
                    layout.prop(ao, 'rotary_axis_1')

                elif ao.machine_axes == '5':
                    layout.prop(ao, 'strategy5axis')
                    if ao.strategy5axis == 'INDEXED':
                        layout.prop(ao, 'strategy')
                    layout.prop(ao, 'rotary_axis_1')
                    layout.prop(ao, 'rotary_axis_2')

                if ao.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'OUTLINEFILL']:
                    layout.prop(ao, 'movement_insideout')

                if ao.strategy in ['CUTOUT', 'CURVE']:
                    if ao.strategy == 'CUTOUT':
                        layout.prop(ao, 'cut_type')
                        layout.label(text="Overshoot works best with curve")
                        layout.label(text="having C remove doubles")
                        layout.prop(ao, 'straight')
                        layout.prop(ao, 'profile_start')
                        layout.label(text="Lead in / out not fully working")
                        layout.prop(ao, 'lead_in')
                        layout.prop(ao, 'lead_out')
                    layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')

                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')

                    layout.prop(ao, 'outlines_count')
                    if ao.outlines_count > 1:
                        layout.prop(ao, 'dist_between_paths')
                        EngagementDisplay(ao, layout)
                        layout.prop(ao, 'movement_insideout')
                    layout.prop(ao, 'dont_merge')

                elif ao.strategy == 'WATERLINE':
                    if ao.waterline_fill:
                        layout.label(text="Waterline roughing strategy")
                        layout.label(text="needs a skin margin")
                        layout.prop(ao, 'skin')
                        layout.prop(ao, 'dist_between_paths')
                        EngagementDisplay(ao, layout)
                        layout.prop(ao, 'stepdown')
                        layout.prop(ao, 'waterline_project')
                elif ao.strategy == 'CARVE':
                    layout.prop(ao, 'carve_depth')
                    layout.prop(ao, 'dist_along_paths')
                elif ao.strategy == 'MEDIAL_AXIS':
                    layout.prop(ao, 'medial_axis_threshold')
                    layout.prop(ao, 'medial_axis_subdivision')
                    layout.prop(ao, 'add_pocket_for_medial')
                    layout.prop(ao, 'add_mesh_for_medial')
                elif ao.strategy == 'DRILL':
                    layout.prop(ao, 'drill_type')
                    layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')
                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')

                elif ao.strategy == 'POCKET':
                    layout.prop(ao, 'pocket_option')
                    layout.prop(ao, 'pocketToCurve')
                    layout.prop(ao, 'dist_between_paths')
                    EngagementDisplay(ao, layout)
                    layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')
                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')
                else:
                    layout.prop(ao, 'dist_between_paths')
                    EngagementDisplay(ao, layout)
                    layout.prop(ao, 'dist_along_paths')
                    if ao.strategy == 'PARALLEL' or ao.strategy == 'CROSS':
                        layout.prop(ao, 'parallel_angle')
                        layout.prop(ao, 'enable_A')
                    if ao.enable_A:
                        layout.prop(ao, 'rotation_A')
                        layout.prop(ao, 'A_along_x')
                        if ao.A_along_x:
                            layout.label(text='A || X - B || Y')
                        else:
                            layout.label(text='A || Y - B ||X')
                    layout.prop(ao, 'enable_B')
                    if ao.enable_B:
                        layout.prop(ao, 'rotation_B')

                    layout.prop(ao, 'inverse')
                if ao.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
                    layout.prop(ao, 'use_bridges')
                    if ao.use_bridges:
                        layout.prop(ao, 'bridges_width')
                        layout.prop(ao, 'bridges_height')

                        layout.prop_search(ao, "bridges_collection_name", bpy.data, "collections")
                        layout.prop(ao, 'use_bridge_modifiers')
                    layout.operator("scene.cam_bridges_add", text="Autogenerate bridges")

            layout.prop(ao, 'skin')

            if ao.machine_axes == '3':
                layout.prop(ao, 'array')
                if ao.array:
                    layout.prop(ao, 'array_x_count')
                    layout.prop(ao, 'array_x_distance')
                    layout.prop(ao, 'array_y_count')
                    layout.prop(ao, 'array_y_distance')


class CAM_MOVEMENT_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM movement panel"""
    bl_label = "CAM movement"
    bl_idname = "WORLD_PT_CAM_MOVEMENT"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'movement_type')

                if ao.movement_type in ['BLOCK', 'SPIRAL', 'CIRCLES']:
                    layout.prop(ao, 'movement_insideout')

                layout.prop(ao, 'spindle_rotation_direction')
                layout.prop(ao, 'free_movement_height')
                if ao.maxz > ao.free_movement_height:
                    layout.label(text='Depth start > Free movement')
                    layout.label(text='POSSIBLE COLLISION')
                layout.prop(ao, 'useG64')
                if ao.useG64:
                    layout.prop(ao, 'G64')
                if ao.strategy == 'PARALLEL' or ao.strategy == 'CROSS':
                    if not ao.ramp:
                        layout.prop(ao, 'parallel_step_back')
                if ao.strategy == 'CUTOUT' or ao.strategy == 'POCKET' or ao.strategy == 'MEDIAL_AXIS':
                    layout.prop(ao, 'first_down')

                if ao.strategy == 'POCKET':
                    layout.prop(ao, 'helix_enter')
                    if ao.helix_enter:
                        layout.prop(ao, 'ramp_in_angle')
                        layout.prop(ao, 'helix_diameter')
                    layout.prop(ao, 'retract_tangential')
                    if ao.retract_tangential:
                        layout.prop(ao, 'retract_radius')
                        layout.prop(ao, 'retract_height')

                layout.prop(ao, 'ramp')
                if ao.ramp:
                    layout.prop(ao, 'ramp_in_angle')
                    layout.prop(ao, 'ramp_out')
                    if ao.ramp_out:
                        layout.prop(ao, 'ramp_out_angle')

                layout.prop(ao, 'stay_low')
                if ao.stay_low:
                    layout.prop(ao, 'merge_dist')
                if ao.cutter_type != 'BALLCONE':
                    layout.prop(ao, 'protect_vertical')
                if ao.protect_vertical:
                    layout.prop(ao, 'protect_vertical_limit')


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
