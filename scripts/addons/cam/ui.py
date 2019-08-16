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

import bpy
from bpy.types import UIList

from cam import simple
from cam.simple import *

# EXPERIMENTAL=True#False


####Panel definitions
class CAMButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.engine in cls.COMPAT_ENGINES


class CAM_CUTTER_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM cutter panel"""
    bl_label = " "
    bl_idname = "WORLD_PT_CAM_CUTTER"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw_header(self, context):
        self.layout.menu("CAM_CUTTER_presets", text="CAM Cutter")

    def draw(self, context):
        layout = self.layout
        d = bpy.context.scene
        if len(d.cam_operations) > 0:
            ao = d.cam_operations[d.cam_active_operation]

            if ao:
                # cutter preset
                row = layout.row(align=True)
                row.menu("CAM_CUTTER_presets", text=bpy.types.CAM_CUTTER_presets.bl_label)
                row.operator("render.cam_preset_cutter_add", text="", icon='ADD')
                row.operator("render.cam_preset_cutter_add", text="", icon='REMOVE').remove_active = True
                layout.prop(ao, 'cutter_id')
                layout.prop(ao, 'cutter_type')
                if ao.cutter_type == 'VCARVE':
                    layout.prop(ao, 'cutter_tip_angle')
                if ao.cutter_type == 'CUSTOM':
                    if ao.use_exact:
                        layout.label(text='Warning - only convex shapes are supported. ', icon='COLOR_RED')
                        layout.label(text='If your custom cutter is concave,')
                        layout.label(text='switch exact mode off.')

                    layout.prop_search(ao, "cutter_object_name", bpy.data, "objects")

                layout.prop(ao, 'cutter_diameter')
                # layout.prop(ao,'cutter_length')
                layout.prop(ao, 'cutter_flutes')
                layout.prop(ao, 'cutter_description')


class CAM_MACHINE_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM machine panel"""
    bl_label = " "
    bl_idname = "WORLD_PT_CAM_MACHINE"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw_header(self, context):
        self.layout.menu("CAM_MACHINE_presets", text="CAM Machine")

    def draw(self, context):
        layout = self.layout
        s = bpy.context.scene
        us = s.unit_settings

        ao = s.cam_machine

        if ao:
            use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

            # machine preset
            row = layout.row(align=True)
            row.menu("CAM_MACHINE_presets", text=bpy.types.CAM_MACHINE_presets.bl_label)
            row.operator("render.cam_preset_machine_add", text="", icon='ADD')
            row.operator("render.cam_preset_machine_add", text="", icon='REMOVE').remove_active = True
            # layout.prop(ao,'name')
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
            layout.prop(ao,
                        'feedrate_default')  # TODO: spindle default and feedrate default should become part of the cutter definition...
            layout.prop(ao, 'spindle_min')
            layout.prop(ao, 'spindle_max')
            layout.prop(ao, 'spindle_start_time')
            layout.prop(ao, 'spindle_default')

            if use_experimental:
                layout.prop(ao, 'axis4')
                layout.prop(ao, 'axis5')
                layout.prop(ao, 'collet_size')

                layout.prop(ao, 'output_block_numbers')
                if ao.output_block_numbers:
                    layout.prop(ao, 'start_block_number')
                    layout.prop(ao, 'block_number_increment')
                layout.prop(ao, 'output_tool_definitions')
                layout.prop(ao, 'output_tool_change')
                if ao.output_tool_change:
                    layout.prop(ao, 'output_g43_on_tool_change')


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
                # label(text='dir(layout))
                layout.template_running_jobs()
                if ao.geometry_source in ['OBJECT', 'GROUP']:
                    row = layout.row(align=True)
                    layout.prop(ao, 'material_from_model')

                    if ao.material_from_model:
                        layout.prop(ao, 'material_radius_around_model')
                    else:
                        layout.prop(ao, 'material_origin')
                        layout.prop(ao, 'material_size')

                    layout.operator("object.cam_position", text="Position object")
                else:
                    layout.label(text='Estimated from image')


class CAM_UL_operations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # assert(isinstance(item, bpy.types.VertexGroup)
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
        # assert(isinstance(item, bpy.types.VertexGroup)
        operation = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.label(text=item.name, translate=False, icon_value=icon)
        # icon = 'LOCKED' if operation.computing else 'UNLOCKED'
        # if operation.computing:
        #	layout.label(text=operation.outtext)#"computing" )
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class CAM_UL_chains(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # assert(isinstance(item, bpy.types.VertexGroup)
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
        # col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
        col.operator("scene.cam_chain_remove", icon='REMOVE', text="")
        # if group:
        # col.separator()
        # col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
        # col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
        # row = layout.row() 

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
                        layout.operator("object.calculate_cam_paths_chain", text="Calculate chain paths")
                        layout.operator("object.cam_export_paths_chain", text="Export chain gcode")
                        # layout.operator("object.calculate_cam_paths_background", text="Calculate path in background")
                        layout.operator("object.cam_simulate_chain", text="Simulate this chain")
                    else:
                        layout.label(text="chain invalid, can't compute")
                else:
                    layout.label(text='chain is currently computing')
                # layout.prop(ao,'computing')

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
        # if group:
        col.separator()
        col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
        # row = layout.row() 

        if len(scene.cam_operations) > 0:
            use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental
            ao = scene.cam_operations[scene.cam_active_operation]

            row = layout.row(align=True)
            row.menu("CAM_OPERATION_presets", text=bpy.types.CAM_OPERATION_presets.bl_label)
            row.operator("render.cam_preset_operation_add", text="", icon='ADD')
            row.operator("render.cam_preset_operation_add", text="", icon='REMOVE').remove_active = True

            if ao:
                if not ao.computing:
                    if ao.valid:
                        layout.operator("object.calculate_cam_path", text="Calculate path")
                        layout.operator("object.calculate_cam_paths_background", text="Calculate path in background")
                        if ao.name is not None:
                            name = "cam_path_{}".format(ao.name)
                            if scene.objects.get(name) is not None:
                                layout.operator("object.cam_export", text="Export gcode")
                        layout.operator("object.cam_simulate", text="Simulate this operation")


                    else:
                        layout.label(text="operation invalid, can't compute")
                else:
                    row = layout.row(align=True)
                    row.label(text='computing')
                    row.operator('object.kill_calculate_cam_paths_background', text="", icon='CANCEL')
                # layout.prop(ao,'computing')

                sub = layout.column()
                sub.active = not ao.computing

                sub.prop(ao, 'name')
                sub.prop(ao, 'filename')

                layout.prop(ao, 'auto_export')
                layout.prop(ao, 'geometry_source')
                if not ao.strategy == 'CURVE':
                    if ao.geometry_source == 'OBJECT':
                        layout.prop_search(ao, "object_name", bpy.data, "objects")
                    elif ao.geometry_source == 'GROUP':
                        layout.prop_search(ao, "group_name", bpy.data, "groups")
                    else:
                        layout.prop_search(ao, "source_image_name", bpy.data, "images")
                else:
                    if ao.geometry_source == 'OBJECT':
                        layout.prop_search(ao, "object_name", bpy.data, "objects")
                    elif ao.geometry_source == 'GROUP':
                        layout.prop_search(ao, "group_name", bpy.data, "groups")

                if ao.strategy in ['CARVE', 'PROJECTED_CURVE']:
                    layout.prop_search(ao, "curve_object", bpy.data, "objects")
                    if ao.strategy == 'PROJECTED_CURVE':
                        layout.prop_search(ao, "curve_object1", bpy.data, "objects")

                if use_experimental and ao.geometry_source in ['OBJECT', 'GROUP']:
                    layout.prop(ao, 'use_modifiers')
                layout.prop(ao, 'hide_all_others')
                layout.prop(ao, 'parent_path_to_object')


class CAM_INFO_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM info panel"""
    bl_label = "CAM info & warnings"
    bl_idname = "WORLD_PT_CAM_INFO"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        row = layout.row()
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.warnings != '':
                lines = ao.warnings.split('\n')
                for l in lines:
                    layout.label(text=l, icon='COLOR_RED')
            if ao.valid:
                if ao.duration > 0:
                    layout.label(text='operation time: ' + str(int(ao.duration / 60)) + \
                                      ' hour, ' + str(int(ao.duration) % 60) + ' min, ' + \
                                      str(int(ao.duration * 60) % 60) + ' sec.')
                layout.label(text='chipload: ' + strInUnits(ao.chipload, 4) + ' / tooth')


class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation properties panel"""
    bl_label = "CAM operation setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        row = layout.row()
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

                    # if ao.geometry_source=='OBJECT' or ao.geometry_source=='GROUP':
                    '''
                    o=bpy.data.objects[ao.object_name]
                    
                    if o.type=='MESH' and (ao.strategy=='DRILL'):
                        layout.label(text='Not supported for meshes')
                        return
                    '''
                # elif o.type=='CURVE' and (ao.strategy!='CARVE' and ao.strategy!='POCKET' and ao.strategy!='DRILL' and ao.strategy!='CUTOUT'):
                #	 layout.label(text='Not supported for curves')
                #	 return

                if ao.strategy == 'CUTOUT':
                    layout.prop(ao, 'cut_type')
                    # layout.prop(ao,'dist_between_paths')
                    if use_experimental:
                        layout.prop(ao, 'outlines_count')
                        if ao.outlines_count > 1:
                            layout.prop(ao, 'dist_between_paths')
                            layout.prop(ao, 'movement_insideout')
                    layout.prop(ao, 'dont_merge')
                elif ao.strategy == 'WATERLINE':
                    layout.prop(ao, 'slice_detail')
                    layout.prop(ao, 'waterline_fill')
                    if ao.waterline_fill:
                        layout.prop(ao, 'dist_between_paths')
                        layout.prop(ao, 'waterline_project')
                    layout.prop(ao, 'inverse')
                elif ao.strategy == 'CARVE':
                    layout.prop(ao, 'carve_depth')
                    layout.prop(ao, 'dist_along_paths')
                elif ao.strategy == 'PENCIL':
                    layout.prop(ao, 'dist_along_paths')
                    layout.prop(ao, 'pencil_threshold')
                elif ao.strategy == 'MEDIAL_AXIS':
                    layout.prop(ao, 'medial_axis_threshold')
                    layout.prop(ao, 'medial_axis_subdivision')
                elif ao.strategy == 'CRAZY':
                    layout.prop(ao, 'crazy_threshold1')
                    layout.prop(ao, 'crazy_threshold5')
                    layout.prop(ao, 'crazy_threshold2')
                    layout.prop(ao, 'crazy_threshold3')
                    layout.prop(ao, 'crazy_threshold4')
                    layout.prop(ao, 'dist_between_paths')
                    layout.prop(ao, 'dist_along_paths')
                elif ao.strategy == 'DRILL':
                    layout.prop(ao, 'drill_type')
                elif ao.strategy == 'POCKET':
                    layout.prop(ao, 'pocket_option')
                    layout.prop(ao, 'dist_between_paths')
                else:
                    layout.prop(ao, 'dist_between_paths')
                    layout.prop(ao, 'dist_along_paths')
                    if ao.strategy == 'PARALLEL' or ao.strategy == 'CROSS':
                        layout.prop(ao, 'parallel_angle')

                    layout.prop(ao, 'inverse')
                if ao.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
                    layout.prop(ao, 'use_bridges')
                    if ao.use_bridges:
                        # layout.prop(ao,'bridges_placement')
                        layout.prop(ao, 'bridges_width')
                        layout.prop(ao, 'bridges_height')

                        layout.prop_search(ao, "bridges_group_name", bpy.data, "groups")
                        layout.prop(ao, 'use_bridge_modifiers')
                    # layout.prop(ao,'bridges_group_name')
                    # if ao.bridges_placement == 'AUTO':
                    #	layout.prop(ao,'bridges_per_curve')
                    #	layout.prop(ao,'bridges_max_distance')
                    layout.operator("scene.cam_bridges_add", text="Autogenerate bridges")

            # elif ao.strategy=='SLICES':
            #	layout.prop(ao,'slice_detail')	
            # first attempt to draw object list for orientations:
            # layout.operator("object.cam_pack_objects")
            # layout.operator("scene.cam_orientation_add")
            # gname=ao.name+'_orientations'

            layout.prop(ao, 'skin')

            # if gname in bpy.data.groups:
            #	layout.label(text='orientations')
            #	group=bpy.data.groups[ao.name+'_orientations']
            #	layout.template_list("CAM_UL_orientations", '', group, "objects", ao, 'active_orientation')
            #	layout.prop(group.objects[ao.active_orientation],'location')
            #	layout.prop(group.objects[ao.active_orientation],'rotation_euler')
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

        row = layout.row()
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
                if ao.strategy == 'PARALLEL' or ao.strategy == 'CROSS':
                    if not ao.ramp:
                        layout.prop(ao, 'parallel_step_back')
                if ao.strategy == 'CUTOUT' or (
                        use_experimental and (ao.strategy == 'POCKET' or ao.strategy == 'MEDIAL_AXIS')):
                    layout.prop(ao, 'first_down')
                # if ao.first_down:

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
        row = layout.row()
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

        row = layout.row()
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                layout.prop(ao, 'optimize')
                if ao.optimize:
                    layout.prop(ao, 'optimize_threshold')
                if ao.geometry_source == 'OBJECT' or ao.geometry_source == 'GROUP':
                    exclude_exact = ao.strategy in ['WATERLINE', 'POCKET', 'CUTOUT', 'DRILL', 'PENCIL']
                    if not exclude_exact:
                        layout.prop(ao, 'use_exact')
                        if ao.use_exact:
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
                layout.prop(ao, 'use_opencamlib')
        # if not ao.use_exact:#this will be replaced with groups of objects.
        # layout.prop(ao,'render_all')# replaced with groups support


class CAM_AREA_Panel(CAMButtonsPanel, bpy.types.Panel):
    """CAM operation area panel"""
    bl_label = "CAM operation area "
    bl_idname = "WORLD_PT_CAM_OPERATION_AREA"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        row = layout.row()
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            ao = scene.cam_operations[scene.cam_active_operation]
            if ao.valid:
                # o=bpy.data.objects[ao.object_name]
                layout.prop(ao, 'use_layers')
                if ao.use_layers:
                    layout.prop(ao, 'stepdown')

                layout.prop(ao, 'ambient_behaviour')
                if ao.ambient_behaviour == 'AROUND':
                    layout.prop(ao, 'ambient_radius')

                layout.prop(ao, 'maxz')  # experimental
                if ao.geometry_source in ['OBJECT', 'GROUP']:
                    layout.prop(ao, 'minz_from_ob')
                    if not ao.minz_from_ob:
                        layout.prop(ao, 'minz')
                else:
                    layout.prop(ao, 'source_image_scale_z')
                    layout.prop(ao, 'source_image_size_x')
                    if ao.source_image_name != '':
                        i = bpy.data.images[ao.source_image_name]
                        if i is not None:
                            sy = int((ao.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000

                            layout.label(text='image size on y axis: ' + strInUnits(sy, 8))
                            # label(text='dir(layout))
                            layout.separator()
                    layout.prop(ao, 'source_image_offset')
                    col = layout.column(align=True)
                    # col.label(text='image crop:')
                    # col=layout.column()
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
        row = layout.row()
        if len(scene.cam_operations) == 0:
            layout.label(text='Add operation first')
        if len(scene.cam_operations) > 0:
            use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental
            if use_experimental:
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
        layout.prop(settings, 'rotate')


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
        layout.prop(settings, 'indexes')


# panel containing all tools
class VIEW3D_PT_tools_curvetools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Tools"

    # bl_category = "Blender CAM"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        # col = layout.column(align=True)
        # lt = context.window_manager.looptools
        layout.operator("object.curve_boolean")
        layout.operator("object.curve_intarsion")
        layout.operator("object.curve_overcuts")
        layout.operator("object.curve_overcuts_b")
        layout.operator("object.silhouete")
        layout.operator("object.silhouete_offset")
        layout.operator("object.curve_remove_doubles")
        layout.operator("object.mesh_get_pockets")
