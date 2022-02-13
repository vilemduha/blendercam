# blender CAM simple.py (c) 2012 Vilem Novak
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

import math
import sys
import os
import string
import time
import bpy
import mathutils
from mathutils import *
from math import *
from shapely.geometry import Point, LineString, Polygon, MultiLineString


def tuple_add(t, t1):  # add two tuples as Vectors
    return t[0] + t1[0], t[1] + t1[1], t[2] + t1[2]


def tuple_sub(t, t1):  # sub two tuples as Vectors
    return t[0] - t1[0], t[1] - t1[1], t[2] - t1[2]


def tuple_mul(t, c):  # multiply two tuples with a number
    return t[0] * c, t[1] * c, t[2] * c


def tuple_length(t):  # get length of vector, but passed in as tuple.
    return Vector(t).length


# timing functions for optimisation purposes...
def timinginit():
    return [0, 0]


def timingstart(tinf):
    t = time.time()
    tinf[1] = t


def timingadd(tinf):
    t = time.time()
    tinf[0] += t - tinf[1]


def timingprint(tinf):
    print('time ' + str(tinf[0]) + 'seconds')


def progress(text, n=None):
    """function for reporting during the script, works for background operations in the header."""
    text = str(text)
    if n is None:
        n = ''
    else:
        n = ' ' + str(int(n * 1000) / 1000) + '%'
    sys.stdout.write('progress{%s%s}\n' % (text, n))
    sys.stdout.flush()


def activate(o):
    """makes an object active, used many times in blender"""
    s = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(state=True)
    s.objects[o.name].select_set(state=True)
    bpy.context.view_layer.objects.active = o


def dist2d(v1, v2):
    """distance between two points in 2d"""
    return math.hypot((v1[0] - v2[0]), (v1[1] - v2[1]))


def delob(ob):
    """object deletion for multiple uses"""
    activate(ob)
    bpy.ops.object.delete(use_global=False)


def dupliob(o, pos):
    """helper function for visualising cutter positions in bullet simulation"""
    activate(o)
    bpy.ops.object.duplicate()
    s = 1.0 / BULLET_SCALE
    bpy.ops.transform.resize(value=(s, s, s), constraint_axis=(False, False, False), orient_type='GLOBAL',
                             mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                             proportional_size=1)
    o = bpy.context.active_object
    bpy.ops.rigidbody.object_remove()
    o.location = pos


def addToGroup(ob, groupname):
    activate(ob)
    if bpy.data.groups.get(groupname) is None:
        bpy.ops.group.create(name=groupname)
    else:
        bpy.ops.object.group_link(group=groupname)


def compare(v1, v2, vmiddle, e):
    """comparison for optimisation of paths"""
    # e=0.0001
    v1 = Vector(v1)
    v2 = Vector(v2)
    vmiddle = Vector(vmiddle)
    vect1 = v2 - v1
    vect2 = vmiddle - v1
    vect1.normalize()
    vect1 *= vect2.length
    v = vect2 - vect1
    if v.length < e:
        return True
    return False


def isVerticalLimit(v1, v2, limit):
    """test path segment on verticality threshold, for protect_vertical option"""
    z = abs(v1[2] - v2[2])
    # verticality=0.05
    # this will be better.
    #
    # print(a)
    if z > 0:
        v2d = Vector((0, 0, -1))
        v3d = Vector((v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]))
        a = v3d.angle(v2d)
        if a > pi / 2:
            a = abs(a - pi)
        # print(a)
        if a < limit:
            # print(abs(v1[0]-v2[0])/z)
            # print(abs(v1[1]-v2[1])/z)
            if v1[2] > v2[2]:
                v1 = (v2[0], v2[1], v1[2])
                return v1, v2
            else:
                v2 = (v1[0], v1[1], v2[2])
                return v1, v2
    return v1, v2


def getCachePath(o):
    fn = bpy.data.filepath
    l = len(bpy.path.basename(fn))
    bn = bpy.path.basename(fn)[:-6]
    print('fn-l:', fn[:-l])
    print('bn:', bn)

    iname = fn[:-l] + 'temp_cam' + os.sep + bn + '_' + o.name
    return iname


def getSimulationPath():
    fn = bpy.data.filepath
    l = len(bpy.path.basename(fn))
    iname = fn[:-l] + 'temp_cam' + os.sep
    return iname


def safeFileName(name):  # for export gcode
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in name if c in valid_chars)
    return filename


def strInUnits(x, precision=5):
    if bpy.context.scene.unit_settings.system == 'METRIC':
        return str(round(x * 1000, precision)) + ' mm '
    elif bpy.context.scene.unit_settings.system == 'IMPERIAL':
        return str(round(x * 1000 / 25.4, precision)) + "'' "
    else:
        return str(x)


# select multiple object starting with name
def select_multiple(name):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    for ob in scene.objects:  # join pocket curve calculations
        if ob.name.startswith(name):
            ob.select_set(True)
        else:
            ob.select_set(False)


# join multiple objects starting with 'name' renaming final object as 'name'
def join_multiple(name):
    select_multiple(name)
    bpy.ops.object.join()
    bpy.context.active_object.name = name  # rename object


# remove multiple objects starting with 'name'.... useful for fixed name operation
def remove_multiple(name):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    for ob in scene.objects:
        if ob.name.startswith(name):
            ob.select_set(True)
            bpy.ops.object.delete()


def deselect():
    bpy.ops.object.select_all(action='DESELECT')


# makes the object with the name active
def make_active(name):
    ob = bpy.context.scene.objects[name]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


# change the name of the active object
def active_name(name):
    bpy.context.active_object.name = name


# renames and makes active name and makes it active
def rename(name, name2):
    make_active(name)
    bpy.context.active_object.name = name2


# boolean union of objects starting with name result is object name.
# all objects starting with name will be deleted and the result will be name
def union(name):
    select_multiple(name)
    bpy.ops.object.curve_boolean(boolean_type='UNION')
    active_name('unionboolean')
    remove_multiple(name)
    rename('unionboolean', name)

def intersect(name):
    select_multiple(name)
    bpy.ops.object.curve_boolean(boolean_type='INTERSECT')
    active_name('intersection')

# boolean difference of objects starting with name result is object from basename.
# all objects starting with name will be deleted and the result will be basename
def difference(name, basename):
    #   name is the series to select
    #   basename is what the base you want to cut including name
    select_multiple(name)
    bpy.context.view_layer.objects.active = bpy.data.objects[basename]
    bpy.ops.object.curve_boolean(boolean_type='DIFFERENCE')
    active_name('booleandifference')
    remove_multiple(name)
    rename('booleandifference', basename)


# duplicate active object or duplicate move
# if x or y not the default, duplicate move will be executed
def duplicate(x=0, y=0):
    if x == 0 and y == 0:
        bpy.ops.object.duplicate()
    else:
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                      TRANSFORM_OT_translate={"value": (x, y, 0.0)})


# Mirror active object along the x axis
def mirrorx():
    bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                             orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))


# mirror active object along y axis
def mirrory():
    bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                             orient_matrix_type='GLOBAL', constraint_axis=(False, True, False))


# move active object and apply translation
def move(x=0.0, y=0.0):
    bpy.ops.transform.translate(value=(x, y, 0.0))
    bpy.ops.object.transform_apply(location=True)


# Rotate active object and apply rotation
def rotate(angle):
    bpy.context.object.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(rotation=True)


# remove doubles
def remove_doubles():
    bpy.ops.object.curve_remove_doubles()


# Add overcut to active object
def add_overcut(diametre, overcut=True):
    if overcut:
        name = bpy.context.active_object.name
        bpy.ops.object.curve_overcuts(diameter=diametre, threshold=math.pi/2.05)
        overcut_name = bpy.context.active_object.name
        make_active(name)
        bpy.ops.object.delete()
        rename(overcut_name, name)
        remove_doubles()


# add bounding rectangtle to curve
def add_bound_rectangle(xmin, ymin, xmax, ymax, name='bounds_rectangle'):
    # xmin = minimum corner x value
    # ymin = minimum corner y value
    # xmax = maximum corner x value
    # ymax = maximum corner y value
    # name = name of the resulting object
    xsize = xmax - xmin
    ysize = ymax - ymin

    bpy.ops.curve.simple(align='WORLD', location=(xmin + xsize/2, ymin + ysize/2, 0), rotation=(0, 0, 0),
                         Simple_Type='Rectangle',
                         Simple_width=xsize, Simple_length=ysize, use_cyclic_u=True, edit_mode=False, shape='3D')
    bpy.ops.object.transform_apply(location=True)
    active_name(name)


def add_rectangle(width, height, center_x=True, center_y=True):
    x_offset = width / 2
    y_offset = height / 2

    if center_x:
        x_offset = 0
    if center_y:
        y_offset = 0

    bpy.ops.curve.simple(align='WORLD', location=(x_offset, y_offset, 0), rotation=(0, 0, 0),
                         Simple_Type='Rectangle',
                         Simple_width=width, Simple_length=height, use_cyclic_u=True, edit_mode=False, shape='3D')
    bpy.ops.object.transform_apply(location=True)
    active_name('simple_rectangle')


#  Returns coords from active object
def active_to_coords():
    bpy.ops.object.duplicate()
    obj = bpy.context.active_object
    bpy.ops.object.convert(target='MESH')
    active_name("_tmp_mesh")

    coords = []
    for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
        coords.append((v.co.x, v.co.y))
    remove_multiple('_tmp_mesh')
    return coords


# returns shapely polygon from active object
def active_to_shapely_poly():
    return Polygon(active_to_coords())  # convert coordinates to shapely Polygon datastructure
