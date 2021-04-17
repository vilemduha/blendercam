# blender CAM utils.py (c) 2012 Vilem Novak
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

# here is the main functionality of Blender CAM. The functions here are called with operators defined in ops.py.

import bpy
from mathutils import *
from bpy.props import *
from cam import utils
import numpy as np

from cam import simple
from cam import image_utils



def createSimulationObject(name, operations, i):
    oname = 'csim_' + name

    o = operations[0]

    if oname in bpy.data.objects:
        ob = bpy.data.objects[oname]
    else:
        bpy.ops.mesh.primitive_plane_add(align='WORLD', enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
        ob = bpy.context.active_object
        ob.name = oname

        bpy.ops.object.modifier_add(type='SUBSURF')
        ss = ob.modifiers[-1]
        ss.subdivision_type = 'SIMPLE'
        ss.levels = 6
        ss.render_levels = 6
        bpy.ops.object.modifier_add(type='SUBSURF')
        ss = ob.modifiers[-1]
        ss.subdivision_type = 'SIMPLE'
        ss.levels = 4
        ss.render_levels = 3
        bpy.ops.object.modifier_add(type='DISPLACE')

    ob.location = ((o.max.x + o.min.x) / 2, (o.max.y + o.min.y) / 2, o.min.z)
    ob.scale.x = (o.max.x - o.min.x) / 2
    ob.scale.y = (o.max.y - o.min.y) / 2
    print(o.max.x, o.min.x)
    print(o.max.y, o.min.y)
    print('bounds')
    disp = ob.modifiers[-1]
    disp.direction = 'Z'
    disp.texture_coords = 'LOCAL'
    disp.mid_level = 0

    if oname in bpy.data.textures:
        t = bpy.data.textures[oname]

        t.type = 'IMAGE'
        disp.texture = t

        t.image = i
    else:
        bpy.ops.texture.new()
        for t in bpy.data.textures:
            if t.name == 'Texture':
                t.type = 'IMAGE'
                t.name = oname
                t = t.type_recast()
                t.type = 'IMAGE'
                t.image = i
                disp.texture = t
    ob.hide_render = True


def doSimulation(name, operations):
    """perform simulation of operations. Currently only for 3 axis"""
    for o in operations:
        utils.getOperationSources(o)
    limits = utils.getBoundsMultiple(
        operations)  # this is here because some background computed operations still didn't have bounds data
    i = image_utils.generateSimulationImage(operations, limits)
    cp = simple.getCachePath(operations[0])[:-len(operations[0].name)] + name
    iname = cp + '_sim.exr'

    image_utils.numpysave(i, iname)
    i = bpy.data.images.load(iname)
    createSimulationObject(name, operations, i)
