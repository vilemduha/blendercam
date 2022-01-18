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
# here is the bridges functionality of Blender CAM. The functions here are called with operators defined from ops.py.

import bpy
from bpy.props import *

from cam import utils
import mathutils
import math

from shapely import ops as sops
from shapely import geometry as sgeometry
from shapely import affinity, prepared


def addBridge(x, y, rot, sizex, sizey):
    bpy.ops.mesh.primitive_plane_add(size=sizey*2, calc_uvs=True, enter_editmode=False, align='WORLD',
                                     location=(0, 0, 0), rotation=(0, 0, 0))
    b = bpy.context.active_object
    b.name = 'bridge'
    # b.show_name=True
    b.dimensions.x = sizex
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.object.editmode_toggle()
    bpy.ops.transform.translate(value=(0, sizey / 2, 0), constraint_axis=(False, True, False),
                                orient_type='GLOBAL', mirror=False, use_proportional_edit=False,
                                proportional_edit_falloff='SMOOTH', proportional_size=1)
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.convert(target='CURVE')

    b.location = x, y, 0
    b.rotation_euler.z = rot
    return b


def addAutoBridges(o):
    """attempt to add auto bridges as set of curves"""
    utils.getOperationSources(o)
    bridgecollectionname = o.bridges_collection_name
    if bridgecollectionname == '' or bpy.data.collections.get(bridgecollectionname) is None:
        bridgecollectionname = 'bridges_' + o.name
        bpy.data.collections.new(bridgecollectionname)
        bpy.context.collection.children.link(bpy.data.collections[bridgecollectionname])
    g = bpy.data.collections[bridgecollectionname]
    o.bridges_collection_name = bridgecollectionname
    for ob in o.objects:

        if ob.type == 'CURVE' or ob.type == 'TEXT':
            curve = utils.curveToShapely(ob)
        if ob.type == 'MESH':
            curve = utils.getObjectSilhouete('OBJECTS', [ob])
        for c in curve:
            c = c.exterior
            minx, miny, maxx, maxy = c.bounds
            d1 = c.project(sgeometry.Point(maxx + 1000, (maxy + miny) / 2.0))
            p = c.interpolate(d1)
            bo = addBridge(p.x, p.y, -math.pi / 2, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)
            d1 = c.project(sgeometry.Point(minx - 1000, (maxy + miny) / 2.0))
            p = c.interpolate(d1)
            bo = addBridge(p.x, p.y, math.pi / 2, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)
            d1 = c.project(sgeometry.Point((minx + maxx) / 2.0, maxy + 1000))
            p = c.interpolate(d1)
            bo = addBridge(p.x, p.y, 0, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)
            d1 = c.project(sgeometry.Point((minx + maxx) / 2.0, miny - 1000))
            p = c.interpolate(d1)
            bo = addBridge(p.x, p.y, math.pi, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)


def getBridgesPoly(o):
    if not hasattr(o, 'bridgespolyorig'):
        bridgecollectionname = o.bridges_collection_name
        bridgecollection = bpy.data.collections[bridgecollectionname]
        shapes = []
        bpy.ops.object.select_all(action='DESELECT')

        for ob in bridgecollection.objects:
            if ob.type == 'CURVE':
                ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.duplicate()
        bpy.ops.object.join()
        ob = bpy.context.active_object
        shapes.extend(utils.curveToShapely(ob, o.use_bridge_modifiers))
        ob.select_set(state=True)
        bpy.ops.object.delete(use_global=False)
        bridgespoly = sops.unary_union(shapes)

        # buffer the poly, so the bridges are not actually milled...
        o.bridgespolyorig = bridgespoly.buffer(distance=o.cutter_diameter / 2.0)
        o.bridgespoly_boundary = o.bridgespolyorig.boundary
        o.bridgespoly_boundary_prep = prepared.prep(o.bridgespolyorig.boundary)
        o.bridgespoly = prepared.prep(o.bridgespolyorig)


def useBridges(ch, o):
    """this adds bridges to chunks, takes the bridge-objects collection and uses the curves inside it as bridges."""
    bridgecollectionname = o.bridges_collection_name
    bridgecollection = bpy.data.collections[bridgecollectionname]
    if len(bridgecollection.objects) > 0:

        # get bridgepoly
        getBridgesPoly(o)

        ####

        bridgeheight = min(o.max.z, o.min.z + abs(o.bridges_height))

        vi = 0
        # shapelyToCurve('test',bridgespoly,0)
        newpoints = []
        p1 = sgeometry.Point(ch.points[0])
        startinside = o.bridgespoly.contains(p1)
        interrupted = False
        while vi < len(ch.points):
            i1 = vi
            i2 = vi
            chp1 = ch.points[i1]
            chp2 = ch.points[i1]  # Vector(v1)#this is for case of last point and not closed chunk..
            if vi + 1 < len(ch.points):
                i2 = vi + 1
                chp2 = ch.points[vi + 1]  # Vector(ch.points[vi+1])
            v1 = mathutils.Vector(chp1)
            v2 = mathutils.Vector(chp2)
            if v1.z < bridgeheight or v2.z < bridgeheight:
                v = v2 - v1
                # dist+=v.length
                p2 = sgeometry.Point(chp2)

                if interrupted:
                    p1 = sgeometry.Point(chp1)
                    startinside = o.bridgespoly.contains(p1)
                    interrupted = False

                endinside = o.bridgespoly.contains(p2)
                l = sgeometry.LineString([chp1, chp2])
                # print(dir(bridgespoly_boundary))
                if o.bridgespoly_boundary_prep.intersects(l):
                    # print('intersects')
                    intersections = o.bridgespoly_boundary.intersection(l)
                else:
                    intersections = sgeometry.GeometryCollection()

                itpoint = intersections.type == 'Point'
                itmpoint = intersections.type == 'MultiPoint'

                # print(startinside, endinside,intersections, intersections.type)
                # print(l,bridgespoly)
                if not startinside:
                    # print('nothing found')
                    newpoints.append(chp1)
                elif startinside:
                    newpoints.append((chp1[0], chp1[1], max(chp1[2], bridgeheight)))
                cpoints = []
                if itpoint:
                    cpoints = [mathutils.Vector((intersections.x, intersections.y, intersections.z))]
                elif itmpoint:
                    cpoints = []
                    for p in intersections:
                        cpoints.append(mathutils.Vector((p.x, p.y, p.z)))
                # ####sort collisions here :(
                ncpoints = []
                while len(cpoints) > 0:
                    mind = 10000000
                    mini = -1
                    for i, p in enumerate(cpoints):
                        if min(mind, (p - v1).length) < mind:
                            mini = i
                            mind = (p - v1).length
                    ncpoints.append(cpoints.pop(mini))
                cpoints = ncpoints
                # endsorting

                if startinside:
                    isinside = True
                else:
                    isinside = False
                for cp in cpoints:
                    v3 = cp
                    # print(v3)
                    if v.length == 0:
                        ratio = 1
                    else:
                        fractvect = v3 - v1
                        ratio = fractvect.length / v.length

                    collisionz = v1.z + v.z * ratio
                    np1 = (v3.x, v3.y, collisionz)
                    np2 = (v3.x, v3.y, max(collisionz, bridgeheight))
                    if not isinside:
                        newpoints.extend((np1, np2))
                    else:
                        newpoints.extend((np2, np1))
                    isinside = not isinside

                startinside = endinside
                vi += 1
            else:
                newpoints.append(chp1)
                vi += 1
                interrupted = True
        ch.points = newpoints
