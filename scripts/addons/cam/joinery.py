# blender CAM ops.py (c) 2021 Alain Pelletier
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# blender operators definitions are in this file. They mostly call the functions from utils.py


import bpy
from bpy.props import *
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, parametric, gcodeimportparser
import shapely
from shapely.geometry import Point, LineString, Polygon
import mathutils
import math


# boolean operations for curve objects

def finger_amount(space, size):
    finger_amt = space / size
    if (finger_amt % 1) != 0:
        finger_amt = round(finger_amt) + 1
    if (finger_amt % 2) != 0:
        finger_amt = round(finger_amt) + 1
    return finger_amt


def mortise(length, thickness, finger_play, cx=0, cy=0, rotation=0):
    bpy.ops.curve.simple(align='WORLD',
                         location=(cx, cy, 0),
                         rotation=(0, 0, rotation), Simple_Type='Rectangle',
                         Simple_width=length + finger_play,
                         Simple_length=thickness, shape='3D', outputType='POLY',
                         use_cyclic_u=True,
                         handleType='AUTO', edit_mode=False)


def horizontal_finger(length, thickness, finger_play, amount):
    #   creates _wfa and it's counterpart _wfb
    #   _wfa is centered at 0,0
    #   _wfb is _wfa offset by one length
    #   takes in the
    #   length = length of the mortise
    #   thickness = thickness of the material
    #   fingerplay = tolerance in length of the finger for smooth fit

    for i in range(amount):
        if i == 0:
            mortise(length, thickness, finger_play, 0, thickness / 2)
            bpy.context.active_object.name = "_width_finger"
        else:
            mortise(length, thickness, finger_play, i * 2 * length, thickness / 2)
            bpy.context.active_object.name = "_width_finger"
            mortise(length, thickness, finger_play, -i * 2 * length, thickness / 2)
            bpy.context.active_object.name = "_width_finger"

    simple.joinMultiple("_width_finger")

    bpy.context.active_object.name = "_wfa"
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                  TRANSFORM_OT_translate={"value": (length, 0.0, 0.0)})
    bpy.context.active_object.name = "_wfb"


def vertical_finger(length, thickness, finger_play, amount):
    #   creates _vfa and it's counterpart _vfb
    #   _vfa is starts at 0,0
    #   _wfb is _wfa offset vertically by one length
    #   takes in the
    #   length = length of the mortise
    #   thickness = thickness of the material
    #   fingerplay = tolerance in length of the finger for smooth fit
    #   amount = amount of fingers

    for i in range(amount):
        mortise(length, thickness, finger_play, 0, i * 2 * length + length / 2, rotation=math.pi / 2)
        bpy.context.active_object.name = "_height_finger"

    simple.joinMultiple("_height_finger")
    bpy.context.active_object.name = "_vfa"
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                  TRANSFORM_OT_translate={"value": (0, -length, 0.0)})
    bpy.context.active_object.name = "_vfb"


def finger_pair(name, dx=0, dy=0):
    simple.makeActive(name)

    xpos = (dx / 2) * 1.00001
    ypos = 1.00001 * dy / 2

    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                  TRANSFORM_OT_translate={"value": (xpos, ypos, 0.0)})
    bpy.context.active_object.name = "_finger_pair"

    simple.makeActive(name)

    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                  TRANSFORM_OT_translate={"value": (-xpos, -ypos, 0.0)})
    bpy.context.active_object.name = "_finger_pair"
    simple.joinMultiple("_finger_pair")
    bpy.ops.object.select_all(action='DESELECT')
    return bpy.context.active_object


def create_base_plate(height, width, depth):
    #   creates blank plates for
    #   _back using width and height
    #   _side using height and depth
    #   _bottom using width and depth

    bpy.ops.curve.simple(align='WORLD', location=(0, height / 2, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=width, Simple_length=height, shape='3D', outputType='POLY',
                         use_cyclic_u=True,
                         handleType='AUTO', edit_mode=False)
    bpy.context.active_object.name = "_back"
    bpy.ops.curve.simple(align='WORLD', location=(0, height / 2, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=depth, Simple_length=height, shape='3D', outputType='POLY',
                         use_cyclic_u=True,
                         handleType='AUTO', edit_mode=False)
    bpy.context.active_object.name = "_side"
    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=width, Simple_length=depth, shape='3D', outputType='POLY',
                         use_cyclic_u=True,
                         handleType='AUTO', edit_mode=False)
    bpy.context.active_object.name = "_bottom"

def create_flex_side(length, height, finger_length, finger_thick, finger_tol):
    bpy.ops.curve.simple(align='WORLD', location=(0, height/2, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=length, Simple_length=height, shape='3D', outputType='POLY',
                         use_cyclic_u=True,
                         handleType='AUTO', edit_mode=False)
    bpy.context.active_object.name = "_side"

    horizontal_finger(finger_length, finger_thick, finger_tol, round(length/(2*finger_length)))
    simple.makeActive('_wfa')
    simple.selectMultiple("_wfa")
#    bpy.ops.transform.transform(mode='TRANSLATION', value=(0, -height/2+finger_thick/2, 0.0))
    fingers = bpy.context.active_object
    simple.makeActive('_side')
    fingers.select_set(True)
    bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
    bpy.context.active_object.name = "side"
    simple.removeMultiple('_')

