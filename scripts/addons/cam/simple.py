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

import math, sys, os, string
import time
import bpy
import mathutils
from mathutils import *
from math import *


def tuple_add(t, t1):  # add two tuples as Vectors
    return (t[0] + t1[0], t[1] + t1[1], t[2] + t1[2])


def tuple_sub(t, t1):  # sub two tuples as Vectors
    return (t[0] - t1[0], t[1] - t1[1], t[2] - t1[2])


def tuple_mul(t, c):  # multiply two tuples with a number
    return (t[0] * c, t[1] * c, t[2] * c)


def tuple_length(t):  # get length of vector, but passed in as tuple.
    return (Vector(t).length)


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
    '''function for reporting during the script, works for background operations in the header.'''
    # for i in range(n+1):
    # sys.stdout.flush()
    text = str(text)
    if n == None:
        n = ''
    else:
        n = ' ' + str(int(n * 1000) / 1000) + '%'
    # d=int(n/2)
    spaces = ' ' * (len(text) + 55)
    sys.stdout.write('progress{%s%s}\n' % (text, n))
    sys.stdout.flush()


# bpy.data.window_managers['WinMan'].progress_update(n)
# if bpy.context.scene.o
# bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
# time.sleep(0.5)

#
def activate(o):
    '''makes an object active, used many times in blender'''
    s = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(state=True)
    s.objects[o.name].select_set(state=True)
    bpy.context.view_layer.objects.active = o


def dist2d(v1, v2):
    '''distance between two points in 2d'''
    return math.sqrt((v1[0] - v2[0]) * (v1[0] - v2[0]) + (v1[1] - v2[1]) * (v1[1] - v2[1]))


def delob(ob):
    '''object deletion for multiple uses'''
    activate(ob)
    bpy.ops.object.delete(use_global=False)


def dupliob(o, pos):
    '''helper function for visualising cutter positions in bullet simulation'''
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
    if bpy.data.groups.get(groupname) == None:
        bpy.ops.group.create(name=groupname)
    else:
        bpy.ops.object.group_link(group=groupname)


def compare(v1, v2, vmiddle, e):
    '''comparison for optimisation of paths'''
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
    '''test path segment on verticality threshold, for protect_vertical option'''
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

    iname = fn[:-l] + 'temp_cam' + os.sep + bn + '_' + o.name
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
