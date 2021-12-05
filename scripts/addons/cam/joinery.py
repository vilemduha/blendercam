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


def mortice(length, thickness, finger_play, cx=0, cy=0, rotation=0):
    bpy.ops.curve.simple(align='WORLD',
                         location=(cx, cy, 0),
                         rotation=(0, 0, rotation), Simple_Type='Rectangle',
                         Simple_width=length + finger_play,
                         Simple_length=thickness, shape='3D', outputType='POLY',
                         use_cyclic_u=True,
                         handleType='AUTO', edit_mode=False)


def horizontal_finger(length, thickness, finger_play, amount):
    for i in range(amount):
        if i == 0:
            mortice(length, thickness, finger_play, 0, thickness / 2)
            bpy.context.active_object.name = "_width_finger"
        else:
            mortice(length, thickness, finger_play, i * 2 * length, thickness / 2)
            bpy.context.active_object.name = "_width_finger"
            mortice(length, thickness, finger_play, -i * 2 * length, thickness / 2)
            bpy.context.active_object.name = "_width_finger"

    simple.joinMultiple("_width_finger")

    bpy.context.active_object.name = "_wfa"
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                  TRANSFORM_OT_translate={"value": (length, 0.0, 0.0)})
    bpy.context.active_object.name = "_wfb"
