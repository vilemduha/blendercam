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

# blender operators definitions are in this file. They mostly call the functions from curvecamcreate.py
from typing import Any

import bpy
from bpy.props import *
from bpy.types import Operator

from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, parametric, joinery
import shapely
from shapely.geometry import Point, LineString, Polygon
import mathutils
import math

DT = 1.025


def finger(diameter, stem=2):
    # diameter = diameter of the tool for joint creation
    # DT = Bit diameter tolerance
    # stem = amount of radius the stem or neck of the joint will have
    global DT
    RESOLUTION = 12  # Data resolution
    cube_sx = diameter * DT * (2 + stem - 1)
    cube_ty = diameter * DT
    cube_sy = 2 * diameter * DT
    circle_radius = diameter * DT / 2
    c1x = cube_sx / 2
    c2x = cube_sx / 2
    c2y = 3 * circle_radius
    c1y = circle_radius

    bpy.ops.curve.simple(align='WORLD', location=(0, cube_ty, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=cube_sx, Simple_length=cube_sy, use_cyclic_u=True, edit_mode=False)
    bpy.context.active_object.name = "ftmprect"

    bpy.ops.curve.simple(align='WORLD', location=(c2x, c2y, 0), rotation=(0, 0, 0), Simple_Type='Ellipse',
                         Simple_a=circle_radius,
                         Simple_b=circle_radius, Simple_sides=4, use_cyclic_u=True, edit_mode=False, shape='3D')

    bpy.context.active_object.name = "ftmpcirc_add"
    bpy.context.object.data.resolution_u = RESOLUTION

    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    simple.duplicate()
    simple.mirrorx()

    simple.union('ftmp')
    simple.rename('ftmp', '_sum')

    rc1 = circle_radius

    bpy.ops.curve.simple(align='WORLD', location=(c1x, c1y, 0), rotation=(0, 0, 0), Simple_Type='Ellipse',
                         Simple_a=circle_radius, Simple_b=rc1, Simple_sides=4, use_cyclic_u=True, edit_mode=False,
                         shape='3D')

    bpy.context.active_object.name = "_circ_delete"
    bpy.context.object.data.resolution_u = RESOLUTION
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    simple.duplicate()
    simple.mirrorx()
    simple.union('_circ')

    simple.difference('_', '_sum')
    bpy.ops.object.curve_remove_doubles()
    simple.rename('_sum', "_puzzle")


def fingers(diameter, inside, amount, stem=1):
    # diameter = diameter of the tool for joint creation
    # inside = Tolerance in the joint receptacle
    global DT   # Bit diameter tolerance
    # stem = amount of radius the stem or neck of the joint will have
    # amount = the amount of fingers

    xtranslate = -(4 + 2 * (stem - 1)) * (amount - 1) * diameter * DT / 2
    finger(diameter, stem=stem)  # generate male finger
    simple.activeName("puzzlem")
    simple.move(x=xtranslate, y=-0.00002)

    if amount > 1:
        # duplicate translate the amount needed (faster than generating new)
        for i in range(amount - 1):
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                          TRANSFORM_OT_translate={
                                              "value": ((4 + 2 * (stem - 1)) * diameter * DT, 0, 0.0)})
        simple.union('puzzle')

    simple.activeName("fingers")
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    # Receptacle is made using the silhouette offset from the fingers
    if inside > 0:
        bpy.ops.object.silhouete_offset(offset=inside, style='1')
        simple.activeName('receptacle')
        simple.move(y=-inside)


def twistf(name, length, diameter, tolerance, twist, tneck, tthick):
    # add twist lock to receptacle
    if twist:
        joinery.interlock_twist(length, tthick, tolerance, cx=0, cy=0, rotation=0, percentage=tneck)
        simple.rotate(math.pi/2)
        simple.move(y=-tthick/2+2*diameter+2*tolerance)
        simple.activeName('xtemptwist')
        simple.makeActive(name)
        simple.activeName('xtemp')
        simple.union('xtemp')
        simple.activeName(name)


def twistm(name, length, diameter, tolerance, twist, tneck, tthick, angle, x=0, y=0):
    # add twist lock to male connector
    global DT
    if twist:
        joinery.interlock_twist(length, tthick, tolerance, cx=0, cy=0, rotation=0, percentage=tneck)
        simple.rotate(math.pi/2)
        simple.move(y=-tthick/2+2*diameter*DT)
        simple.rotate(angle)
        simple.move(x=x, y=y)
        simple.activeName('_twist')
        simple.makeActive(name)
        simple.activeName('_tmp')
        simple.difference('_', '_tmp')
        simple.activeName(name)


def bar(width, thick, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, which='MF'):
    # width = length of the bar
    # thick = thickness of the bar
    # diameter = diameter of the tool for joint creation
    # tolerance = Tolerance in the joint
    # amount = amount of fingers in the joint 0 means auto generate
    # stem = amount of radius the stem or neck of the joint will have
    # twist = twist lock addition
    # tneck = percentage the twist neck will have compared to thick
    # tthick = thicknest of the twist material
    # Which M,F, MF, MM, FF

    global DT
    if amount == 0:
        amount = round(thick / ((4 + 2 * (stem - 1)) * diameter * DT)) - 1
    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=width, Simple_length=thick, use_cyclic_u=True, edit_mode=False)
    simple.activeName('tmprect')

    fingers(diameter, tolerance, amount, stem=stem)

    if which == 'MM' or which == 'M' or which == 'MF':
        simple.rename('fingers', '_tmpfingers')
        simple.rotate(-math.pi / 2)
        simple.move(x=width/2)
        simple.rename('tmprect', '_tmprect')
        simple.union('_tmp')
        simple.activeName("tmprect")
        twistm('tmprect', thick, diameter, tolerance, twist, tneck, tthick, -math.pi/2, x=width/2)

    twistf('receptacle', thick, diameter, tolerance, twist, tneck, tthick)
    simple.rename('receptacle', '_tmpreceptacle')
    if which == 'FF' or which == 'F' or which == 'MF':
        simple.rotate(-math.pi / 2)
        simple.move(x=-width / 2)
        simple.rename('tmprect', '_tmprect')
        simple.difference('_tmp', '_tmprect')
        simple.activeName("tmprect")

    simple.removeMultiple("_")  # Remove temporary base and holes
    simple.removeMultiple("fingers")  # Remove temporary base and holes
    simple.rename('tmprect', 'Puzzle_bar')
    simple.removeMultiple("tmp")  # Remove temporary base and holes
    simple.makeActive('Puzzle_bar')


def arc(radius, thick, angle, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, which='MF'):
    # radius = radius of the curve
    # thick = thickness of the bar
    # angle = angle of the arc
    # diameter = diameter of the tool for joint creation
    # tolerance = Tolerance in the joint
    # amount = amount of fingers in the joint 0 means auto generate
    # stem = amount of radius the stem or neck of the joint will have
    # twist = twist lock addition
    # tneck = percentage the twist neck will have compared to thick
    # tthick = thicknest of the twist material
    # which = which joint to generate, Male Female MaleFemale M, F, MF

    global DT  # diameter tolerance for diameter of finger creation

    if angle == 0:  # angle cannot be 0
        angle = 0.01

    negative = False
    if angle < 0:  # if angle < 0 then negative is true
        angle = -angle
        negative = True

    if amount == 0:
        amount = round(thick / ((4 + 2 * (stem - 1)) * diameter * DT)) - 1

    fingers(diameter, tolerance, amount, stem=stem)
    twistf('receptacle', thick, diameter, tolerance, twist, tneck, tthick)

    # generate arc
    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Segment',
                         Simple_a=radius - thick / 2,
                         Simple_b=radius + thick / 2, Simple_startangle=-0.0001, Simple_endangle=math.degrees(angle),
                         Simple_radius=radius, use_cyclic_u=False, edit_mode=False)
    bpy.context.active_object.name = "tmparc"

    simple.rename('fingers', '_tmpfingers')

    simple.rotate(math.pi)
    simple.move(x=radius)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    simple.rename('tmparc', '_tmparc')
    if which == 'MF' or which == 'M':
        simple.union('_tmp')
        simple.activeName("base")
        twistm('base', thick, diameter, tolerance, twist, tneck, tthick, math.pi, x=radius)
        simple.rename('base', '_tmparc')

    simple.rename('receptacle', '_tmpreceptacle')
    simple.mirrory()
    simple.move(x=radius)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    simple.rotate(angle)
    simple.makeActive('_tmparc')

    if which == 'MF' or which == 'F':
        simple.difference('_tmp', '_tmparc')
    bpy.context.active_object.name = "PUZZLE_arc"
    bpy.ops.object.curve_remove_doubles()
    simple.removeMultiple("_")  # Remove temporary base and holes
    simple.makeActive('PUZZLE_arc')
    if which == 'M':
        simple.rotate(-angle)
        simple.mirrory()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        simple.rotate(-math.pi / 2)
        simple.move(y=radius)
        simple.rename('PUZZLE_arc', 'PUZZLE_arc_male')
    elif which == 'F':
        simple.mirrorx()
        simple.move(x=radius)
        simple.rotate(math.pi / 2)
        simple.rename('PUZZLE_arc', 'PUZZLE_arc_receptacle')
    else:
        simple.move(x=-radius)
    # bpy.ops.object.transform_apply(location=True, rotation=False, scale=False, properties=False)
    #
    if negative:  # mirror if angle is negative
        simple.mirrory()
    #
    # bpy.ops.object.curve_remove_doubles()


def arcbararc(length, radius, thick, angle, angleb, diameter, tolerance, amount=0, stem=1, twist=False,
              tneck=0.5, tthick=0.01, which='MF'):
    # length is the total width of the segments including 2 * radius and thick
    # radius = radius of the curve
    # thick = thickness of the bar
    # angle = angle of the female part
    # angleb = angle of the male part
    # diameter = diameter of the tool for joint creation
    # tolerance = Tolerance in the joint
    # amount = amount of fingers in the joint 0 means auto generate
    # stem = amount of radius the stem or neck of the joint will have
    # twist = twist lock addition
    # tneck = percentage the twist neck will have compared to thick
    # tthick = thicknest of the twist material
    # which = which joint to generate, Male Female MaleFemale M, F, MF

    length -= (radius * 2 + thick)  # adjust length to include 2x radius + thick

    # generate base rectangle
    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=length * 1.005, Simple_length=thick, use_cyclic_u=True, edit_mode=False)
    simple.activeName("tmprect")

    #  Generate male section and join to the base
    if which == 'M' or which == 'MF':
        arc(radius, thick, angleb, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck,
            tthick=tthick, which='M')
        simple.move(x=length / 2)
        simple.activeName('tmp_male')
        simple.selectMultiple('tmp')
        bpy.ops.object.curve_boolean(boolean_type='UNION')
        simple.activeName('male')
        simple.removeMultiple('tmp')
        simple.rename('male', 'tmprect')

    # Generate female section and join to base
    if which == 'F' or which == 'MF':
        arc(radius, thick, angle, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck,
            tthick=tthick, which='F')
        simple.move(x=-length / 2)
        simple.activeName('tmp_receptacle')
        simple.union('tmp')

    simple.activeName('arcBarArc')
    simple.makeActive('arcBarArc')


def arcbar(length, radius, thick, angle, diameter, tolerance, amount=0, stem=1, twist=False,
           tneck=0.5, tthick=0.01, which='MF'):
    # length is the total width of the segments including 2 * radius and thick
    # radius = radius of the curve
    # thick = thickness of the bar
    # angle = angle of the female part
    # diameter = diameter of the tool for joint creation
    # tolerance = Tolerance in the joint
    # amount = amount of fingers in the joint 0 means auto generate
    # stem = amount of radius the stem or neck of the joint will have
    # twist = twist lock addition
    # tneck = percentage the twist neck will have compared to thick
    # tthick = thicknest of the twist material
    # which = which joint to generate, Male Female MaleFemale M, F, MF
    if which == 'M':
        which = 'MM'
    elif which == 'F':
        which = 'FF'
    length -= (radius * 2 + thick)  # adjust length to include 2x radius + thick

    # generate base rectangle
    #  Generate male section and join to the base
    if which == 'MM' or which == 'MF':
        bar(length, thick, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck, tthick=tthick,
            which='M')
        simple.activeName('tmprect')

    if which == 'FF' or which == 'FM':
        bar(length, thick, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck, tthick=tthick,
            which='F')
        simple.rotate(math.pi)
        simple.activeName('tmprect')

    # Generate female section and join to base
    if which == 'FF' or which == 'MF':
        arc(radius, thick, angle, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck,
            tthick=tthick, which='F')
        simple.move(x=-length / 2 * 0.998)
        simple.activeName('tmp_receptacle')
        simple.union('tmp')
        simple.activeName('arcBar')
        simple.removeMultiple('tmp')

    if which == 'MM':
        arc(radius, thick, angle, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck,
            tthick=tthick, which='M')
        bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                 orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
        simple.move(x=-length / 2 * 0.998)
        simple.activeName('tmp_receptacle')
        simple.union('tmp')
        simple.activeName('arcBar')
        simple.removeMultiple('tmp')

    simple.makeActive('arcBar')


def multiangle(radius, thick, angle, diameter, tolerance, amount=0, stem=1, twist=False,
               tneck=0.5, tthick=0.01, combination='MFF'):
    # length is the total width of the segments including 2 * radius and thick
    # radius = radius of the curve
    # thick = thickness of the bar
    # angle = angle of the female part
    # diameter = diameter of the tool for joint creation
    # tolerance = Tolerance in the joint
    # amount = amount of fingers in the joint 0 means auto generate
    # stem = amount of radius the stem or neck of the joint will have
    # twist = twist lock addition
    # tneck = percentage the twist neck will have compared to thick
    # tthick = thicknest of the twist material
    # which = which joint to generate, Male Female MaleFemale M, F, MF
    rectxsize = (radius - thick / 2)
    rexterior = radius + thick/2
    rinterior = radius-thick/2

    height = math.sqrt(rexterior * rexterior - radius * radius)

    bpy.ops.curve.simple(align='WORLD', location=(0, height, 0),
                         rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=rectxsize, Simple_length=rectxsize/2, use_cyclic_u=True,
                         edit_mode=False, shape='3D')
    simple.move(y=rectxsize/4)
    simple.activeName('tmp_rect')

    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Circle', Simple_sides=4,
                         Simple_radius=rinterior, shape='3D', use_cyclic_u=True, edit_mode=False)
    simple.move(y=radius * math.tan(angle))
    simple.activeName('tmpcircle')

    arc(radius, thick, angle, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck, tthick=tthick,
        which='MF')
    simple.activeName('tmp_arc')
    simple.duplicate()
    simple.mirrorx()
    simple.union("tmp_")
    simple.difference('tmp', 'tmp_')
    simple.activeName('multiangle60')


def t(length, thick, diameter, tolerance, amount=0, stem=1, twist=False, tneck=0.5, tthick=0.01, combination='MF',
      base_gender='M', corner=False):
    if corner:
        if combination == 'MF':
            base_gender = 'M'
            combination = 'f'
        elif combination == 'F':
            base_gender = 'F'
            combination = 'f'
        elif combination == 'M':
            base_gender = 'M'
            combination = 'm'

    bar(length, thick, diameter, tolerance, amount=amount, stem=stem, twist=twist, tneck=tneck,
        tthick=tthick, which=base_gender)
    simple.activeName('tmp')
    fingers(diameter, tolerance, amount=amount, stem=stem)
    if combination == 'MF' or combination == 'M' or combination == 'm':
        simple.makeActive('fingers')
        simple.move(y=thick / 2)
        simple.duplicate()
        simple.activeName('tmp')
        simple.union('tmp')

    if combination == 'M':
        simple.makeActive('fingers')
        simple.mirrory()
        simple.activeName('tmp')
        simple.union('tmp')

    if combination == 'MF' or combination == 'F' or combination == 'f':
        simple.makeActive('receptacle')
        simple.move(y=-thick / 2)
        simple.duplicate()
        simple.activeName('tmp')
        simple.difference('tmp', 'tmp')

    if combination == 'F':
        simple.makeActive('receptacle')
        simple.mirrory()
        simple.activeName('tmp')
        simple.difference('tmp', 'tmp')

    simple.removeMultiple('receptacle')
    simple.removeMultiple('fingers')

    simple.rename('tmp', 't')
    simple.makeActive('t')


def mitre(length, thick, angle, angleb, diameter, tolerance, amount=0, stem=1, twist=False,
          tneck=0.5, tthick=0.01, which='MF'):
    # length is the total width of the segments including 2 * radius and thick
    # radius = radius of the curve
    # thick = thickness of the bar
    # angle = angle of the female part
    # angleb = angle of the male part
    # diameter = diameter of the tool for joint creation
    # tolerance = Tolerance in the joint
    # amount = amount of fingers in the joint 0 means auto generate
    # stem = amount of radius the stem or neck of the joint will have
    # twist = twist lock addition
    # tneck = percentage the twist neck will have compared to thick
    # tthick = thicknest of the twist material
    # which = which joint to generate, Male Female MaleFemale M, F, MF

    # generate base rectangle
    bpy.ops.curve.simple(align='WORLD', location=(0, -thick / 2, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=length * 1.005 + 4 * thick, Simple_length=thick, use_cyclic_u=True,
                         edit_mode=False,
                         shape='3D')
    simple.activeName("tmprect")

    # generate cutout shapes
    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=4 * thick, Simple_length=6 * thick, use_cyclic_u=True, edit_mode=False,
                         shape='3D')
    simple.move(x=2 * thick)
    simple.rotate(angle)
    simple.move(x=length / 2)
    simple.activeName('tmpmitreright')

    bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple_Type='Rectangle',
                         Simple_width=4 * thick, Simple_length=6 * thick, use_cyclic_u=True, edit_mode=False,
                         shape='3D')
    simple.move(x=2 * thick)
    simple.rotate(angleb)
    simple.move(x=length / 2)
    simple.mirrorx()
    simple.activeName('tmpmitreleft')
    simple.difference('tmp', 'tmprect')
    simple.makeActive('tmprect')

    fingers(diameter, tolerance, amount, stem=stem)

    #  Generate male section and join to the base
    if which == 'M' or which == 'MF':
        simple.makeActive('fingers')
        simple.duplicate()
        simple.activeName('tmpfingers')
        simple.rotate(angle - math.pi / 2)
        h = thick / math.cos(angle)
        h /= 2
        simple.move(x=length / 2 + h * math.sin(angle), y=-thick / 2)
        if which == 'M':
            simple.rename('fingers', 'tmpfingers')
            simple.rotate(angleb - math.pi / 2)
            h = thick / math.cos(angleb)
            h /= 2
            simple.move(x=length / 2 + h * math.sin(angleb), y=-thick / 2)
            simple.mirrorx()

        simple.union('tmp')
        simple.activeName('tmprect')

    # Generate female section and join to base
    if which == 'MF' or which == 'F':
        simple.makeActive('receptacle')
        simple.mirrory()
        simple.duplicate()
        simple.activeName('tmpreceptacle')
        simple.rotate(angleb - math.pi / 2)
        h = thick / math.cos(angleb)
        h /= 2
        simple.move(x=length / 2 + h * math.sin(angleb), y=-thick / 2)
        simple.mirrorx()
        if which == 'F':
            simple.rename('receptacle', 'tmpreceptacle2')
            simple.rotate(angle - math.pi / 2)
            h = thick / math.cos(angle)
            h /= 2
            simple.move(x=length / 2 + h * math.sin(angle), y=-thick / 2)
        simple.difference('tmp', 'tmprect')

    simple.removeMultiple('receptacle')
    simple.removeMultiple('fingers')
    simple.rename('tmprect', 'mitre')
