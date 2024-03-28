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
# ***** END GPL LICENCE BLOCK ****
import subprocess
import sys
try:
    import shapely
except ModuleNotFoundError:
    # pip install required python stuff
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", " pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "shapely", "Equation", "opencamlib"])
    # install numba if available for this platform, ignore failure
    subprocess.run([sys.executable, "-m", "pip", "install", "numba"])

from shapely import geometry as sgeometry  # noqa

from .ui import *
from .version import __version__
from . import (
    ui,
    ops,
    constants,
    curvecamtools,
    curvecamequation,
    curvecamcreate,
    utils,
    simple,
    polygon_utils_cam,
    autoupdate,
    basrelief,
)  # , post_processors
from .utils import (
    updateMachine,
    updateRest,
    updateOperation,
    updateOperationValid,
    operationValid,
    updateZbufferImage,
    updateOffsetImage,
    updateStrategy,
    updateCutout,
    updateChipload,
    updateRotation,
    update_operation,
    getStrategyList,
    updateBridges,
)
import bl_operators
import blf
import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    CollectionProperty,
)
from bpy.types import (
    Menu,
    Operator,
    UIList,
    AddonPreferences,
)
from bpy_extras.object_utils import object_data_add
import bpy.ops
import math
from mathutils import *
import numpy
import os
import pickle
import shutil
import threading
import time

from pathlib import Path

bl_info = {
    "name": "CAM - gcode generation tools",
    "author": "Vilem Novak & Contributors",
    "version":(1,0,12),
    "blender": (3, 6, 0),
    "location": "Properties > render",
    "description": "Generate machining paths for CNC",
    "warning": "",
    "doc_url": "https://blendercam.com/",
    "tracker_url": "",
    "category": "Scene"}


class CamAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    experimental: BoolProperty(
        name="Show experimental features",
        default=False,
    )

    update_source: StringProperty(
        name="Source of updates for the addon",
        description="This can be either a github repo link in which case "
        "it will download the latest release on there, "
        "or an api link like "
        "https://api.github.com/repos/<author>/blendercam/commits"
        " to get from a github repository",
        default="https://github.com/pppalain/blendercam",
    )

    last_update_check: IntProperty(
        name="Last update time",
        default=0,
    )

    last_commit_hash: StringProperty(
        name="Hash of last commit from updater",
        default="",
    )

    just_updated: BoolProperty(
        name="Set to true on update or initial install",
        default=True,
    )

    new_version_available: StringProperty(
        name="Set to new version name if one is found",
        default="",
    )

    default_interface_level: EnumProperty(
        name="Interface level in new file",
        description="Choose visible options",
        items=[
            ('0', "Basic", "Only show essential options"),
            ('1', "Advanced", "Show advanced options"),
            ('2', "Complete", "Show all options"),
            ('3', "Experimental", "Show experimental options")
        ],
        default='3',
    )

    default_machine_preset: StringProperty(
        name="Machine preset in new file",
        description="So that machine preset choice persists between files",
        default='',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(
            text="Use experimental features when you want to help development of Blender CAM:")
        layout.prop(self, "experimental")
        layout.prop(self, "update_source")
        layout.label(text="Choose a preset update source")

        UPDATE_SOURCES = [("https://github.com/vilemduha/blendercam", "Stable", "Stable releases (github.com/vilemduja/blendercam)"),
                          ("https://github.com/pppalain/blendercam", "Unstable",
                           "Unstable releases (github.com/pppalain/blendercam)"),
                          # comments for searching in github actions release script to automatically set this repo
                          # if required
                          # REPO ON NEXT LINE
                          ("https://api.github.com/repos/pppalain/blendercam/commits",
                           "Direct from git (may not work)", "Get from git commits directly"),
                          # REPO ON PREV LINE
                          ("", "None", "Don't do auto update"),
                          ]
        grid = layout.grid_flow(align=True)
        for (url, short, long) in UPDATE_SOURCES:
            op = grid.operator("render.cam_set_update_source", text=short)
            op.new_source = url


class machineSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    # name = StringProperty(name="Machine Name", default="Machine")
    post_processor: EnumProperty(
        name='Post processor',
        items=(
            ('ISO', 'Iso', 'exports standardized gcode ISO 6983 (RS-274)'),
            ('MACH3', 'Mach3', 'default mach3'),
            ('EMC', 'LinuxCNC - EMC2',
             'Linux based CNC control software - formally EMC2'),
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
            ('LYNX_OTTER_O', 'Lynx Otter o', 'Lynx Otter o')
        ),
        description='Post processor',
        default='MACH3',
    )
    # units = EnumProperty(name='Units', items = (('IMPERIAL', ''))
    # position definitions:
    use_position_definitions: BoolProperty(
        name="Use position definitions",
        description="Define own positions for op start, "
        "toolchange, ending position",
        default=False,
    )
    starting_position: FloatVectorProperty(
        name='Start position',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )
    mtc_position: FloatVectorProperty(
        name='MTC position',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )
    ending_position: FloatVectorProperty(
        name='End position',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )

    working_area: FloatVectorProperty(
        name='Work Area',
        default=(0.500, 0.500, 0.100),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateMachine,
    )
    feedrate_min: FloatProperty(
        name="Feedrate minimum /min",
        default=0.0,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit='LENGTH',
    )
    feedrate_max: FloatProperty(
        name="Feedrate maximum /min",
        default=2,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit='LENGTH',
    )
    feedrate_default: FloatProperty(
        name="Feedrate default /min",
        default=1.5,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit='LENGTH',
    )
    hourly_rate: FloatProperty(
        name="Price per hour",
        default=100,
        min=0.005,
        precision=2,
    )

    # UNSUPPORTED:

    spindle_min: FloatProperty(
        name="Spindle speed minimum RPM",
        default=5000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_max: FloatProperty(
        name="Spindle speed maximum RPM",
        default=30000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_default: FloatProperty(
        name="Spindle speed default RPM",
        default=15000,
        min=0.00001,
        max=320000,
        precision=1,
    )
    spindle_start_time: FloatProperty(
        name="Spindle start delay seconds",
        description='Wait for the spindle to start spinning before starting '
        'the feeds , in seconds',
        default=0,
        min=0.0000,
        max=320000,
        precision=1,
    )

    axis4: BoolProperty(
        name="#4th axis",
        description="Machine has 4th axis",
        default=0,
    )
    axis5: BoolProperty(
        name="#5th axis",
        description="Machine has 5th axis",
        default=0,
    )

    eval_splitting: BoolProperty(
        name="Split files",
        description="split gcode file with large number of operations",
        default=True,
    )  # split large files
    split_limit: IntProperty(
        name="Operations per file",
        description="Split files with larger number of operations than this",
        min=1000,
        max=20000000,
        default=800000,
    )

    # rotary_axis1 = EnumProperty(name='Axis 1',
    #     items=(
    #         ('X', 'X', 'x'),
    #         ('Y', 'Y', 'y'),
    #         ('Z', 'Z', 'z')),
    #     description='Number 1 rotational axis',
    #     default='X', update = updateOffsetImage)

    collet_size: FloatProperty(
        name="#Collet size",
        description="Collet size for collision detection",
        default=33,
        min=0.00001,
        max=320000,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    # exporter_start = StringProperty(name="exporter start", default="%")

    # post processor options

    output_block_numbers: BoolProperty(
        name="output block numbers",
        description="output block numbers ie N10 at start of line",
        default=False,
    )

    start_block_number: IntProperty(
        name="start block number",
        description="the starting block number ie 10",
        default=10,
    )

    block_number_increment: IntProperty(
        name="block number increment",
        description="how much the block number should "
        "increment for the next line",
        default=10,
    )

    output_tool_definitions: BoolProperty(
        name="output tool definitions",
        description="output tool definitions",
        default=True,
    )

    output_tool_change: BoolProperty(
        name="output tool change commands",
        description="output tool change commands ie: Tn M06",
        default=True,
    )

    output_g43_on_tool_change: BoolProperty(
        name="output G43 on tool change",
        description="output G43 on tool change line",
        default=False,
    )


class PackObjectsSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    sheet_fill_direction: EnumProperty(
        name='Fill direction',
        items=(
            ('X', 'X', 'Fills sheet in X axis direction'),
            ('Y', 'Y', 'Fills sheet in Y axis direction')
        ),
        description='Fill direction of the packer algorithm',
        default='Y',
    )
    sheet_x: FloatProperty(
        name="X size",
        description="Sheet size",
        min=0.001,
        max=10,
        default=0.5,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    sheet_y: FloatProperty(
        name="Y size",
        description="Sheet size",
        min=0.001,
        max=10,
        default=0.5,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    distance: FloatProperty(
        name="Minimum distance",
        description="minimum distance between objects(should be "
        "at least cutter diameter!)",
        min=0.001,
        max=10,
        default=0.01,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    tolerance: FloatProperty(
        name="Placement Tolerance",
        description="Tolerance for placement: smaller value slower placemant",
        min=0.001,
        max=0.02,
        default=0.005,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    rotate: BoolProperty(
        name="enable rotation",
        description="Enable rotation of elements",
        default=True,
    )
    rotate_angle: FloatProperty(
        name="Placement Angle rotation step",
        description="bigger rotation angle,faster placemant",
        default=0.19635 * 4,
        min=math.pi/180,
        max=math.pi,
        precision=5,
        subtype="ANGLE",
        unit="ROTATION",
    )


class SliceObjectsSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    slice_distance: FloatProperty(
        name="Slicing distance",
        description="slices distance in z, should be most often "
        "thickness of plywood sheet.",
        min=0.001,
        max=10,
        default=0.005,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    slice_above0: BoolProperty(
        name="Slice above 0",
        description="only slice model above 0",
        default=False,
    )
    slice_3d: BoolProperty(
        name="3d slice",
        description="for 3d carving",
        default=False,
    )
    indexes: BoolProperty(
        name="add indexes",
        description="adds index text of layer + index",
        default=True,
    )


class import_settings(bpy.types.PropertyGroup):
    split_layers: BoolProperty(
        name="Split Layers",
        description="Save every layer as single Objects in Collection",
        default=False,
    )
    subdivide: BoolProperty(
        name="Subdivide",
        description="Only Subdivide gcode segments that are "
        "bigger than 'Segment length' ",
        default=False,
    )
    output: EnumProperty(
        name="output type",
        items=(
            ('mesh', 'Mesh', 'Make a mesh output'),
            ('curve', 'Curve', 'Make curve output')
        ),
        default='curve',
    )
    max_segment_size: FloatProperty(
        name="",
        description="Only Segments bigger then this value get subdivided",
        default=0.001,
        min=0.0001,
        max=1.0,
        unit="LENGTH",
    )


class camOperation(bpy.types.PropertyGroup):

    material: PointerProperty(
        type=CAM_MATERIAL_Properties
    )
    info: PointerProperty(
        type=CAM_INFO_Properties
    )
    optimisation: PointerProperty(
        type=CAM_OPTIMISATION_Properties
    )
    movement: PointerProperty(
        type=CAM_MOVEMENT_Properties
    )

    name: StringProperty(
        name="Operation Name",
        default="Operation",
        update=updateRest,
    )
    filename: StringProperty(
        name="File name",
        default="Operation",
        update=updateRest,
    )
    auto_export: BoolProperty(
        name="Auto export",
        description="export files immediately after path calculation",
        default=True,
    )
    remove_redundant_points: BoolProperty(
        name="Symplify Gcode",
        description="Remove redundant points sharing the same angle"
                    " as the start vector",
        default=False,
    )
    simplify_tol: IntProperty(
        name="Tolerance",
        description='lower number means more precise',
        default=50,
        min=1,
        max=1000,
    )
    hide_all_others: BoolProperty(
        name="Hide all others",
        description="Hide all other tool pathes except toolpath"
                    " assotiated with selected CAM operation",
        default=False,
    )
    parent_path_to_object: BoolProperty(
        name="Parent path to object",
        description="Parent generated CAM path to source object",
        default=False,
    )
    object_name: StringProperty(
        name='Object',
        description='object handled by this operation',
        update=updateOperationValid,
    )
    collection_name: StringProperty(
        name='Collection',
        description='Object collection handled by this operation',
        update=updateOperationValid,
    )
    curve_object: StringProperty(
        name='Curve source',
        description='curve which will be sampled along the 3d object',
        update=operationValid,
    )
    curve_object1: StringProperty(
        name='Curve target',
        description='curve which will serve as attractor for the '
        'cutter when the cutter follows the curve',
        update=operationValid,
    )
    source_image_name: StringProperty(
        name='image_source',
        description='image source',
        update=operationValid,
    )
    geometry_source: EnumProperty(
        name='Source of data',
        items=(
            ('OBJECT', 'object', 'a'),
            ('COLLECTION', 'Collection of objects', 'a'),
            ('IMAGE', 'Image', 'a')
        ),
        description='Geometry source',
        default='OBJECT',
        update=updateOperationValid,
    )
    cutter_type: EnumProperty(
        name='Cutter',
        items=(
            ('END', 'End', 'end - flat cutter'),
            ('BALLNOSE', 'Ballnose', 'ballnose cutter'),
            ('BULLNOSE', 'Bullnose', 'bullnose cutter ***placeholder **'),
            ('VCARVE', 'V-carve', 'v carve cutter'),
            ('BALLCONE', 'Ballcone', 'Ball with a Cone for Parallel - X'),
            ('CYLCONE', 'Cylinder cone',
             'Cylinder end with a Cone for Parallel - X'),
            ('LASER', 'Laser', 'Laser cutter'),
            ('PLASMA', 'Plasma', 'Plasma cutter'),
            ('CUSTOM', 'Custom-EXPERIMENTAL',
             'modelled cutter - not well tested yet.')
        ),
        description='Type of cutter used',
        default='END',
        update=updateZbufferImage,
    )
    cutter_object_name: StringProperty(
        name='Cutter object',
        description='object used as custom cutter for this operation',
        update=updateZbufferImage,
    )

    machine_axes: EnumProperty(
        name='Number of axes',
        items=(
            ('3', '3 axis', 'a'),
            ('4', '#4 axis - EXPERIMENTAL', 'a'),
            ('5', '#5 axis - EXPERIMENTAL', 'a')
        ),
        description='How many axes will be used for the operation',
        default='3',
        update=updateStrategy,
    )
    strategy: EnumProperty(
        name='Strategy',
        items=getStrategyList,
        description='Strategy',
        update=updateStrategy,
    )

    strategy4axis: EnumProperty(
        name='4 axis Strategy',
        items=(
            ('PARALLELR', 'Parallel around 1st rotary axis',
             'Parallel lines around first rotary axis'),
            ('PARALLEL', 'Parallel along 1st rotary axis',
             'Parallel lines along first rotary axis'),
            ('HELIX', 'Helix around 1st rotary axis',
             'Helix around rotary axis'),
            ('INDEXED', 'Indexed 3-axis',
             'all 3 axis strategies, just applied to the 4th axis'),
            ('CROSS', 'Cross', 'Cross paths')
        ),
        description='#Strategy',
        default='PARALLEL',
        update=updateStrategy,
    )
    strategy5axis: EnumProperty(
        name='Strategy',
        items=(
            ('INDEXED', 'Indexed 3-axis',
             'all 3 axis strategies, just rotated by 4+5th axes'),
        ),
        description='5 axis Strategy',
        default='INDEXED',
        update=updateStrategy,
    )

    rotary_axis_1: EnumProperty(
        name='Rotary axis',
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
        ),
        description='Around which axis rotates the first rotary axis',
        default='X',
        update=updateStrategy,
    )
    rotary_axis_2: EnumProperty(
        name='Rotary axis 2',
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
        ),
        description='Around which axis rotates the second rotary axis',
        default='Z',
        update=updateStrategy,
    )

    skin: FloatProperty(
        name="Skin",
        description="Material to leave when roughing ",
        min=0.0,
        max=1.0,
        default=0.0,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateOffsetImage,
    )
    inverse: BoolProperty(
        name="Inverse milling",
        description="Male to female model conversion",
        default=False,
        update=updateOffsetImage,
    )
    array: BoolProperty(
        name="Use array",
        description="Create a repetitive array for producing the "
        "same thing many times",
        default=False,
        update=updateRest,
    )
    array_x_count: IntProperty(
        name="X count",
        description="X count",
        default=1,
        min=1,
        max=32000,
        update=updateRest,
    )
    array_y_count: IntProperty(
        name="Y count",
        description="Y count",
        default=1,
        min=1,
        max=32000,
        update=updateRest,
    )
    array_x_distance: FloatProperty(
        name="X distance",
        description="distance between operation origins",
        min=0.00001,
        max=1.0,
        default=0.01,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    array_y_distance: FloatProperty(
        name="Y distance",
        description="distance between operation origins",
        min=0.00001,
        max=1.0,
        default=0.01,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )

    # pocket options
    pocket_option: EnumProperty(
        name='Start Position',
        items=(
            ('INSIDE', 'Inside', 'a'),
            ('OUTSIDE', 'Outside', 'a')
        ),
        description='Pocket starting position',
        default='INSIDE',
        update=updateRest,
    )
    pocketToCurve: BoolProperty(
        name="Pocket to curve",
        description="generates a curve instead of a path",
        default=False,
        update=updateRest,
    )
    # Cutout
    cut_type: EnumProperty(
        name='Cut',
        items=(
            ('OUTSIDE', 'Outside', 'a'),
            ('INSIDE', 'Inside', 'a'),
            ('ONLINE', 'On line', 'a')
        ),
        description='Type of cutter used',
        default='OUTSIDE',
        update=updateRest,
    )
    outlines_count: IntProperty(
        name="Outlines count",
        description="Outlines count",
        default=1,
        min=1,
        max=32,
        update=updateCutout,
    )
    straight: BoolProperty(
        name="Overshoot Style",
        description="Use overshoot cutout instead of conventional rounded",
        default=False,
        update=updateRest,
    )
    # cutter
    cutter_id: IntProperty(
        name="Tool number",
        description="For machines which support tool change based on tool id",
        min=0,
        max=10000,
        default=1,
        update=updateRest,
    )
    cutter_diameter: FloatProperty(
        name="Cutter diameter",
        description="Cutter diameter = 2x cutter radius",
        min=0.000001,
        max=10,
        default=0.003,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateOffsetImage,
    )
    cylcone_diameter: FloatProperty(
        name="Bottom Diameter",
        description="Bottom diameter",
        min=0.000001,
        max=10,
        default=0.003,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateOffsetImage,
    )
    cutter_length: FloatProperty(
        name="#Cutter length",
        description="#not supported#Cutter length",
        min=0.0,
        max=100.0,
        default=25.0,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateOffsetImage,
    )
    cutter_flutes: IntProperty(
        name="Cutter flutes",
        description="Cutter flutes",
        min=1,
        max=20,
        default=2,
        update=updateChipload,
    )
    cutter_tip_angle: FloatProperty(
        name="Cutter v-carve angle",
        description="Cutter v-carve angle",
        min=0.0,
        max=180.0,
        default=60.0,
        precision=constants.PRECISION,
        update=updateOffsetImage,
    )
    ball_radius: FloatProperty(
        name="Ball radius",
        description="Radius of",
        min=0.0,
        max=0.035,
        default=0.001,
        unit="LENGTH",
        precision=constants.PRECISION,
        update=updateOffsetImage,
    )
    # ball_cone_flute: FloatProperty(name="BallCone Flute Length", description="length of flute", min=0.0,
    #                                 max=0.1, default=0.017, unit="LENGTH", precision=constants.PRECISION, update=updateOffsetImage)
    bull_corner_radius: FloatProperty(
        name="Bull Corner Radius",
        description="Radius tool bit corner",
        min=0.0,
        max=0.035,
        default=0.005,
        unit="LENGTH",
        precision=constants.PRECISION,
        update=updateOffsetImage,
    )

    cutter_description: StringProperty(
        name="Tool Description",
        default="",
        update=updateOffsetImage,
    )

    Laser_on: StringProperty(
        name="Laser ON string",
        default="M68 E0 Q100",
    )
    Laser_off: StringProperty(
        name="Laser OFF string",
        default="M68 E0 Q0",
    )
    Laser_cmd: StringProperty(
        name="Laser command",
        default="M68 E0 Q",
    )
    Laser_delay: FloatProperty(
        name="Laser ON Delay",
        description="time after fast move to turn on laser and "
        "let machine stabilize",
        default=0.2,
    )
    Plasma_on: StringProperty(
        name="Plasma ON string",
        default="M03",
    )
    Plasma_off: StringProperty(
        name="Plasma OFF string",
        default="M05",
    )
    Plasma_delay: FloatProperty(
        name="Plasma ON Delay",
        description="time after fast move to turn on Plasma and "
        "let machine stabilize",
        default=0.1,
    )
    Plasma_dwell: FloatProperty(
        name="Plasma dwell time",
        description="Time to dwell and warm up the torch",
        default=0.0,
    )

    # steps
    dist_between_paths: FloatProperty(
        name="Distance between toolpaths",
        default=0.001,
        min=0.00001,
        max=32,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    dist_along_paths: FloatProperty(
        name="Distance along toolpaths",
        default=0.0002,
        min=0.00001,
        max=32,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    parallel_angle: FloatProperty(
        name="Angle of paths",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=updateRest,
    )

    old_rotation_A: FloatProperty(
        name="A axis angle",
        description="old value of Rotate A axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=updateRest,
    )

    old_rotation_B: FloatProperty(
        name="A axis angle",
        description="old value of Rotate A axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=updateRest,
    )

    rotation_A: FloatProperty(
        name="A axis angle",
        description="Rotate A axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=updateRotation,
    )
    enable_A: BoolProperty(
        name="Enable A axis",
        description="Rotate A axis",
        default=False,
        update=updateRotation,
    )
    A_along_x: BoolProperty(
        name="A Along X ",
        description="A Parallel to X",
        default=True,
        update=updateRest,
    )

    rotation_B: FloatProperty(
        name="B axis angle",
        description="Rotate B axis\nto specified angle",
        default=0,
        min=-360,
        max=360,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=updateRotation,
    )
    enable_B: BoolProperty(
        name="Enable B axis",
        description="Rotate B axis",
        default=False,
        update=updateRotation,
    )

    # carve only
    carve_depth: FloatProperty(
        name="Carve depth",
        default=0.001,
        min=-.100,
        max=32,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )

    # drill only
    drill_type: EnumProperty(
        name='Holes on',
        items=(
            ('MIDDLE_SYMETRIC', 'Middle of symetric curves', 'a'),
            ('MIDDLE_ALL', 'Middle of all curve parts', 'a'),
            ('ALL_POINTS', 'All points in curve', 'a')
        ),
        description='Strategy to detect holes to drill',
        default='MIDDLE_SYMETRIC',
        update=updateRest,
    )
    # waterline only
    slice_detail: FloatProperty(
        name="Distance betwen slices",
        default=0.001,
        min=0.00001,
        max=32,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    waterline_fill: BoolProperty(
        name="Fill areas between slices",
        description="Fill areas between slices in waterline mode",
        default=True,
        update=updateRest,
    )
    waterline_project: BoolProperty(
        name="Project paths - not recomended",
        description="Project paths in areas between slices",
        default=True,
        update=updateRest,
    )

    # movement and ramps
    use_layers: BoolProperty(
        name="Use Layers",
        description="Use layers for roughing",
        default=True,
        update=updateRest,
    )
    stepdown: FloatProperty(
        name="",
        description="Layer height",
        default=0.01,
        min=0.00001,
        max=32,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    lead_in: FloatProperty(
        name="Lead in radius",
        description="Lead out radius for torch or laser to turn off",
        min=0.00,
        max=1,
        default=0.0,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    lead_out: FloatProperty(
        name="Lead out radius",
        description="Lead out radius for torch or laser to turn off",
        min=0.00,
        max=1,
        default=0.0,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    profile_start: IntProperty(
        name="Start point",
        description="Start point offset",
        min=0,
        default=0,
        update=updateRest,
    )

    # helix_angle: FloatProperty(name="Helix ramp angle", default=3*math.pi/180, min=0.00001, max=math.pi*0.4999,precision=1, subtype="ANGLE" , unit="ROTATION" , update = updateRest)

    minz: FloatProperty(
        name="Operation depth end",
        default=-0.01,
        min=-3,
        max=3,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )

    minz_from: EnumProperty(
        name='Set max depth from',
        description='Set maximum operation depth',
        items=(
            ('OBJECT', 'Object', 'Set max operation depth from Object'),
            ('MATERIAL', 'Material', 'Set max operation depth from Material'),
            ('CUSTOM', 'Custom', 'Custom max depth'),
        ),
        default='OBJECT',
        update=updateRest,
    )

    start_type: EnumProperty(
        name='Start type',
        items=(
            ('ZLEVEL', 'Z level', 'Starts on a given Z level'),
            ('OPERATIONRESULT', 'Rest milling',
             'For rest milling, operations have to be '
             'put in chain for this to work well.'),
        ),
        description='Starting depth',
        default='ZLEVEL',
        update=updateStrategy,
    )

    maxz: FloatProperty(
        name="Operation depth start",
        description='operation starting depth',
        default=0,
        min=-3,
        max=10,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )  # EXPERIMENTAL

    first_down: BoolProperty(
        name="First down",
        description="First go down on a contour, then go to the next one",
        default=False,
        update=update_operation,
    )

    #######################################################
    # Image related
    ####################################################

    source_image_scale_z: FloatProperty(
        name="Image source depth scale",
        default=0.01,
        min=-1,
        max=1,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateZbufferImage,
    )
    source_image_size_x: FloatProperty(
        name="Image source x size",
        default=0.1,
        min=-10,
        max=10,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateZbufferImage,
    )
    source_image_offset: FloatVectorProperty(
        name='Image offset',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
        update=updateZbufferImage,
    )

    source_image_crop: BoolProperty(
        name="Crop source image",
        description="Crop source image - the position of the sub-rectangle "
        "is relative to the whole image, so it can be used for e.g. "
        "finishing just a part of an image",
        default=False,
        update=updateZbufferImage,
    )
    source_image_crop_start_x: FloatProperty(
        name='crop start x',
        default=0,
        min=0,
        max=100,
        precision=constants.PRECISION,
        subtype='PERCENTAGE',
        update=updateZbufferImage,
    )
    source_image_crop_start_y: FloatProperty(
        name='crop start y',
        default=0,
        min=0,
        max=100,
        precision=constants.PRECISION,
        subtype='PERCENTAGE',
        update=updateZbufferImage,
    )
    source_image_crop_end_x: FloatProperty(
        name='crop end x',
        default=100,
        min=0,
        max=100,
        precision=constants.PRECISION,
        subtype='PERCENTAGE',
        update=updateZbufferImage,
    )
    source_image_crop_end_y: FloatProperty(
        name='crop end y',
        default=100,
        min=0,
        max=100,
        precision=constants.PRECISION,
        subtype='PERCENTAGE',
        update=updateZbufferImage,
    )

    #########################################################
    # Toolpath and area related
    #####################################################

    ambient_behaviour: EnumProperty(
        name='Ambient',
        items=(('ALL', 'All', 'a'), ('AROUND', 'Around', 'a')),
        description='handling ambient surfaces',
        default='ALL',
        update=updateZbufferImage,
    )

    ambient_radius: FloatProperty(
        name="Ambient radius",
        description="Radius around the part which will be milled if "
        "ambient is set to Around",
        min=0.0,
        max=100.0,
        default=0.01,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    # ambient_cutter = EnumProperty(name='Borders',items=(('EXTRAFORCUTTER', 'Extra for cutter', "Extra space for cutter is cut around the segment"),('ONBORDER', "Cutter on edge", "Cutter goes exactly on edge of ambient with it's middle") ,('INSIDE', "Inside segment", 'Cutter stays within segment')	 ),description='handling of ambient and cutter size',default='INSIDE')
    use_limit_curve: BoolProperty(
        name="Use limit curve",
        description="A curve limits the operation area",
        default=False,
        update=updateRest,
    )
    ambient_cutter_restrict: BoolProperty(
        name="Cutter stays in ambient limits",
        description="Cutter doesn't get out from ambient limits otherwise "
        "goes on the border exactly",
        default=True,
        update=updateRest,
    )  # restricts cutter inside ambient only
    limit_curve: StringProperty(
        name='Limit curve',
        description='curve used to limit the area of the operation',
        update=updateRest,
    )

    # feeds
    feedrate: FloatProperty(
        name="Feedrate",
        description="Feedrate in units per minute",
        min=0.00005,
        max=50.0,
        default=1.0,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateChipload,
    )
    plunge_feedrate: FloatProperty(
        name="Plunge speed ",
        description="% of feedrate",
        min=0.1,
        max=100.0,
        default=50.0,
        precision=1,
        subtype='PERCENTAGE',
        update=updateRest,
    )
    plunge_angle: FloatProperty(
        name="Plunge angle",
        description="What angle is allready considered to plunge",
        default=math.pi / 6,
        min=0,
        max=math.pi * 0.5,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=updateRest,
    )
    spindle_rpm: FloatProperty(
        name="Spindle rpm",
        description="Spindle speed ",
        min=0,
        max=60000,
        default=12000,
        update=updateChipload,
    )

    # optimization and performance

    do_simulation_feedrate: BoolProperty(
        name="Adjust feedrates with simulation EXPERIMENTAL",
        description="Adjust feedrates with simulation",
        default=False,
        update=updateRest,
    )

    dont_merge: BoolProperty(
        name="Dont merge outlines when cutting",
        description="this is usefull when you want to cut around everything",
        default=False,
        update=updateRest,
    )

    pencil_threshold: FloatProperty(
        name="Pencil threshold",
        default=0.00002,
        min=0.00000001,
        max=1,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )

    crazy_threshold1: FloatProperty(
        name="min engagement",
        default=0.02,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        update=updateRest,
    )
    crazy_threshold5: FloatProperty(
        name="optimal engagement",
        default=0.3,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        update=updateRest,
    )
    crazy_threshold2: FloatProperty(
        name="max engagement",
        default=0.5,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        update=updateRest,
    )
    crazy_threshold3: FloatProperty(
        name="max angle",
        default=2,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        update=updateRest,
    )
    crazy_threshold4: FloatProperty(
        name="test angle step",
        default=0.05,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        update=updateRest,
    )
    # Add pocket operation to medial axis
    add_pocket_for_medial: BoolProperty(
        name="Add pocket operation",
        description="clean unremoved material after medial axis",
        default=True,
        update=updateRest,
    )

    add_mesh_for_medial: BoolProperty(
        name="Add Medial mesh",
        description="Medial operation returns mesh for editing and "
        "further processing",
        default=False,
        update=updateRest,
    )
    ####
    medial_axis_threshold: FloatProperty(
        name="Long vector threshold",
        default=0.001,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    medial_axis_subdivision: FloatProperty(
        name="Fine subdivision",
        default=0.0002,
        min=0.00000001,
        max=100,
        precision=constants.PRECISION,
        unit="LENGTH",
        update=updateRest,
    )
    # calculations

    # bridges
    use_bridges: BoolProperty(
        name="Use bridges",
        description="use bridges in cutout",
        default=False,
        update=updateBridges,
    )
    bridges_width: FloatProperty(
        name='width of bridges',
        default=0.002,
        unit='LENGTH',
        precision=constants.PRECISION,
        update=updateBridges,
    )
    bridges_height: FloatProperty(
        name='height of bridges',
        description="Height from the bottom of the cutting operation",
        default=0.0005,
        unit='LENGTH',
        precision=constants.PRECISION,
        update=updateBridges,
    )
    bridges_collection_name: StringProperty(
        name='Bridges Collection',
        description='Collection of curves used as bridges',
        update=operationValid,
    )
    use_bridge_modifiers: BoolProperty(
        name="use bridge modifiers",
        description="include bridge curve modifiers using render level when "
        "calculating operation, does not effect original bridge data",
        default=True,
        update=updateBridges,
    )

    # commented this - auto bridges will be generated, but not as a setting of the operation
    # bridges_placement = EnumProperty(name='Bridge placement',
    #     items=(
    #         ('AUTO','Automatic', 'Automatic bridges with a set distance'),
    #         ('MANUAL','Manual', 'Manual placement of bridges'),
    #         ),
    #     description='Bridge placement',
    #     default='AUTO',
    #     update = updateStrategy)
    #
    # bridges_per_curve = IntProperty(name="minimum bridges per curve", description="", default=4, min=1, max=512, update = updateBridges)
    # bridges_max_distance = FloatProperty(name = 'Maximum distance between bridges', default=0.08, unit='LENGTH', precision=constants.PRECISION, update = updateBridges)

    use_modifiers: BoolProperty(
        name="use mesh modifiers",
        description="include mesh modifiers using render level when "
        "calculating operation, does not effect original mesh",
        default=True,
        update=operationValid,
    )
    # optimisation panel

    # material settings


##############################################################################
    # MATERIAL SETTINGS

    min: FloatVectorProperty(
        name='Operation minimum',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
    )
    max: FloatVectorProperty(
        name='Operation maximum',
        default=(0, 0, 0),
        unit='LENGTH',
        precision=constants.PRECISION,
        subtype="XYZ",
    )

    # g-code options for operation
    output_header: BoolProperty(
        name="output g-code header",
        description="output user defined g-code command header"
        " at start of operation",
        default=False,
    )

    gcode_header: StringProperty(
        name="g-code header",
        description="g-code commands at start of operation."
        " Use ; for line breaks",
        default="G53 G0",
    )

    enable_dust: BoolProperty(
        name="Dust collector",
        description="output user defined g-code command header"
        " at start of operation",
        default=False,
    )

    gcode_start_dust_cmd: StringProperty(
        name="Start dust collector",
        description="commands to start dust collection. Use ; for line breaks",
        default="M100",
    )

    gcode_stop_dust_cmd: StringProperty(
        name="Stop dust collector",
        description="command to stop dust collection. Use ; for line breaks",
        default="M101",
    )

    enable_hold: BoolProperty(
        name="Hold down",
        description="output hold down command at start of operation",
        default=False,
    )

    gcode_start_hold_cmd: StringProperty(
        name="g-code header",
        description="g-code commands at start of operation."
        " Use ; for line breaks",
        default="M102",
    )

    gcode_stop_hold_cmd: StringProperty(
        name="g-code header",
        description="g-code commands at end operation. Use ; for line breaks",
        default="M103",
    )

    enable_mist: BoolProperty(
        name="Mist",
        description="Mist command at start of operation",
        default=False,
    )

    gcode_start_mist_cmd: StringProperty(
        name="g-code header",
        description="g-code commands at start of operation."
        " Use ; for line breaks",
        default="M104",
    )

    gcode_stop_mist_cmd: StringProperty(
        name="g-code header",
        description="g-code commands at end operation. Use ; for line breaks",
        default="M105",
    )

    output_trailer: BoolProperty(
        name="output g-code trailer",
        description="output user defined g-code command trailer"
        " at end of operation",
        default=False,
    )

    gcode_trailer: StringProperty(
        name="g-code trailer",
        description="g-code commands at end of operation."
        " Use ; for line breaks",
        default="M02",
    )

    # internal properties
    ###########################################

    # testing = IntProperty(name="developer testing ", description="This is just for script authors for help in coding, keep 0", default=0, min=0, max=512)
    offset_image = numpy.array([], dtype=float)
    zbuffer_image = numpy.array([], dtype=float)

    silhouete = sgeometry.Polygon()
    ambient = sgeometry.Polygon()
    operation_limit = sgeometry.Polygon()
    borderwidth = 50
    object = None
    path_object_name: StringProperty(
        name='Path object',
        description='actual cnc path'
    )

    # update and tags and related

    changed: BoolProperty(
        name="True if any of the operation settings has changed",
        description="mark for update",
        default=False,
    )
    update_zbufferimage_tag: BoolProperty(
        name="mark zbuffer image for update",
        description="mark for update",
        default=True,
    )
    update_offsetimage_tag: BoolProperty(
        name="mark offset image for update",
        description="mark for update",
        default=True,
    )
    update_silhouete_tag: BoolProperty(
        name="mark silhouete image for update",
        description="mark for update",
        default=True,
    )
    update_ambient_tag: BoolProperty(
        name="mark ambient polygon for update",
        description="mark for update",
        default=True,
    )
    update_bullet_collision_tag: BoolProperty(
        name="mark bullet collisionworld for update",
        description="mark for update",
        default=True,
    )

    valid: BoolProperty(
        name="Valid",
        description="True if operation is ok for calculation",
        default=True,
    )
    changedata: StringProperty(
        name='changedata',
        description='change data for checking if stuff changed.',
    )

    # process related data

    computing: BoolProperty(
        name="Computing right now",
        description="",
        default=False,
    )
    pid: IntProperty(
        name="process id",
        description="Background process id",
        default=-1,
    )
    outtext: StringProperty(
        name='outtext',
        description='outtext',
        default='',
    )


# this type is defined just to hold reference to operations for chains
class opReference(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Operation name",
        default="Operation",
    )
    computing = False  # for UiList display


# chain is just a set of operations which get connected on export into 1 file.
class camChain(bpy.types.PropertyGroup):
    index: IntProperty(
        name="index",
        description="index in the hard-defined camChains",
        default=-1,
    )
    active_operation: IntProperty(
        name="active operation",
        description="active operation in chain",
        default=-1,
    )
    name: StringProperty(
        name="Chain Name",
        default="Chain",
    )
    filename: StringProperty(
        name="File name",
        default="Chain",
    )  # filename of
    valid: BoolProperty(
        name="Valid",
        description="True if whole chain is ok for calculation",
        default=True,
    )
    computing: BoolProperty(
        name="Computing right now",
        description="",
        default=False,
    )
    # this is to hold just operation names.
    operations: CollectionProperty(
        type=opReference,
    )


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

    @classmethod
    def post_cb(cls, context):
        name = cls.bl_label
        filepath = bpy.utils.preset_find(name,
                                         cls.preset_subdir,
                                         display_name=True,
                                         ext=".py")
        context.preferences.addons['cam'].preferences.default_machine_preset = filepath
        bpy.ops.wm.save_userpref()


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

    preset_defines = [
        "o = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"]

    preset_values = ['o.use_layers', 'o.info.duration', 'o.info.chipload', 'o.material.estimate_from_model', 'o.movement.stay_low', 'o.carve_depth',
                     'o.dist_along_paths', 'o.source_image_crop_end_x', 'o.source_image_crop_end_y', 'o.material.size',
                     'o.material.radius_around_model', 'o.use_limit_curve', 'o.cut_type', 'o.optimisation.use_exact',
                     'o.optimisation.exact_subdivide_edges', 'o.minz_from', 'o.movement.free_height',
                     'o.source_image_crop_start_x', 'o.movement.insideout', 'o.movement.movement.spindle_rotation', 'o.skin',
                     'o.source_image_crop_start_y', 'o.movement.type', 'o.source_image_crop', 'o.limit_curve',
                     'o.spindle_rpm', 'o.ambient_behaviour', 'o.cutter_type', 'o.source_image_scale_z',
                     'o.cutter_diameter', 'o.source_image_size_x', 'o.curve_object', 'o.curve_object1',
                     'o.cutter_flutes', 'o.ambient_radius', 'o.optimisation.simulation_detail', 'o.update_offsetimage_tag',
                     'o.dist_between_paths', 'o.max', 'o.min', 'o.optimisation.pixsize', 'o.slice_detail', 'o.movement.parallel_step_back',
                     'o.drill_type', 'o.source_image_name', 'o.dont_merge', 'o.update_silhouete_tag',
                     'o.material.origin', 'o.inverse', 'o.waterline_fill', 'o.source_image_offset', 'o.optimisation.circle_detail',
                     'o.strategy', 'o.update_zbufferimage_tag', 'o.stepdown', 'o.feedrate', 'o.cutter_tip_angle',
                     'o.cutter_id', 'o.path_object_name', 'o.pencil_threshold', 'o.geometry_source',
                     'o.optimize_threshold', 'o.movement.protect_vertical', 'o.plunge_feedrate', 'o.minz', 'o.info.warnings',
                     'o.object_name', 'o.optimize', 'o.parallel_angle', 'o.cutter_length',
                     'o.output_header', 'o.gcode_header', 'o.output_trailer', 'o.gcode_trailer', 'o.use_modifiers',
                     'o.movement.useG64',
                     'o.movement.G64', 'o.enable_A', 'o.enable_B', 'o.A_along_x', 'o.rotation_A', 'o.rotation_B', 'o.straight']

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


_IS_LOADING_DEFAULTS = False


@bpy.app.handlers.persistent
def check_operations_on_load(context):
    global _IS_LOADING_DEFAULTS
    """checks any broken computations on load and reset them."""
    s = bpy.context.scene
    for o in s.cam_operations:
        if o.computing:
            o.computing = False
    # set interface level to previously used level for a new file
    if not bpy.data.filepath:
        _IS_LOADING_DEFAULTS = True
        s.interface.level = bpy.context.preferences.addons['cam'].preferences.default_interface_level
        machine_preset = bpy.context.preferences.addons[
            'cam'].preferences.machine_preset = bpy.context.preferences.addons['cam'].preferences.default_machine_preset
        if len(machine_preset) > 0:
            print("Loading preset:", machine_preset)
            # load last used machine preset
            bpy.ops.script.execute_preset(filepath=machine_preset,
                                          menu_idname="CAM_MACHINE_MT_presets")
        _IS_LOADING_DEFAULTS = False
    # check for updated version of the plugin
    bpy.ops.render.cam_check_updates()
    # copy presets if not there yet
    if bpy.context.preferences.addons['cam'].preferences.just_updated:
        preset_source_path = Path(__file__).parent / 'presets'
        preset_target_path = Path(bpy.utils.script_path_user()) / 'presets'

        def copy_if_not_exists(src, dst):
            if Path(dst).exists() == False:
                shutil.copy2(src, dst)
        shutil.copytree(preset_source_path, preset_target_path,
                        copy_function=copy_if_not_exists, dirs_exist_ok=True)

        bpy.context.preferences.addons['cam'].preferences.just_updated = False
        bpy.ops.wm.save_userpref()


def get_panels():  # convenience function for bot register and unregister functions
    # types = bpy.types
    return (
        ui.CAM_UL_operations,
        # ui.CAM_UL_orientations,
        ui.CAM_UL_chains,
        opReference,
        camChain,
        machineSettings,
        CamAddonPreferences,

        ui.CAM_INTERFACE_Panel,
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
        camOperation,

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
    autoupdate.UpdateSourceOperator,
    autoupdate.Updater,
    autoupdate.UpdateChecker,
    ui.CAM_UL_operations,
    ui.CAM_UL_chains,
    opReference,
    camChain,
    machineSettings,
    CamAddonPreferences,
    import_settings,
    ui.CAM_INTERFACE_Panel,
    ui.CAM_INTERFACE_Properties,
    ui.CAM_CHAINS_Panel,
    ui.CAM_OPERATIONS_Panel,
    ui.CAM_INFO_Properties,
    ui.CAM_INFO_Panel,
    ui.CAM_MATERIAL_Panel,
    ui.CAM_MATERIAL_Properties,
    ui.CAM_MATERIAL_PositionObject,
    ui.CAM_OPERATION_PROPERTIES_Panel,
    ui.CAM_OPTIMISATION_Panel,
    ui.CAM_OPTIMISATION_Properties,
    ui.CAM_AREA_Panel,
    ui.CAM_MOVEMENT_Panel,
    ui.CAM_MOVEMENT_Properties,
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
    camOperation,

]


def register():
    for p in classes:
        bpy.utils.register_class(p)

    s = bpy.types.Scene

    s.cam_chains = CollectionProperty(
        type=camChain,
    )
    s.cam_active_chain = IntProperty(
        name="CAM Active Chain",
        description="The selected chain",
    )

    s.cam_operations = CollectionProperty(
        type=camOperation,
    )

    s.cam_active_operation = IntProperty(
        name="CAM Active Operation",
        description="The selected operation",
        update=updateOperation,
    )
    s.cam_machine = PointerProperty(
        type=machineSettings,
    )

    s.cam_import_gcode = PointerProperty(
        type=import_settings,
    )

    s.cam_text = StringProperty()
    bpy.app.handlers.frame_change_pre.append(ops.timer_update)
    bpy.app.handlers.load_post.append(check_operations_on_load)
    # bpy.types.INFO_HT_header.append(header_info)

    s.cam_pack = PointerProperty(
        type=PackObjectsSettings,
    )

    s.cam_slice = PointerProperty(
        type=SliceObjectsSettings,
    )

    bpy.types.Scene.interface = PointerProperty(
        type=CAM_INTERFACE_Properties,
    )

    basrelief.register()


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
    basrelief.unregister()
