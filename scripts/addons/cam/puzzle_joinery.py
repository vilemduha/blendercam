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

from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, parametric, joinery
import shapely
from shapely.geometry import Point, LineString, Polygon
import mathutils
import math

def rotate(angle):
    bpy.context.active_object.rotation_euler.z = angle

def finger(diameter, inside, DT=1.025):
    RESOLUTION = 12    # Data resolution
    cube_sx = diameter * DT * 2 + inside
    cube_ty = diameter * DT + inside
    cube_sy = 2 * diameter * DT + inside / 2
    circle_radius = diameter * DT / 2
    c1x = -diameter * DT - inside
    c2x = diameter * DT + inside
    c2y = 3 * circle_radius   # + inside / 2
    c1y = circle_radius

    bpy.ops.curve.simple(align='WORLD', location=(0, cube_ty, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=cube_sx, Simple_length=cube_sy, use_cyclic_u=True, edit_mode=False)
    bpy.context.active_object.name = "_tmprect"


    bpy.ops.curve.simple(align='WORLD', location=(c2x, c2y, 0), rotation=(0, 0, 0), Simple_Type='Ellipse', Simple_a=circle_radius,
                         Simple_b=circle_radius + inside, Simple_sides=4, use_cyclic_u=True, edit_mode=False)

    bpy.context.active_object.name = "_tmpcirc_add"
    bpy.context.object.data.resolution_u = RESOLUTION

    bpy.ops.curve.simple(align='WORLD', location=(-c2x, c2y, 0), rotation=(0, 0, 0), Simple_Type='Ellipse', Simple_a=circle_radius,
                         Simple_b=circle_radius + inside, Simple_sides=4, use_cyclic_u=True, edit_mode=False)

    bpy.context.active_object.name = "_tmpcirc_add"
    bpy.context.object.data.resolution_u = RESOLUTION
    simple.joinMultiple('_tmpcirc')
    simple.selectMultiple('_tmp')
    bpy.ops.object.curve_boolean(boolean_type='UNION')
    bpy.context.active_object.name = "sum"
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.context.object.scale[0] = inside * 3 + 1
    bpy.context.object.scale[1] = inside * 3 + 1
    simple.removeMultiple('_tmp')
    simple.makeActive('sum')
    bpy.context.active_object.name = "_sum"

#    bpy.ops.curve.primitive_bezier_circle_add(radius=circle_radius, enter_editmode=False, align='WORLD',
#                                              location=(c1x, circle_radius, 0))
    rc1 = circle_radius - inside
    bpy.ops.curve.simple(align='WORLD', location=(c1x, c1y, 0), rotation=(0, 0, 0), Simple_Type='Ellipse', Simple_a=circle_radius,
                         Simple_b=rc1, Simple_sides=4, use_cyclic_u=True, edit_mode=False)

    bpy.context.active_object.name = "_circ_delete"
    bpy.context.object.data.resolution_u = RESOLUTION

    bpy.ops.curve.simple(align='WORLD', location=(-c1x, c1y, 0), rotation=(0, 0, 0), Simple_Type='Ellipse', Simple_a=circle_radius,
                         Simple_b=rc1, Simple_sides=4, use_cyclic_u=True, edit_mode=False)
    bpy.context.active_object.name = "_circ_delete"
    bpy.context.object.data.resolution_u = RESOLUTION

    simple.selectMultiple("_")  # select everything starting with _

    bpy.context.view_layer.objects.active = bpy.data.objects['_sum']  # Make the plate base active
    bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
    bpy.context.active_object.name = "PUZZLE"
    simple.removeMultiple("_")  # Remove temporary base and holes
    simple.makeActive("PUZZLE")
    bpy.context.active_object.name = "_puzzle"

def fingers(diameter, inside, amount):
    DT = 1.025
    translate = -4 * (amount - 1) * diameter * DT/2
    for i in range(amount):
        print('i 1:', i)
        finger(diameter, 0, DT=DT)
        bpy.ops.transform.translate(value=(i * 4 * diameter * DT, 0, 0.0))
        bpy.context.active_object.name = "puzzle"

    simple.selectMultiple('puzzle')
    bpy.ops.object.curve_boolean(boolean_type='UNION')
    bpy.context.active_object.name = "fingers"
    simple.removeMultiple("puzzle")
    simple.makeActive('fingers')
    bpy.ops.object.curve_remove_doubles()
    bpy.ops.transform.translate(value=(translate, -0.00002, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')


    #  receptacle is smaller by the inside tolerance amount
    for i in range(amount):
        print('i 2:', i)
        finger(diameter, inside, DT=DT)
        bpy.ops.transform.translate(value=(i * 4 * diameter * DT, 0, 0.0))
        bpy.context.active_object.name = "puzzle"
    simple.selectMultiple('puzzle')
    bpy.ops.object.curve_boolean(boolean_type='UNION')
    bpy.context.active_object.name = "receptacle"
    simple.removeMultiple("puzzle")
    simple.makeActive('receptacle')
    bpy.ops.transform.translate(value=(translate, -inside * 1.05, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.curve_remove_doubles()


def bar(width, thick, diameter, tolerance, amount=0):
    if amount == 0:
        amount = round(thick / (5 * diameter * 1.025))
    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=width, Simple_length=thick, use_cyclic_u=True, edit_mode=False)
    bpy.context.active_object.name = "tmprect"

    if amount < 2:
        finger(diameter, tolerance, DT=1.025)
        simple.rename('_puzzle', 'receptacle')
        bpy.ops.transform.translate(value=(0, -tolerance, 0.0))
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        finger(diameter, 0, DT=1.025)
        simple.rename('_puzzle', '_tmpfingers')
    else:
        fingers(diameter, tolerance, amount)
        simple.rename('fingers', '_tmpfingers')

    rotate(-math.pi/2)
    bpy.ops.transform.translate(value=(width/2, 0, 0.0))
    simple.rename('tmprect', '_tmprect')
    simple.selectMultiple('_tmp')
    bpy.ops.object.curve_boolean(boolean_type='UNION')
    bpy.context.active_object.name = "base"
    simple.removeMultiple('_tmp')
    simple.rename('base', '_tmpbase')

    simple.rename('receptacle', '_tmpreceptacle')
    rotate(-math.pi/2)
    bpy.ops.transform.translate(value=(-width/2, 0, 0.0))
    simple.selectMultiple("_tmp")


    simple.selectMultiple("_")  # select everything starting with plate_

    bpy.context.view_layer.objects.active = bpy.data.objects['_tmpbase']  # Make the plate base active
    bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
    bpy.context.active_object.name = "PUZZLE_bar"
    simple.removeMultiple("_")  # Remove temporary base and holes




