# blender CAM __init__.py (c) 2012 Vilem Novak
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

import bgl
import bl_operators
import blf
import bpy
import math
import numpy
import os
import pickle
import subprocess
import sys
import threading
import time
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import Menu, Operator, UIList, AddonPreferences
from bpy_extras.object_utils import object_data_add
from cam import ui, ops, curvecamtools, curvecamequation, curvecamcreate, utils, simple, \
    polygon_utils_cam  # , post_processors
from mathutils import *
from shapely import geometry as sgeometry

bl_info = {
    "name": "CAM - gcode generation tools",
    "author": "Vilem Novak",
    "version": (0, 9, 3),
    "blender": (2, 80, 0),
    "location": "Properties > render",
    "description": "Generate machining paths for CNC",
    "warning": "there is no warranty for the produced gcode by now",
    "wiki_url": "https://github.com/vilemduha/blendercam/wiki",
    "tracker_url": "",
    "category": "Scene"}

PRECISION = 5

was_hidden_dict = {}


def updateMachine(self, context):
    print('update machine ')
    utils.addMachineAreaObject()


def updateMaterial(self, context):
    print('update material')
    utils.addMaterialAreaObject()


def updateOperation(self, context):
    scene = context.scene
    ao = scene.cam_operations[scene.cam_active_operation]

    if ao.hide_all_others:
        for _ao in scene.cam_operations:
            if _ao.path_object_name in bpy.data.objects:
                other_obj = bpy.data.objects[_ao.path_object_name]
                current_obj = bpy.data.objects[ao.path_object_name]
                if other_obj != current_obj:
                    other_obj.hide = True
                    other_obj.select = False
    else:
        for path_obj_name in was_hidden_dict:
            print(was_hidden_dict)
            if was_hidden_dict[path_obj_name]:
                # Find object and make it hidde, then reset 'hidden' flag
                obj = bpy.data.objects[path_obj_name]
                obj.hide = True
                obj.select = False
                was_hidden_dict[path_obj_name] = False

    # try highlighting the object in the 3d view and make it active
    bpy.ops.object.select_all(action='DESELECT')
    # highlight the cutting path if it exists
    try:
        ob = bpy.data.objects[ao.path_object_name]
        ob.select_set(state=True, view_layer=None)
        # Show object if, it's was hidden
        if ob.hide:
            ob.hide = False
            was_hidden_dict[ao.path_object_name] = True
        bpy.context.scene.objects.active = ob
    except Exception as e:
        print(e)


class CamAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    experimental: BoolProperty(
        name="Show experimental features",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Use experimental features when you want to help development of Blender CAM:")

        layout.prop(self, "experimental")


class machineSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    # name = bpy.props.StringProperty(name="Machine Name", default="Machine")
    post_processor: EnumProperty(name='Post processor',
                                 items=(('ISO', 'Iso', 'exports standardized gcode ISO 6983 (RS-274)'),
                                        ('MACH3', 'Mach3', 'default mach3'),
                                        ('EMC', 'LinuxCNC - EMC2', 'Linux based CNC control software - formally EMC2'),
                                        ('FADAL', 'Fadal', 'Fadal VMC'),
                                        ('GRBL', 'grbl',
                                         'optimized gcode for grbl firmware on Arduino with cnc shield'),
                                        ('HEIDENHAIN', 'Heidenhain', 'heidenhain'),
                                        ('HEIDENHAIN530', 'Heidenhain530', 'heidenhain530'),
                                        ('TNC151', 'Heidenhain TNC151',
                                         'Post Processor for the Heidenhain TNC151 machine'),
                                        ('SIEGKX1', 'Sieg KX1', 'Sieg KX1'),
                                        ('HM50', 'Hafco HM-50', 'Hafco HM-50'),
                                        ('CENTROID', 'Centroid M40', 'Centroid M40'),
                                        ('ANILAM', 'Anilam Crusader M', 'Anilam Crusader M'),
                                        ('GRAVOS', 'Gravos', 'Gravos'),
                                        ('WIN-PC', 'WinPC-NC', 'German CNC by Burkhard Lewetz'),
                                        ('SHOPBOT MTC', 'ShopBot MTC', 'ShopBot MTC'),
                                        ('LYNX_OTTER_O', 'Lynx Otter o', 'Lynx Otter o')),
                                 description='Post processor',
                                 default='MACH3')
    # units = EnumProperty(name='Units', items = (('IMPERIAL', ''))
    # position definitions:
    use_position_definitions: bpy.props.BoolProperty(name="Use position definitions",
                                                     description="Define own positions for op start, "
                                                                 "toolchange, ending position",
                                                     default=False)
    starting_position: bpy.props.FloatVectorProperty(name='Start position', default=(0, 0, 0), unit='LENGTH',
                                                     precision=PRECISION, subtype="XYZ", update=updateMachine)
    mtc_position: bpy.props.FloatVectorProperty(name='MTC position', default=(0, 0, 0), unit='LENGTH',
                                                precision=PRECISION, subtype="XYZ", update=updateMachine)
    ending_position: bpy.props.FloatVectorProperty(name='End position', default=(0, 0, 0), unit='LENGTH',
                                                   precision=PRECISION, subtype="XYZ", update=updateMachine)

    working_area: bpy.props.FloatVectorProperty(name='Work Area', default=(0.500, 0.500, 0.100), unit='LENGTH',
                                                precision=PRECISION, subtype="XYZ", update=updateMachine)
    feedrate_min: bpy.props.FloatProperty(name="Feedrate minimum /min", default=0.0, min=0.00001, max=320000,
                                          precision=PRECISION, unit='LENGTH')
    feedrate_max: bpy.props.FloatProperty(name="Feedrate maximum /min", default=2, min=0.00001, max=320000,
                                          precision=PRECISION, unit='LENGTH')
    feedrate_default: bpy.props.FloatProperty(name="Feedrate default /min", default=1.5, min=0.00001, max=320000,
                                              precision=PRECISION, unit='LENGTH')
    hourly_rate: bpy.props.FloatProperty(name="Price per hour", default=100, min=0.005, precision=2)

    # UNSUPPORTED:

    spindle_min: bpy.props.FloatProperty(name="Spindle speed minimum RPM", default=5000, min=0.00001, max=320000,
                                         precision=1)
    spindle_max: bpy.props.FloatProperty(name="Spindle speed maximum RPM", default=30000, min=0.00001, max=320000,
                                         precision=1)
    spindle_default: bpy.props.FloatProperty(name="Spindle speed default RPM", default=15000, min=0.00001, max=320000,
                                             precision=1)
    spindle_start_time: bpy.props.FloatProperty(name="Spindle start delay seconds",
                                                description='Wait for the spindle to start spinning before starting '
                                                            'the feeds , in seconds',
                                                default=0, min=0.0000, max=320000, precision=1)

    axis4: bpy.props.BoolProperty(name="#4th axis", description="Machine has 4th axis", default=0)
    axis5: bpy.props.BoolProperty(name="#5th axis", description="Machine has 5th axis", default=0)

    eval_splitting: bpy.props.BoolProperty(name="Split files",
                                           description="split gcode file with large number of operations",
                                           default=True)  # split large files
    split_limit: IntProperty(name="Operations per file",
                             description="Split files with larger number of operations than this", min=1000,
                             max=20000000, default=800000)

    # rotary_axis1 = EnumProperty(name='Axis 1',
    #     items=(
    #         ('X', 'X', 'x'),
    #         ('Y', 'Y', 'y'),
    #         ('Z', 'Z', 'z')),
    #     description='Number 1 rotational axis',
    #     default='X', update = updateOffsetImage)

    collet_size: bpy.props.FloatProperty(name="#Collet size", description="Collet size for collision detection",
                                         default=33, min=0.00001, max=320000, precision=PRECISION, unit="LENGTH")
    # exporter_start = bpy.props.StringProperty(name="exporter start", default="%")

    # post processor options

    output_block_numbers: BoolProperty(name="output block numbers",
                                       description="output block numbers ie N10 at start of line", default=False)

    start_block_number: IntProperty(name="start block number", description="the starting block number ie 10",
                                    default=10)

    block_number_increment: IntProperty(name="block number increment",
                                        description="how much the block number should increment for the next line",
                                        default=10)

    output_tool_definitions: BoolProperty(name="output tool definitions", description="output tool definitions",
                                          default=True)

    output_tool_change: BoolProperty(name="output tool change commands",
                                     description="output tool change commands ie: Tn M06", default=True)

    output_g43_on_tool_change: BoolProperty(name="output G43 on tool change",
                                            description="output G43 on tool change line", default=False)


class PackObjectsSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    sheet_fill_direction: EnumProperty(name='Fill direction',
                                       items=(('X', 'X', 'Fills sheet in X axis direction'),
                                              ('Y', 'Y', 'Fills sheet in Y axis direction')),
                                       description='Fill direction of the packer algorithm',
                                       default='Y')
    sheet_x: FloatProperty(name="X size", description="Sheet size", min=0.001, max=10, default=0.5,
                           precision=PRECISION, unit="LENGTH")
    sheet_y: FloatProperty(name="Y size", description="Sheet size", min=0.001, max=10, default=0.5,
                           precision=PRECISION, unit="LENGTH")
    distance: FloatProperty(name="Minimum distance",
                            description="minimum distance between objects(should be at least cutter diameter!)",
                            min=0.001, max=10, default=0.01, precision=PRECISION, unit="LENGTH")
    tolerance: FloatProperty(name="Placement Tolerance",
                             description="Tolerance for placement: smaller value slower placemant",
                             min=0.001, max=0.02, default=0.005, precision=PRECISION, unit="LENGTH")
    rotate: bpy.props.BoolProperty(name="enable rotation", description="Enable rotation of elements", default=True)
    rotate_angle: FloatProperty(name="Placement Angle rotation step",
                                description="bigger rotation angle,faster placemant", default=0.19635 * 4,
                                min=math.pi/180,
                                max=math.pi, precision=5,
                                subtype="ANGLE", unit="ROTATION")


class SliceObjectsSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    slice_distance: FloatProperty(name="Slicing distance",
                                  description="slices distance in z, should be most often thickness of plywood sheet.",
                                  min=0.001, max=10, default=0.005, precision=PRECISION, unit="LENGTH")
    slice_above0: bpy.props.BoolProperty(name="Slice above 0", description="only slice model above 0", default=False)
    slice_3d: bpy.props.BoolProperty(name="3d slice", description="for 3d carving", default=False)
    indexes: bpy.props.BoolProperty(name="add indexes", description="adds index text of layer + index", default=True)


class import_settings(bpy.types.PropertyGroup):
    split_layers: BoolProperty(name="Split Layers", description="Save every layer as single Objects in Collection",
                               default=False)
    subdivide: BoolProperty(name="Subdivide",
                            description="Only Subdivide gcode segments that are bigger than 'Segment length' ",
                            default=False)
    output: bpy.props.EnumProperty(name="output type", items=(
        ('mesh', 'Mesh', 'Make a mesh output'), ('curve', 'Curve', 'Make curve output')), default='curve')
    max_segment_size: FloatProperty(name="", description="Only Segments bigger then this value get subdivided",
                                    default=0.001, min=0.0001, max=1.0, unit="LENGTH")


def operationValid(self, context):
    o = self
    o.changed = True
    o.valid = True
    invalidmsg = "Operation has no valid data input\n"
    o.warnings = ""
    o = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    if o.geometry_source == 'OBJECT':
        if o.object_name not in bpy.data.objects:
            o.valid = False
            o.warnings = invalidmsg
    if o.geometry_source == 'COLLECTION':
        if o.collection_name not in bpy.data.collections:
            o.valid = False
            o.warnings = invalidmsg
        elif len(bpy.data.collections[o.collection_name].objects) == 0:
            o.valid = False
            o.warnings = invalidmsg

    if o.geometry_source == 'IMAGE':
        if o.source_image_name not in bpy.data.images:
            o.valid = False
            o.warnings = invalidmsg

        o.use_exact = False
    o.update_offsetimage_tag = True
    o.update_zbufferimage_tag = True
    print('validity ')


# print(o.valid)

def updateOperationValid(self, context):
    operationValid(self, context)
    updateOperation(self, context)


# Update functions start here
def updateChipload(self, context):
    """this is very simple computation of chip size, could be very much improved"""
    print('update chipload ')
    o = self
    # Old chipload
    o.chipload = (o.feedrate / (o.spindle_rpm * o.cutter_flutes))
    # New chipload with chip thining compensation.
    # I have tried to combine these 2 formulas to compinsate for the phenomenon of chip thinning when cutting at less
    # than 50% cutter engagement with cylindrical end mills. formula 1 Nominal Chipload is
    # " feedrate mm/minute = spindle rpm x chipload x cutter diameter mm x cutter_flutes "
    # formula 2 (.5*(cutter diameter mm devided by dist_between_paths)) divided by square root of
    # ((cutter diameter mm devided by dist_between_paths)-1) x Nominal Chipload
    # Nominal Chipload = what you find in end mill data sheats recomended chip load at %50 cutter engagment.
    # I am sure there is a better way to do this. I dont get consistent result and
    # I am not sure if there is something wrong with the units going into the formula, my math or my lack of
    # underestanding of python or programming in genereal. Hopefuly some one can have a look at this and with any luck
    # we will be one tiny step on the way to a slightly better chipload calculating function.

    # self.chipload = ((0.5*(o.cutter_diameter/o.dist_between_paths))/(math.sqrt((o.feedrate*1000)/(o.spindle_rpm*o.cutter_diameter*o.cutter_flutes)*(o.cutter_diameter/o.dist_between_paths)-1)))
    print(o.chipload)


def updateOffsetImage(self, context):
    """refresh offset image tag for rerendering"""
    updateChipload(self, context)
    print('update offset')
    self.changed = True
    self.update_offsetimage_tag = True


def updateZbufferImage(self, context):
    """changes tags so offset and zbuffer images get updated on calculation time."""
    # print('updatezbuf')
    # print(self,context)
    self.changed = True
    self.update_zbufferimage_tag = True
    self.update_offsetimage_tag = True
    utils.getOperationSources(self)


def updateStrategy(o, context):
    """"""
    o.changed = True
    print('update strategy')
    if o.machine_axes == '5' or (
            o.machine_axes == '4' and o.strategy4axis == 'INDEXED'):  # INDEXED 4 AXIS DOESN'T EXIST NOW...
        utils.addOrientationObject(o)
    else:
        utils.removeOrientationObject(o)
    updateExact(o, context)


def updateCutout(o, context):
    pass


def updateExact(o, context):
    print('update exact ')
    o.changed = True
    o.update_zbufferimage_tag = True
    o.update_offsetimage_tag = True
    if o.use_exact and (
             o.strategy == 'POCKET' or o.strategy == 'MEDIAL_AXIS' or o.inverse):
        #    o.use_exact = False
        o.use_opencamlib = False
        print(' pocket cannot use opencamlib')


def updateOpencamlib(o, context):
    print('update opencamlib ')
    o.changed = True
    if o.use_opencamlib and (
            o.strategy == 'POCKET' or o.strategy == 'MEDIAL_AXIS' or o.inverse):
        o.use_exact = False
        o.use_opencamlib = False
        print('pocket cannot use opencamlib')


def updateBridges(o, context):
    print('update bridges ')
    o.changed = True


def updateRotation(o, context):
    if o.enable_B or o.enable_A:
        print(o, o.rotation_A)
        ob = bpy.data.objects[o.object_name]
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if o.A_along_x:  # A parallel with X
            if o.enable_A:
                bpy.context.active_object.rotation_euler.x = o.rotation_A
            if o.enable_B:
                bpy.context.active_object.rotation_euler.y = o.rotation_B
        else:  # A parallel with Y
            if o.enable_A:
                bpy.context.active_object.rotation_euler.y = o.rotation_A
            if o.enable_B:
                bpy.context.active_object.rotation_euler.x = o.rotation_B


# def updateRest(o, context):
#    print('update rest ')
#    # if o.use_layers:
# o.parallel_step_back = False
#    o.changed = True

def updateRest(o, context):
    print('update rest ')
    o.changed = True


#    if (o.strategy == 'WATERLINE'):
#        o.use_layers = True


def getStrategyList(scene, context):
    use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental
    items = [
        ('CUTOUT', 'Profile(Cutout)', 'Cut the silhouete with offset'),
        ('POCKET', 'Pocket', 'Pocket operation'),
        ('DRILL', 'Drill', 'Drill operation'),
        ('PARALLEL', 'Parallel', 'Parallel lines on any angle'),
        ('CROSS', 'Cross', 'Cross paths'),
        ('BLOCK', 'Block', 'Block path'),
        ('SPIRAL', 'Spiral', 'Spiral path'),
        ('CIRCLES', 'Circles', 'Circles path'),
        ('OUTLINEFILL', 'Outline Fill',
         'Detect outline and fill it with paths as pocket. Then sample these paths on the 3d surface'),
        ('CARVE', 'Project curve to surface', 'Engrave the curve path to surface'),
        ('WATERLINE', 'Waterline - Roughing -below zero', 'Waterline paths - constant z below zero'),
        ('CURVE', 'Curve to Path', 'Curve object gets converted directly to path'),
        ('MEDIAL_AXIS', 'Medial axis',
         'Medial axis, must be used with V or ball cutter, for engraving various width shapes with a single stroke ')
    ]
    #   if use_experimental:
    #       items.extend([('MEDIAL_AXIS', 'Medial axis - EXPERIMENTAL',
    #                      'Medial axis, must be used with V or ball cutter, for engraving various width shapes with a single stroke ')]);
    # ('PENCIL', 'Pencil - EXPERIMENTAL','Pencil operation - detects negative corners in the model and mills only those.'),
    # ('CRAZY', 'Crazy path - EXPERIMENTAL', 'Crazy paths - dont even think about using this!'),
    #                     ('PROJECTED_CURVE', 'Projected curve - EXPERIMENTAL', 'project 1 curve towards other curve')])
    return items


class camOperation(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Operation Name", default="Operation", update=updateRest)
    filename: bpy.props.StringProperty(name="File name", default="Operation", update=updateRest)
    auto_export: bpy.props.BoolProperty(name="Auto export",
                                        description="export files immediately after path calculation", default=True)
    remove_redundant_points: bpy.props.BoolProperty(
        name="Symplify Gcode",
        description="Remove redundant points sharing the same angle"
                    " as the start vector",
        default=False)
    simplify_tol: bpy.props.IntProperty(name="Tolerance", description='lower number means more precise', default=50,
                                        min=1, max=1000)
    hide_all_others: bpy.props.BoolProperty(
        name="Hide all others",
        description="Hide all other tool pathes except toolpath"
                    " assotiated with selected CAM operation",
        default=False)
    parent_path_to_object: bpy.props.BoolProperty(
        name="Parent path to object",
        description="Parent generated CAM path to source object",
        default=False)
    object_name: bpy.props.StringProperty(name='Object', description='object handled by this operation',
                                          update=updateOperationValid)
    collection_name: bpy.props.StringProperty(name='Collection',
                                              description='Object collection handled by this operation',
                                              update=updateOperationValid)
    curve_object: bpy.props.StringProperty(name='Curve source',
                                           description='curve which will be sampled along the 3d object',
                                           update=operationValid)
    curve_object1: bpy.props.StringProperty(name='Curve target',
                                            description='curve which will serve as attractor for the cutter when the cutter follows the curve',
                                            update=operationValid)
    source_image_name: bpy.props.StringProperty(name='image_source', description='image source', update=operationValid)
    geometry_source: EnumProperty(name='Source of data',
                                  items=(
                                      ('OBJECT', 'object', 'a'), ('COLLECTION', 'Collection of objects', 'a'),
                                      ('IMAGE', 'Image', 'a')),
                                  description='Geometry source',
                                  default='OBJECT', update=updateOperationValid)
    cutter_type: EnumProperty(name='Cutter',
                              items=(
                                  ('END', 'End', 'end - flat cutter'),
                                  ('BALLNOSE', 'Ballnose', 'ballnose cutter'),
                                  ('BULLNOSE', 'Bullnose', 'bullnose cutter ***placeholder **'),
                                  ('VCARVE', 'V-carve', 'v carve cutter'),
                                  ('BALLCONE', 'Ballcone', 'Ball with a Cone for Parallel - X'),
                                  ('CYLCONE', 'Cylinder cone', 'Cylinder end with a Cone for Parallel - X'),
                                  ('LASER', 'Laser', 'Laser cutter'),
                                  ('PLASMA', 'Plasma', 'Plasma cutter'),
                                  ('CUSTOM', 'Custom-EXPERIMENTAL', 'modelled cutter - not well tested yet.')),
                              description='Type of cutter used',
                              default='END', update=updateZbufferImage)
    cutter_object_name: bpy.props.StringProperty(name='Cutter object',
                                                 description='object used as custom cutter for this operation',
                                                 update=updateZbufferImage)

    machine_axes: EnumProperty(name='Number of axes',
                               items=(
                                   ('3', '3 axis', 'a'),
                                   ('4', '#4 axis - EXPERIMENTAL', 'a'),
                                   ('5', '#5 axis - EXPERIMENTAL', 'a')),
                               description='How many axes will be used for the operation',
                               default='3', update=updateStrategy)
    strategy: EnumProperty(name='Strategy',
                           items=getStrategyList,
                           description='Strategy',
                           update=updateStrategy)

    strategy4axis: EnumProperty(name='4 axis Strategy',
                                items=(
                                    ('PARALLELR', 'Parallel around 1st rotary axis',
                                     'Parallel lines around first rotary axis'),
                                    ('PARALLEL', 'Parallel along 1st rotary axis',
                                     'Parallel lines along first rotary axis'),
                                    ('HELIX', 'Helix around 1st rotary axis', 'Helix around rotary axis'),
                                    ('INDEXED', 'Indexed 3-axis',
                                     'all 3 axis strategies, just applied to the 4th axis'),
                                    ('CROSS', 'Cross', 'Cross paths')),
                                description='#Strategy',
                                default='PARALLEL',
                                update=updateStrategy)
    strategy5axis: EnumProperty(name='Strategy',
                                items=(
                                    ('INDEXED', 'Indexed 3-axis', 'all 3 axis strategies, just rotated by 4+5th axes'),
                                ),
                                description='5 axis Strategy',
                                default='INDEXED',
                                update=updateStrategy)

    rotary_axis_1: EnumProperty(name='Rotary axis',
                                items=(
                                    ('X', 'X', ''),
                                    ('Y', 'Y', ''),
                                    ('Z', 'Z', ''),
                                ),
                                description='Around which axis rotates the first rotary axis',
                                default='X',
                                update=updateStrategy)
    rotary_axis_2: EnumProperty(name='Rotary axis 2',
                                items=(
                                    ('X', 'X', ''),
                                    ('Y', 'Y', ''),
                                    ('Z', 'Z', ''),
                                ),
                                description='Around which axis rotates the second rotary axis',
                                default='Z',
                                update=updateStrategy)

    skin: FloatProperty(name="Skin", description="Material to leave when roughing ", min=0.0, max=1.0, default=0.0,
                        precision=PRECISION, unit="LENGTH", update=updateOffsetImage)
    inverse: bpy.props.BoolProperty(name="Inverse milling", description="Male to female model conversion",
                                    default=False, update=updateOffsetImage)
    array: bpy.props.BoolProperty(name="Use array",
                                  description="Create a repetitive array for producing the same thing manytimes",
                                  default=False, update=updateRest)
    array_x_count: bpy.props.IntProperty(name="X count", description="X count", default=1, min=1, max=32000,
                                         update=updateRest)
    array_y_count: bpy.props.IntProperty(name="Y count", description="Y count", default=1, min=1, max=32000,
                                         update=updateRest)
    array_x_distance: FloatProperty(name="X distance", description="distance between operation origins", min=0.00001,
                                    max=1.0, default=0.01, precision=PRECISION, unit="LENGTH", update=updateRest)
    array_y_distance: FloatProperty(name="Y distance", description="distance between operation origins", min=0.00001,
                                    max=1.0, default=0.01, precision=PRECISION, unit="LENGTH", update=updateRest)

    # pocket options
    pocket_option: EnumProperty(name='Start Position', items=(
        ('INSIDE', 'Inside', 'a'), ('OUTSIDE', 'Outside', 'a'), ('MIDDLE', 'Middle', 'a')),
                                description='Pocket starting position', default='MIDDLE', update=updateRest)
    pocketToCurve: bpy.props.BoolProperty(name="Pocket to curve",
                                          description="generates a curve instead of a path",
                                          default=False, update=updateRest)
    # Cutout
    cut_type: EnumProperty(name='Cut',
                           items=(('OUTSIDE', 'Outside', 'a'), ('INSIDE', 'Inside', 'a'), ('ONLINE', 'On line', 'a')),
                           description='Type of cutter used', default='OUTSIDE', update=updateRest)
    outlines_count: bpy.props.IntProperty(name="Outlines count`EXPERIMENTAL", description="Outlines count", default=1,
                                          min=1, max=32, update=updateCutout)
    straight: bpy.props.BoolProperty(name="Overshoot Style",
                                     description="Use overshoot cutout instead of conventional rounded",
                                     default=False, update=updateRest)
    # cutter
    cutter_id: IntProperty(name="Tool number", description="For machines which support tool change based on tool id",
                           min=0, max=10000, default=1, update=updateRest)
    cutter_diameter: FloatProperty(name="Cutter diameter", description="Cutter diameter = 2x cutter radius",
                                   min=0.000001, max=10, default=0.003, precision=PRECISION, unit="LENGTH",
                                   update=updateOffsetImage)
    cylcone_diameter: FloatProperty(name="Bottom Diameter", description="Bottom diameter",
                                    min=0.000001, max=10, default=0.003, precision=PRECISION, unit="LENGTH",
                                    update=updateOffsetImage)
    cutter_length: FloatProperty(name="#Cutter length", description="#not supported#Cutter length", min=0.0, max=100.0,
                                 default=25.0, precision=PRECISION, unit="LENGTH", update=updateOffsetImage)
    cutter_flutes: IntProperty(name="Cutter flutes", description="Cutter flutes", min=1, max=20, default=2,
                               update=updateChipload)
    cutter_tip_angle: FloatProperty(name="Cutter v-carve angle", description="Cutter v-carve angle", min=0.0,
                                    max=180.0, default=60.0, precision=PRECISION, update=updateOffsetImage)
    ball_radius: FloatProperty(name="Ball radius", description="Radius of", min=0.0,
                               max=0.035, default=0.001, unit="LENGTH", precision=PRECISION, update=updateOffsetImage)
    # ball_cone_flute: FloatProperty(name="BallCone Flute Length", description="length of flute", min=0.0,
    #                                 max=0.1, default=0.017, unit="LENGTH", precision=PRECISION, update=updateOffsetImage)
    bull_corner_radius: FloatProperty(name="Bull Corner Radius", description="Radius tool bit corner", min=0.0,
                                      max=0.035, default=0.005, unit="LENGTH", precision=PRECISION,
                                      update=updateOffsetImage)

    cutter_description: StringProperty(name="Tool Description", default="", update=updateOffsetImage)

    Laser_on: bpy.props.StringProperty(name="Laser ON string", default="M68 E0 Q100")
    Laser_off: bpy.props.StringProperty(name="Laser OFF string", default="M68 E0 Q0")
    Laser_cmd: bpy.props.StringProperty(name="Laser command", default="M68 E0 Q")
    Laser_delay: bpy.props.FloatProperty(name="Laser ON Delay",
                                         description="time after fast move to turn on laser and let machine stabilize",
                                         default=0.2)
    Plasma_on: bpy.props.StringProperty(name="Plasma ON string", default="M03")
    Plasma_off: bpy.props.StringProperty(name="Plasma OFF string", default="M05")
    Plasma_delay: bpy.props.FloatProperty(name="Plasma ON Delay",
                                          description="time after fast move to turn on Plasma and let machine stabilize",
                                          default=0.1)
    Plasma_dwell: bpy.props.FloatProperty(name="Plasma dwell time", description="Time to dwell and warm up the torch",
                                          default=0.0)

    # steps
    dist_between_paths: bpy.props.FloatProperty(name="Distance between toolpaths", default=0.001, min=0.00001, max=32,
                                                precision=PRECISION, unit="LENGTH", update=updateRest)
    dist_along_paths: bpy.props.FloatProperty(name="Distance along toolpaths", default=0.0002, min=0.00001, max=32,
                                              precision=PRECISION, unit="LENGTH", update=updateRest)
    parallel_angle: bpy.props.FloatProperty(name="Angle of paths", default=0, min=-360, max=360, precision=0,
                                            subtype="ANGLE", unit="ROTATION", update=updateRest)
    old_rotation_A: bpy.props.FloatProperty(name="A axis angle",
                                            description="old value of Rotate A axis\nto specified angle", default=0,
                                            min=-360, max=360, precision=0, subtype="ANGLE", unit="ROTATION",
                                            update=updateRest)

    old_rotation_B: bpy.props.FloatProperty(name="A axis angle",
                                            description="old value of Rotate A axis\nto specified angle", default=0,
                                            min=-360, max=360, precision=0, subtype="ANGLE", unit="ROTATION",
                                            update=updateRest)

    rotation_A: bpy.props.FloatProperty(name="A axis angle", description="Rotate A axis\nto specified angle", default=0,
                                        min=-360, max=360, precision=0,
                                        subtype="ANGLE", unit="ROTATION", update=updateRest)
    enable_A: bpy.props.BoolProperty(name="Enable A axis", description="Rotate A axis", default=False,
                                     update=updateRest)
    A_along_x: bpy.props.BoolProperty(name="A Along X ", description="A Parallel to X", default=True, update=updateRest)

    rotation_B: bpy.props.FloatProperty(name="B axis angle", description="Rotate B axis\nto specified angle", default=0,
                                        min=-360, max=360, precision=0,
                                        subtype="ANGLE", unit="ROTATION", update=updateRest)
    enable_B: bpy.props.BoolProperty(name="Enable B axis", description="Rotate B axis", default=False,
                                     update=updateRest)

    # carve only
    carve_depth: bpy.props.FloatProperty(name="Carve depth", default=0.001, min=-.100, max=32, precision=PRECISION,
                                         unit="LENGTH", update=updateRest)

    # drill only
    drill_type: EnumProperty(name='Holes on', items=(
        ('MIDDLE_SYMETRIC', 'Middle of symetric curves', 'a'), ('MIDDLE_ALL', 'Middle of all curve parts', 'a'),
        ('ALL_POINTS', 'All points in curve', 'a')), description='Strategy to detect holes to drill',
                             default='MIDDLE_SYMETRIC', update=updateRest)
    # waterline only
    slice_detail: bpy.props.FloatProperty(name="Distance betwen slices", default=0.001, min=0.00001, max=32,
                                          precision=PRECISION, unit="LENGTH", update=updateRest)
    waterline_fill: bpy.props.BoolProperty(name="Fill areas between slices",
                                           description="Fill areas between slices in waterline mode", default=True,
                                           update=updateRest)
    waterline_project: bpy.props.BoolProperty(name="Project paths - not recomended",
                                              description="Project paths in areas between slices", default=True,
                                              update=updateRest)

    # movement and ramps
    use_layers: bpy.props.BoolProperty(name="Use Layers", description="Use layers for roughing", default=True,
                                       update=updateRest)
    stepdown: bpy.props.FloatProperty(name="", description="Layer height", default=0.01, min=0.00001, max=32, precision=PRECISION,
                                      unit="LENGTH", update=updateRest)
    first_down: bpy.props.BoolProperty(name="First down",
                                       description="First go down on a contour, then go to the next one",
                                       default=False, update=updateRest)
    ramp: bpy.props.BoolProperty(name="Ramp in - EXPERIMENTAL",
                                 description="Ramps down the whole contour, so the cutline looks like helix",
                                 default=False, update=updateRest)
    ramp_out: bpy.props.BoolProperty(name="Ramp out - EXPERIMENTAL",
                                     description="Ramp out to not leave mark on surface", default=False,
                                     update=updateRest)
    ramp_in_angle: bpy.props.FloatProperty(name="Ramp in angle", default=math.pi / 6, min=0, max=math.pi * 0.4999,
                                           precision=1, subtype="ANGLE", unit="ROTATION", update=updateRest)
    ramp_out_angle: bpy.props.FloatProperty(name="Ramp out angle", default=math.pi / 6, min=0, max=math.pi * 0.4999,
                                            precision=1, subtype="ANGLE", unit="ROTATION", update=updateRest)
    helix_enter: bpy.props.BoolProperty(name="Helix enter - EXPERIMENTAL", description="Enter material in helix",
                                        default=False, update=updateRest)
    lead_in: bpy.props.FloatProperty(name="Lead in radius",
                                     description="Lead out radius for torch or laser to turn off",
                                     min=0.00, max=1, default=0.0, precision=PRECISION, unit="LENGTH")
    lead_out: bpy.props.FloatProperty(name="Lead out radius",
                                      description="Lead out radius for torch or laser to turn off",
                                      min=0.00, max=1, default=0.0, precision=PRECISION, unit="LENGTH")
    profile_start: bpy.props.IntProperty(name="Start point", description="Start point offset", min=0, default=0,
                                         update=updateRest)

    # helix_angle: bpy.props.FloatProperty(name="Helix ramp angle", default=3*math.pi/180, min=0.00001, max=math.pi*0.4999,precision=1, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
    helix_diameter: bpy.props.FloatProperty(name='Helix diameter % of cutter D', default=90, min=10, max=100,
                                            precision=1, subtype='PERCENTAGE', update=updateRest)
    retract_tangential: bpy.props.BoolProperty(name="Retract tangential - EXPERIMENTAL",
                                               description="Retract from material in circular motion", default=False,
                                               update=updateRest)
    retract_radius: bpy.props.FloatProperty(name='Retract arc radius', default=0.001, min=0.000001, max=100,
                                            precision=PRECISION, unit="LENGTH", update=updateRest)
    retract_height: bpy.props.FloatProperty(name='Retract arc height', default=0.001, min=0.00000, max=100,
                                            precision=PRECISION, unit="LENGTH", update=updateRest)

    minz_from_ob: bpy.props.BoolProperty(name="Depth from object", description="Operation ending depth from object",
                                         default=True, update=updateRest)
    minz_from_material: bpy.props.BoolProperty(name="Depth from material",
                                               description="Operation ending depth from material",
                                               default=False, update=updateRest)
    minz: bpy.props.FloatProperty(name="Operation depth end", default=-0.01, min=-3, max=3, precision=PRECISION,
                                  unit="LENGTH",
                                  update=updateRest)  # this is input minz. True minimum z can be something else, depending on material e.t.c.
    start_type: bpy.props.EnumProperty(name='Start type',
                                       items=(
                                           ('ZLEVEL', 'Z level', 'Starts on a given Z level'),
                                           ('OPERATIONRESULT', 'Rest milling',
                                            'For rest milling, operations have to be put in chain for this to work well.'),
                                       ),
                                       description='Starting depth',
                                       default='ZLEVEL',
                                       update=updateStrategy)

    maxz: bpy.props.FloatProperty(name="Operation depth start", description='operation starting depth', default=0,
                                  min=-3, max=10, precision=PRECISION, unit="LENGTH",
                                  update=updateRest)  # EXPERIMENTAL

    #######################################################
    # Image related
    ####################################################

    source_image_scale_z: bpy.props.FloatProperty(name="Image source depth scale", default=0.01, min=-1, max=1,
                                                  precision=PRECISION, unit="LENGTH", update=updateZbufferImage)
    source_image_size_x: bpy.props.FloatProperty(name="Image source x size", default=0.1, min=-10, max=10,
                                                 precision=PRECISION, unit="LENGTH", update=updateZbufferImage)
    source_image_offset: bpy.props.FloatVectorProperty(name='Image offset', default=(0, 0, 0), unit='LENGTH',
                                                       precision=PRECISION, subtype="XYZ", update=updateZbufferImage)
    source_image_crop: bpy.props.BoolProperty(name="Crop source image",
                                              description="Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image",
                                              default=False, update=updateZbufferImage)
    source_image_crop_start_x: bpy.props.FloatProperty(name='crop start x', default=0, min=0, max=100,
                                                       precision=PRECISION, subtype='PERCENTAGE',
                                                       update=updateZbufferImage)
    source_image_crop_start_y: bpy.props.FloatProperty(name='crop start y', default=0, min=0, max=100,
                                                       precision=PRECISION, subtype='PERCENTAGE',
                                                       update=updateZbufferImage)
    source_image_crop_end_x: bpy.props.FloatProperty(name='crop end x', default=100, min=0, max=100,
                                                     precision=PRECISION, subtype='PERCENTAGE',
                                                     update=updateZbufferImage)
    source_image_crop_end_y: bpy.props.FloatProperty(name='crop end y', default=100, min=0, max=100,
                                                     precision=PRECISION, subtype='PERCENTAGE',
                                                     update=updateZbufferImage)

    #########################################################
    # Toolpath and area related
    #####################################################

    protect_vertical: bpy.props.BoolProperty(name="Protect vertical",
                                             description="The path goes only vertically next to steep areas",
                                             default=True)
    protect_vertical_limit: bpy.props.FloatProperty(name="Verticality limit",
                                                    description="What angle is allready considered vertical",
                                                    default=math.pi / 45, min=0, max=math.pi * 0.5, precision=0,
                                                    subtype="ANGLE", unit="ROTATION", update=updateRest)

    ambient_behaviour: EnumProperty(name='Ambient', items=(('ALL', 'All', 'a'), ('AROUND', 'Around', 'a')),
                                    description='handling ambient surfaces', default='ALL', update=updateZbufferImage)

    ambient_radius: FloatProperty(name="Ambient radius",
                                  description="Radius around the part which will be milled if ambient is set to Around",
                                  min=0.0, max=100.0, default=0.01, precision=PRECISION, unit="LENGTH",
                                  update=updateRest)
    # ambient_cutter = EnumProperty(name='Borders',items=(('EXTRAFORCUTTER', 'Extra for cutter', "Extra space for cutter is cut around the segment"),('ONBORDER', "Cutter on edge", "Cutter goes exactly on edge of ambient with it's middle") ,('INSIDE', "Inside segment", 'Cutter stays within segment')	 ),description='handling of ambient and cutter size',default='INSIDE')
    use_limit_curve: bpy.props.BoolProperty(name="Use limit curve", description="A curve limits the operation area",
                                            default=False, update=updateRest)
    ambient_cutter_restrict: bpy.props.BoolProperty(name="Cutter stays in ambient limits",
                                                    description="Cutter doesn't get out from ambient limits otherwise goes on the border exactly",
                                                    default=True,
                                                    update=updateRest)  # restricts cutter inside ambient only
    limit_curve: bpy.props.StringProperty(name='Limit curve',
                                          description='curve used to limit the area of the operation',
                                          update=updateRest)

    # feeds
    feedrate: FloatProperty(name="Feedrate", description="Feedrate", min=0.00005, max=50.0, default=1.0,
                            precision=PRECISION, unit="LENGTH", update=updateChipload)
    plunge_feedrate: FloatProperty(name="Plunge speed ", description="% of feedrate", min=0.1, max=100.0, default=50.0,
                                   precision=1, subtype='PERCENTAGE', update=updateRest)
    plunge_angle: bpy.props.FloatProperty(name="Plunge angle",
                                          description="What angle is allready considered to plunge",
                                          default=math.pi / 6, min=0, max=math.pi * 0.5, precision=0, subtype="ANGLE",
                                          unit="ROTATION", update=updateRest)
    spindle_rpm: FloatProperty(name="Spindle rpm", description="Spindle speed ", min=0, max=60000, default=12000,
                               update=updateChipload)
    # movement parallel_step_back
    movement_type: EnumProperty(name='Movement type', items=(
        ('CONVENTIONAL', 'Conventional / Up milling', 'cutter rotates against the direction of the feed'),
        ('CLIMB', 'Climb / Down milling', 'cutter rotates with the direction of the feed'),
        ('MEANDER', 'Meander / Zig Zag', 'cutting is done both with and against the rotation of the spindle')),
                                description='movement type', default='CLIMB', update=updateRest)
    spindle_rotation_direction: EnumProperty(name='Spindle rotation',
                                             items=(('CW', 'Clock wise', 'a'), ('CCW', 'Counter clock wise', 'a')),
                                             description='Spindle rotation direction', default='CW', update=updateRest)
    free_movement_height: bpy.props.FloatProperty(name="Free movement height", default=0.01, min=0.0000, max=32,
                                                  precision=PRECISION, unit="LENGTH", update=updateRest)
    useG64: bpy.props.BoolProperty(name="G64 trajectory",
                                   description='Use only if your machie supports G64 code.  LinuxCNC and Mach3 do',
                                   default=False, update=updateRest)
    G64: bpy.props.FloatProperty(name="Path Control Mode with Optional Tolerance", default=0.0001, min=0.0000,
                                 max=0.005,
                                 precision=PRECISION, unit="LENGTH", update=updateRest)
    movement_insideout: EnumProperty(name='Direction',
                                     items=(('INSIDEOUT', 'Inside out', 'a'), ('OUTSIDEIN', 'Outside in', 'a')),
                                     description='approach to the piece', default='INSIDEOUT', update=updateRest)
    parallel_step_back: bpy.props.BoolProperty(name="Parallel step back",
                                               description='For roughing and finishing in one pass: mills material in climb mode, then steps back and goes between 2 last chunks back',
                                               default=False, update=updateRest)
    stay_low: bpy.props.BoolProperty(name="Stay low if possible", default=True, update=updateRest)
    merge_dist: bpy.props.FloatProperty(name="Merge distance - EXPERIMENTAL", default=0.0, min=0.0000, max=0.1,
                                        precision=PRECISION, unit="LENGTH", update=updateRest)
    # optimization and performance
    circle_detail: bpy.props.IntProperty(name="Detail of circles used for curve offsets", default=64, min=12, max=512,
                                         update=updateRest)
    use_exact: bpy.props.BoolProperty(name="Use exact mode",
                                      description="Exact mode allows greater precision, but is slower with complex meshes",
                                      default=True, update=updateExact)
    exact_subdivide_edges: bpy.props.BoolProperty(name="Auto subdivide long edges",
                                                  description="This can avoid some collision issues when importing CAD models",
                                                  default=False, update=updateExact)
    use_opencamlib: bpy.props.BoolProperty(name="Use OpenCAMLib",
                                           description="Use OpenCAMLib to sample paths or get waterline shape",
                                           default=False, update=updateOpencamlib)
    pixsize: bpy.props.FloatProperty(name="sampling raster detail", default=0.0001, min=0.00001, max=0.1,
                                     precision=PRECISION, unit="LENGTH", update=updateZbufferImage)
    simulation_detail: bpy.props.FloatProperty(name="Simulation sampling raster detail", default=0.0002, min=0.00001,
                                               max=0.01, precision=PRECISION, unit="LENGTH", update=updateRest)
    do_simulation_feedrate: bpy.props.BoolProperty(name="Adjust feedrates with simulation EXPERIMENTAL",
                                                   description="Adjust feedrates with simulation", default=False,
                                                   update=updateRest)

    imgres_limit: bpy.props.IntProperty(name="Maximum resolution in megapixels", default=16, min=1, max=512,
                                        description="This property limits total memory usage and prevents crashes. Increase it if you know what are doing.",
                                        update=updateZbufferImage)
    optimize: bpy.props.BoolProperty(name="Reduce path points", description="Reduce path points", default=True,
                                     update=updateRest)
    optimize_threshold: bpy.props.FloatProperty(name="Reduction threshold in μm", default=.2, min=0.000000001,
                                                max=1000, precision=20, update=updateRest)

    dont_merge: bpy.props.BoolProperty(name="Dont merge outlines when cutting",
                                       description="this is usefull when you want to cut around everything",
                                       default=False, update=updateRest)

    pencil_threshold: bpy.props.FloatProperty(name="Pencil threshold", default=0.00002, min=0.00000001, max=1,
                                              precision=PRECISION, unit="LENGTH", update=updateRest)
    crazy_threshold1: bpy.props.FloatProperty(name="min engagement", default=0.02, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold5: bpy.props.FloatProperty(name="optimal engagement", default=0.3, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold2: bpy.props.FloatProperty(name="max engagement", default=0.5, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold3: bpy.props.FloatProperty(name="max angle", default=2, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    crazy_threshold4: bpy.props.FloatProperty(name="test angle step", default=0.05, min=0.00000001, max=100,
                                              precision=PRECISION, update=updateRest)
    # Add pocket operation to medial axis
    add_pocket_for_medial: bpy.props.BoolProperty(name="Add pocket operation",
                                                  description="clean unremoved material after medial axis",
                                                  default=True,
                                                  update=updateRest)

    add_mesh_for_medial: bpy.props.BoolProperty(name="Add Medial mesh",
                                                description="Medial operation returns mesh for editing and further processing",
                                                default=False,
                                                update=updateRest)
    ####
    medial_axis_threshold: bpy.props.FloatProperty(name="Long vector threshold", default=0.001, min=0.00000001,
                                                   max=100, precision=PRECISION, unit="LENGTH", update=updateRest)
    medial_axis_subdivision: bpy.props.FloatProperty(name="Fine subdivision", default=0.0002, min=0.00000001, max=100,
                                                     precision=PRECISION, unit="LENGTH", update=updateRest)
    # calculations
    duration: bpy.props.FloatProperty(name="Estimated time", default=0.01, min=0.0000, max=3200000000,
                                      precision=PRECISION, unit="TIME")
    # chip_rate
    # bridges
    use_bridges: bpy.props.BoolProperty(name="Use bridges", description="use bridges in cutout", default=False,
                                        update=updateBridges)
    bridges_width: bpy.props.FloatProperty(name='width of bridges', default=0.002, unit='LENGTH', precision=PRECISION,
                                           update=updateBridges)
    bridges_height: bpy.props.FloatProperty(name='height of bridges',
                                            description="Height from the bottom of the cutting operation",
                                            default=0.0005, unit='LENGTH', precision=PRECISION, update=updateBridges)
    bridges_collection_name: bpy.props.StringProperty(name='Bridges Collection',
                                                      description='Collection of curves used as bridges',
                                                      update=operationValid)
    use_bridge_modifiers: BoolProperty(name="use bridge modifiers",
                                       description="include bridge curve modifiers using render level when calculating operation, does not effect original bridge data",
                                       default=True, update=updateBridges)

    # commented this - auto bridges will be generated, but not as a setting of the operation
    # bridges_placement = bpy.props.EnumProperty(name='Bridge placement',
    #     items=(
    #         ('AUTO','Automatic', 'Automatic bridges with a set distance'),
    #         ('MANUAL','Manual', 'Manual placement of bridges'),
    #         ),
    #     description='Bridge placement',
    #     default='AUTO',
    #     update = updateStrategy)
    #
    # bridges_per_curve = bpy.props.IntProperty(name="minimum bridges per curve", description="", default=4, min=1, max=512, update = updateBridges)
    # bridges_max_distance = bpy.props.FloatProperty(name = 'Maximum distance between bridges', default=0.08, unit='LENGTH', precision=PRECISION, update = updateBridges)

    use_modifiers: BoolProperty(name="use mesh modifiers",
                                description="include mesh modifiers using render level when calculating operation, does not effect original mesh",
                                default=True, update=operationValid)
    # optimisation panel

    # material settings
    material_from_model: bpy.props.BoolProperty(name="Estimate from model",
                                                description="Estimate material size from model", default=True,
                                                update=updateMaterial)
    material_radius_around_model: bpy.props.FloatProperty(name="radius around model",
                                                          description="How much to add to model size on all sides",
                                                          default=0.0, unit='LENGTH', precision=PRECISION,
                                                          update=updateMaterial)
    material_center_x: bpy.props.BoolProperty(name="Center with X axis", description="Position model centered on X",
                                              default=False, update=updateMaterial)
    material_center_y: bpy.props.BoolProperty(name="Center with Y axis", description="Position model centered on Y",
                                              default=False, update=updateMaterial)

    material_Z: bpy.props.EnumProperty(name="Z placement", items=(
    ('ABOVE', 'Above', 'Place objec above 0'), ('BELOW', 'Below', 'Place object below 0'),
    ('CENTERED', 'Centered', 'Place object centered on 0')), description="Position below Zero", default='BELOW',
                                       update=updateMaterial)

    material_origin: bpy.props.FloatVectorProperty(name='Material origin', default=(0, 0, 0), unit='LENGTH',
                                                   precision=PRECISION, subtype="XYZ", update=updateMaterial)
    material_size: bpy.props.FloatVectorProperty(name='Material size', default=(0.200, 0.200, 0.100), unit='LENGTH',
                                                 precision=PRECISION, subtype="XYZ", update=updateMaterial)
    min: bpy.props.FloatVectorProperty(name='Operation minimum', default=(0, 0, 0), unit='LENGTH', precision=PRECISION,
                                       subtype="XYZ")
    max: bpy.props.FloatVectorProperty(name='Operation maximum', default=(0, 0, 0), unit='LENGTH', precision=PRECISION,
                                       subtype="XYZ")
    warnings: bpy.props.StringProperty(name='warnings', description='warnings', default='', update=updateRest)
    chipload: bpy.props.FloatProperty(name="chipload", description="Calculated chipload", default=0.0, unit='LENGTH',
                                      precision=10)

    # g-code options for operation
    output_header: BoolProperty(name="output g-code header",
                                description="output user defined g-code command header at start of operation",
                                default=False)

    gcode_header: StringProperty(name="g-code header",
                                 description="g-code commands at start of operation. Use ; for line breaks",
                                 default="G53 G0")

    enable_dust: BoolProperty(name="Dust collector",
                                description="output user defined g-code command header at start of operation",
                                default=False)

    gcode_start_dust_cmd: StringProperty(name="Start dust collector",
                                 description="commands to start dust collection. Use ; for line breaks",
                                 default="M100")

    gcode_stop_dust_cmd: StringProperty(name="Stop dust collector",
                                 description="command to stop dust collection. Use ; for line breaks",
                                 default="M101")

    enable_hold: BoolProperty(name="Hold down",
                              description="output hold down command at start of operation",
                              default=False)

    gcode_start_hold_cmd: StringProperty(name="g-code header",
                                         description="g-code commands at start of operation. Use ; for line breaks",
                                         default="M102")

    gcode_stop_hold_cmd: StringProperty(name="g-code header",
                                        description="g-code commands at end operation. Use ; for line breaks",
                                        default="M103")

    enable_mist: BoolProperty(name="Mist",
                              description="Mist command at start of operation",
                              default=False)

    gcode_start_mist_cmd: StringProperty(name="g-code header",
                                         description="g-code commands at start of operation. Use ; for line breaks",
                                         default="M104")

    gcode_stop_mist_cmd: StringProperty(name="g-code header",
                                        description="g-code commands at end operation. Use ; for line breaks",
                                        default="M105")

    output_trailer: BoolProperty(name="output g-code trailer",
                                 description="output user defined g-code command trailer at end of operation",
                                 default=False)

    gcode_trailer: StringProperty(name="g-code trailer",
                                  description="g-code commands at end of operation. Use ; for line breaks",
                                  default="M02")

    # internal properties
    ###########################################

    # testing = bpy.props.IntProperty(name="developer testing ", description="This is just for script authors for help in coding, keep 0", default=0, min=0, max=512)
    offset_image = numpy.array([], dtype=float)
    zbuffer_image = numpy.array([], dtype=float)

    silhouete = sgeometry.Polygon()
    ambient = sgeometry.Polygon()
    operation_limit = sgeometry.Polygon()
    borderwidth = 50
    object = None
    path_object_name: bpy.props.StringProperty(name='Path object', description='actual cnc path')

    # update and tags and related

    changed: bpy.props.BoolProperty(name="True if any of the operation settings has changed",
                                    description="mark for update", default=False)
    update_zbufferimage_tag: bpy.props.BoolProperty(name="mark zbuffer image for update",
                                                    description="mark for update", default=True)
    update_offsetimage_tag: bpy.props.BoolProperty(name="mark offset image for update", description="mark for update",
                                                   default=True)
    update_silhouete_tag: bpy.props.BoolProperty(name="mark silhouete image for update", description="mark for update",
                                                 default=True)
    update_ambient_tag: bpy.props.BoolProperty(name="mark ambient polygon for update", description="mark for update",
                                               default=True)
    update_bullet_collision_tag: bpy.props.BoolProperty(name="mark bullet collisionworld for update",
                                                        description="mark for update", default=True)

    valid: bpy.props.BoolProperty(name="Valid", description="True if operation is ok for calculation", default=True);
    changedata: bpy.props.StringProperty(name='changedata', description='change data for checking if stuff changed.')

    # process related data

    computing: bpy.props.BoolProperty(name="Computing right now", description="", default=False)
    pid: bpy.props.IntProperty(name="process id", description="Background process id", default=-1)
    outtext: bpy.props.StringProperty(name='outtext', description='outtext', default='')


class opReference(bpy.types.PropertyGroup):  # this type is defined just to hold reference to operations for chains
    name: bpy.props.StringProperty(name="Operation name", default="Operation")
    computing = False  # for UiList display


class camChain(bpy.types.PropertyGroup):  # chain is just a set of operations which get connected on export into 1 file.
    index: bpy.props.IntProperty(name="index", description="index in the hard-defined camChains", default=-1)
    active_operation: bpy.props.IntProperty(name="active operation", description="active operation in chain",
                                            default=-1)
    name: bpy.props.StringProperty(name="Chain Name", default="Chain")
    filename: bpy.props.StringProperty(name="File name", default="Chain")  # filename of
    valid: bpy.props.BoolProperty(name="Valid", description="True if whole chain is ok for calculation", default=True);
    computing: bpy.props.BoolProperty(name="Computing right now", description="", default=False)
    operations: bpy.props.CollectionProperty(type=opReference)  # this is to hold just operation names.


@bpy.app.handlers.persistent
def check_operations_on_load(context):
    """checks any broken computations on load and reset them."""
    s = bpy.context.scene
    for o in s.cam_operations:
        if o.computing:
            o.computing = False


class CAM_CUTTER_MT_presets(Menu):
    bl_label = "Cutter presets"
    preset_subdir = "cam_cutters"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class CAM_MACHINE_MT_presets(Menu):
    bl_label = "Machine presets"
    preset_subdir = "cam_machines"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class AddPresetCamCutter(bl_operators.presets.AddPresetBase, Operator):
    """Add a Cutter Preset"""
    bl_idname = "render.cam_preset_cutter_add"
    bl_label = "Add Cutter Preset"
    preset_menu = "CAM_CUTTER_MT_presets"

    preset_defines = [
        "d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"
    ]

    preset_values = [
        "d.cutter_id",
        "d.cutter_type",
        "d.cutter_diameter",
        "d.cutter_length",
        "d.cutter_flutes",
        "d.cutter_tip_angle",
        "d.cutter_description",
    ]

    preset_subdir = "cam_cutters"


class CAM_OPERATION_MT_presets(Menu):
    bl_label = "Operation presets"
    preset_subdir = "cam_operations"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class AddPresetCamOperation(bl_operators.presets.AddPresetBase, Operator):
    """Add an Operation Preset"""
    bl_idname = "render.cam_preset_operation_add"
    bl_label = "Add Operation Preset"
    preset_menu = "CAM_OPERATION_MT_presets"

    preset_defines = ["o = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"]

    preset_values = ['o.use_layers', 'o.duration', 'o.chipload', 'o.material_from_model', 'o.stay_low', 'o.carve_depth',
                     'o.dist_along_paths', 'o.source_image_crop_end_x', 'o.source_image_crop_end_y', 'o.material_size',
                     'o.material_radius_around_model', 'o.use_limit_curve', 'o.cut_type', 'o.use_exact',
                     'o.exact_subdivide_edges', 'o.minz_from_ob', 'o.free_movement_height',
                     'o.source_image_crop_start_x', 'o.movement_insideout', 'o.spindle_rotation_direction', 'o.skin',
                     'o.source_image_crop_start_y', 'o.movement_type', 'o.source_image_crop', 'o.limit_curve',
                     'o.spindle_rpm', 'o.ambient_behaviour', 'o.cutter_type', 'o.source_image_scale_z',
                     'o.cutter_diameter', 'o.source_image_size_x', 'o.curve_object', 'o.curve_object1',
                     'o.cutter_flutes', 'o.ambient_radius', 'o.simulation_detail', 'o.update_offsetimage_tag',
                     'o.dist_between_paths', 'o.max', 'o.min', 'o.pixsize', 'o.slice_detail', 'o.parallel_step_back',
                     'o.drill_type', 'o.source_image_name', 'o.dont_merge', 'o.update_silhouete_tag',
                     'o.material_origin', 'o.inverse', 'o.waterline_fill', 'o.source_image_offset', 'o.circle_detail',
                     'o.strategy', 'o.update_zbufferimage_tag', 'o.stepdown', 'o.feedrate', 'o.cutter_tip_angle',
                     'o.cutter_id', 'o.path_object_name', 'o.pencil_threshold', 'o.geometry_source',
                     'o.optimize_threshold', 'o.protect_vertical', 'o.plunge_feedrate', 'o.minz', 'o.warnings',
                     'o.object_name', 'o.optimize', 'o.parallel_angle', 'o.cutter_length',
                     'o.output_header', 'o.gcode_header', 'o.output_trailer', 'o.gcode_trailer', 'o.use_modifiers',
                     'o.minz_from_material', 'o.useG64',
                     'o.G64', 'o.enable_A', 'o.enable_B', 'o.A_along_x', 'o.rotation_A', 'o.rotation_B', 'o.straight']

    preset_subdir = "cam_operations"


class AddPresetCamMachine(bl_operators.presets.AddPresetBase, Operator):
    """Add a Cam Machine Preset"""
    bl_idname = "render.cam_preset_machine_add"
    bl_label = "Add Machine Preset"
    preset_menu = "CAM_MACHINE_MT_presets"

    preset_defines = [
        "d = bpy.context.scene.cam_machine",
        "s = bpy.context.scene.unit_settings"
    ]
    preset_values = [
        "d.post_processor",
        "s.system",
        "d.use_position_definitions",
        "d.starting_position",
        "d.mtc_position",
        "d.ending_position",
        "d.working_area",
        "d.feedrate_min",
        "d.feedrate_max",
        "d.feedrate_default",
        "d.spindle_min",
        "d.spindle_max",
        "d.spindle_default",
        "d.axis4",
        "d.axis5",
        "d.collet_size",
        "d.output_tool_change",
        "d.output_block_numbers",
        "d.output_tool_definitions",
        "d.output_g43_on_tool_change",
    ]

    preset_subdir = "cam_machines"


class BLENDERCAM_ENGINE(bpy.types.RenderEngine):
    bl_idname = 'BLENDERCAM_RENDER'
    bl_label = "Cam"


def get_panels():  # convenience function for bot register and unregister functions
    # types = bpy.types
    return (
        ui.CAM_UL_operations,
        # ui.CAM_UL_orientations,
        ui.CAM_UL_chains,
        camOperation,
        opReference,
        camChain,
        machineSettings,
        CamAddonPreferences,

        ui.CAM_CHAINS_Panel,
        ui.CAM_OPERATIONS_Panel,
        ui.CAM_INFO_Panel,
        ui.CAM_MATERIAL_Panel,
        ui.CAM_OPERATION_PROPERTIES_Panel,
        ui.CAM_OPTIMISATION_Panel,
        ui.CAM_AREA_Panel,
        ui.CAM_MOVEMENT_Panel,
        ui.CAM_FEEDRATE_Panel,
        ui.CAM_CUTTER_Panel,
        ui.CAM_GCODE_Panel,
        ui.CAM_MACHINE_Panel,
        ui.CAM_PACK_Panel,
        ui.CAM_SLICE_Panel,
        ui.VIEW3D_PT_tools_curvetools,
        ui.CustomPanel,

        ops.PathsBackground,
        ops.KillPathsBackground,
        ops.CalculatePath,
        ops.PathsChain,
        ops.PathExportChain,
        ops.PathsAll,
        ops.PathExport,
        ops.CAMPositionObject,
        ops.CAMSimulate,
        ops.CAMSimulateChain,
        ops.CamChainAdd,
        ops.CamChainRemove,
        ops.CamChainOperationAdd,
        ops.CamChainOperationRemove,
        ops.CamChainOperationUp,
        ops.CamChainOperationDown,

        ops.CamOperationAdd,
        ops.CamOperationCopy,
        ops.CamOperationRemove,
        ops.CamOperationMove,
        # bridges related
        ops.CamBridgesAdd,
        # 5 axis ops
        ops.CamOrientationAdd,
        # shape packing
        ops.CamPackObjects,
        ops.CamSliceObjects,
        # other tools
        curvecamtools.CamCurveBoolean,
        curvecamtools.CamCurveConvexHull,
        curvecamtools.CamCurveHatch,
        curvecamtools.CamCurvePlate,
        curvecamtools.CamCurveDrawer,
        curvecamcreate.CamCurveFlatCone,
        curvecamtools.CamCurveMortise,
        curvecamtools.CamOffsetSilhouete,
        curvecamtools.CamObjectSilhouete,
        curvecamtools.CamCurveIntarsion,
        curvecamtools.CamCurveOvercuts,
        curvecamtools.CamCurveOvercutsB,
        curvecamtools.CamCurveRemoveDoubles,
        curvecamtools.CamMeshGetPockets,
        curvecamequation.CamSineCurve,
        curvecamequation.CamLissajousCurve,
        curvecamequation.CamHypotrochoidCurve,
        curvecamequation.CamCustomCurve,

        CAM_CUTTER_MT_presets,
        CAM_OPERATION_MT_presets,
        CAM_MACHINE_MT_presets,
        AddPresetCamCutter,
        AddPresetCamOperation,
        AddPresetCamMachine,
        BLENDERCAM_ENGINE,
        # CamBackgroundMonitor
        # pack module:
        PackObjectsSettings,
        SliceObjectsSettings,

    )


def compatible_panels():
    """gets panels that are for blender internal, but are compatible with blender CAM"""
    t = bpy.types
    return (
        # textures
        t.TEXTURE_PT_context_texture,
        t.TEXTURE_PT_preview,
        t.TEXTURE_PT_colors,
        t.TEXTURE_PT_clouds,
        t.TEXTURE_PT_wood,
        t.TEXTURE_PT_marble,
        t.TEXTURE_PT_magic,
        t.TEXTURE_PT_blend,
        t.TEXTURE_PT_stucci,
        t.TEXTURE_PT_image,
        t.TEXTURE_PT_image_sampling,
        t.TEXTURE_PT_image_mapping,
        t.TEXTURE_PT_envmap,
        t.TEXTURE_PT_envmap_sampling,
        t.TEXTURE_PT_musgrave,
        t.TEXTURE_PT_voronoi,
        t.TEXTURE_PT_distortednoise,
        t.TEXTURE_PT_voxeldata,
        t.TEXTURE_PT_pointdensity,
        t.TEXTURE_PT_pointdensity_turbulence,
        t.TEXTURE_PT_ocean,
        t.TEXTURE_PT_mapping,
        t.TEXTURE_PT_influence,
        t.TEXTURE_PT_custom_props,

        # meshes
        t.DATA_PT_context_mesh,
        t.DATA_PT_normals,
        t.DATA_PT_texture_space,
        t.DATA_PT_shape_keys,
        t.DATA_PT_uv_texture,
        t.DATA_PT_vertex_colors,
        t.DATA_PT_vertex_groups,
        t.DATA_PT_customdata,
        t.DATA_PT_custom_props_mesh,

        # materials
        t.MATERIAL_PT_context_material,
        t.MATERIAL_PT_preview,
        t.MATERIAL_PT_pipeline,
        t.MATERIAL_PT_diffuse,
        t.MATERIAL_PT_specular,
        t.MATERIAL_PT_shading,
        t.MATERIAL_PT_transp,
        t.MATERIAL_PT_mirror,
        t.MATERIAL_PT_sss,
        t.MATERIAL_PT_halo,
        t.MATERIAL_PT_flare,
        t.MATERIAL_PT_game_settings,
        t.MATERIAL_PT_physics,
        t.MATERIAL_PT_strand,
        t.MATERIAL_PT_options,
        t.MATERIAL_PT_shadow,
        t.MATERIAL_PT_transp_game,
        t.MATERIAL_PT_volume_density,
        t.MATERIAL_PT_volume_shading,
        t.MATERIAL_PT_volume_lighting,
        t.MATERIAL_PT_volume_transp,
        t.MATERIAL_PT_volume_integration,
        t.MATERIAL_PT_volume_options,
        t.MATERIAL_PT_custom_props,

        # particles
        t.PARTICLE_PT_context_particles,
        t.PARTICLE_PT_emission,
        t.PARTICLE_PT_hair_dynamics,
        t.PARTICLE_PT_cache,
        t.PARTICLE_PT_velocity,
        t.PARTICLE_PT_rotation,
        t.PARTICLE_PT_physics,
        t.PARTICLE_PT_boidbrain,
        t.PARTICLE_PT_render,
        t.PARTICLE_PT_draw,
        t.PARTICLE_PT_children,
        t.PARTICLE_PT_field_weights,
        t.PARTICLE_PT_force_fields,
        t.PARTICLE_PT_vertexgroups,

        # scene
        t.SCENE_PT_scene,
        t.SCENE_PT_unit,
        t.SCENE_PT_keying_sets,
        t.SCENE_PT_keying_set_paths,
        t.SCENE_PT_color_management,

        t.SCENE_PT_audio,
        t.SCENE_PT_physics,
        t.SCENE_PT_rigid_body_world,
        t.SCENE_PT_rigid_body_cache,
        t.SCENE_PT_rigid_body_field_weights,
        t.SCENE_PT_simplify,
        t.SCENE_PT_custom_props,

        # world
        t.WORLD_PT_context_world,
        t.WORLD_PT_preview,
        t.WORLD_PT_world,
        t.WORLD_PT_ambient_occlusion,
        t.WORLD_PT_environment_lighting,
        t.WORLD_PT_indirect_lighting,
        t.WORLD_PT_gather,
        t.WORLD_PT_mist,
        t.WORLD_PT_custom_props

    )


classes = [
    ui.CAM_UL_operations,
    ui.CAM_UL_chains,
    camOperation,
    opReference,
    camChain,
    machineSettings,
    CamAddonPreferences,
    import_settings,

    ui.CAM_CHAINS_Panel,
    ui.CAM_OPERATIONS_Panel,
    ui.CAM_INFO_Panel,
    ui.CAM_MATERIAL_Panel,
    ui.CAM_OPERATION_PROPERTIES_Panel,
    ui.CAM_OPTIMISATION_Panel,
    ui.CAM_AREA_Panel,
    ui.CAM_MOVEMENT_Panel,
    ui.CAM_FEEDRATE_Panel,
    ui.CAM_CUTTER_Panel,
    ui.CAM_GCODE_Panel,
    ui.CAM_MACHINE_Panel,
    ui.CAM_PACK_Panel,
    ui.CAM_SLICE_Panel,
    ui.VIEW3D_PT_tools_curvetools,
    ui.VIEW3D_PT_tools_create,
    ui.CustomPanel,
    ui.WM_OT_gcode_import,

    ops.PathsBackground,
    ops.KillPathsBackground,
    ops.CalculatePath,
    ops.PathsChain,
    ops.PathExportChain,
    ops.PathsAll,
    ops.PathExport,
    ops.CAMPositionObject,
    ops.CAMSimulate,
    ops.CAMSimulateChain,
    ops.CamChainAdd,
    ops.CamChainRemove,
    ops.CamChainOperationAdd,
    ops.CamChainOperationRemove,
    ops.CamChainOperationUp,
    ops.CamChainOperationDown,

    ops.CamOperationAdd,
    ops.CamOperationCopy,
    ops.CamOperationRemove,
    ops.CamOperationMove,
    # bridges related
    ops.CamBridgesAdd,
    # 5 axis ops
    ops.CamOrientationAdd,
    # shape packing
    ops.CamPackObjects,
    ops.CamSliceObjects,
    # other tools
    curvecamtools.CamCurveBoolean,
    curvecamtools.CamCurveConvexHull,
    curvecamtools.CamOffsetSilhouete,
    curvecamtools.CamObjectSilhouete,
    curvecamtools.CamCurveIntarsion,
    curvecamtools.CamCurveOvercuts,
    curvecamtools.CamCurveOvercutsB,
    curvecamtools.CamCurveRemoveDoubles,
    curvecamtools.CamMeshGetPockets,

    curvecamequation.CamSineCurve,
    curvecamequation.CamLissajousCurve,
    curvecamequation.CamHypotrochoidCurve,
    curvecamequation.CamCustomCurve,

    curvecamcreate.CamCurveHatch,
    curvecamcreate.CamCurvePlate,
    curvecamcreate.CamCurveDrawer,
    curvecamcreate.CamCurveGear,
    curvecamcreate.CamCurveFlatCone,
    curvecamcreate.CamCurveMortise,
    curvecamcreate.CamCurveInterlock,
    curvecamcreate.CamCurvePuzzle,

    CAM_CUTTER_MT_presets,
    CAM_OPERATION_MT_presets,
    CAM_MACHINE_MT_presets,
    AddPresetCamCutter,
    AddPresetCamOperation,
    AddPresetCamMachine,
    BLENDERCAM_ENGINE,
    # CamBackgroundMonitor
    # pack module:
    PackObjectsSettings,
    SliceObjectsSettings,
]


def register():
    for p in classes:
        bpy.utils.register_class(p)

    s = bpy.types.Scene

    s.cam_chains = bpy.props.CollectionProperty(type=camChain)
    s.cam_active_chain = bpy.props.IntProperty(name="CAM Active Chain", description="The selected chain")

    s.cam_operations = bpy.props.CollectionProperty(type=camOperation)

    s.cam_active_operation = bpy.props.IntProperty(name="CAM Active Operation", description="The selected operation",
                                                   update=updateOperation)
    s.cam_machine = bpy.props.PointerProperty(type=machineSettings)

    s.cam_import_gcode = bpy.props.PointerProperty(type=import_settings)

    s.cam_text = bpy.props.StringProperty()
    bpy.app.handlers.frame_change_pre.append(ops.timer_update)
    bpy.app.handlers.load_post.append(check_operations_on_load)
    # bpy.types.INFO_HT_header.append(header_info)

    s.cam_pack = bpy.props.PointerProperty(type=PackObjectsSettings)

    s.cam_slice = bpy.props.PointerProperty(type=SliceObjectsSettings)


def unregister():
    for p in classes:
        bpy.utils.unregister_class(p)
    s = bpy.types.Scene

    # cam chains are defined hardly now.
    del s.cam_chains
    del s.cam_active_chain
    del s.cam_operations
    del s.cam_active_operation
    del s.cam_machine
    del s.cam_import_gcode
    del s.cam_text
    del s.cam_pack
    del s.cam_slice
