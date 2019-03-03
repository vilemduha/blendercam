# blender CAM pack.py (c) 2012 Vilem Novak
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

import bpy
from cam import utils, simple, polygon_utils_cam
import shapely
from shapely import geometry as sgeometry
from shapely import affinity, prepared
from shapely import speedups
import random, time
import mathutils
from mathutils import Vector


# this algorithm takes all selected curves,
# converts them to polygons,
# offsets them by the pre-set margin
# then chooses a starting location possibly inside the allready occupied area and moves and rotates the polygon out of the occupied area
# if one or more positions are found where the poly doesn't overlap, it is placed and added to the occupied area - allpoly
# this algorithm is very slow and STUPID, a collision algorithm would be much much faster...
def translate(s, x, y):
    ncoords = []
    for p in s.exterior.coords:
        ncoords.append((p[0] + x, p[1] + y))

    return sgeometry.Polygon(ncoords)


def srotate(s, r, x, y):
    ncoords = []
    e = mathutils.Euler((0, 0, r))
    for p in s.exterior.coords:
        v1 = Vector((p[0], p[1], 0))
        v2 = Vector((x, y, 0))
        v = v1 - v2
        v.rotate(e)
        ncoords.append((v[0], v[1]))

    return sgeometry.Polygon(ncoords)


def packCurves():
    if speedups.available:
        speedups.enable()
    t = time.time()
    packsettings = bpy.context.scene.cam_pack

    sheetsizex = packsettings.sheet_x
    sheetsizey = packsettings.sheet_y
    direction = packsettings.sheet_fill_direction
    distance = packsettings.distance
    rotate = packsettings.rotate

    polyfield = []  # in this, position, rotation, and actual poly will be stored.
    for ob in bpy.context.selected_objects:
        allchunks = []
        simple.activate(ob)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        z = ob.location.z
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()

        chunks = utils.curveToChunks(ob)
        npolys = utils.chunksToShapely(chunks)
        # add all polys in silh to one poly
        poly = shapely.ops.unary_union(npolys)

        poly = poly.buffer(distance / 1.5, 8)
        poly = poly.simplify(0.0003)
        polyfield.append([[0, 0], 0.0, poly, ob, z])
    random.shuffle(polyfield)
    # primitive layout here:
    allpoly = prepared.prep(sgeometry.Polygon())  # main collision poly.
    # allpoly=sgeometry.Polygon()#main collision poly.

    shift = 0.0015  # one milimeter by now.
    rotchange = .3123456  # in radians

    xmin, ymin, xmax, ymax = polyfield[0][2].bounds
    if direction == 'X':
        mindist = -xmin
    else:
        mindist = -ymin
    i = 0
    p = polyfield[0][2]
    placedpolys = []
    rotcenter = sgeometry.Point(0, 0)
    for pf in polyfield:
        print(i)
        rot = 0
        porig = pf[2]
        placed = False
        xmin, ymin, xmax, ymax = p.bounds
        # p.shift(-xmin,-ymin)
        if direction == 'X':
            x = mindist
            y = -ymin
        if direction == 'Y':
            x = -xmin
            y = mindist

        iter = 0
        best = None
        hits = 0
        besthit = None
        while not placed:

            # swap x and y, and add to x
            # print(x,y)
            p = porig

            if rotate:
                # ptrans=srotate(p,rot,0,0)
                ptrans = affinity.rotate(p, rot, origin=rotcenter, use_radians=True)
                # ptrans = translate(ptrans,x,y)
                ptrans = affinity.translate(ptrans, x, y)
            else:
                # ptrans = translate(p,x,y)
                ptrans = affinity.translate(p, x, y)
            xmin, ymin, xmax, ymax = ptrans.bounds
            # print(iter,p.bounds)

            if xmin > 0 and ymin > 0 and (
                    (direction == 'Y' and xmax < sheetsizex) or (direction == 'X' and ymax < sheetsizey)):
                if not allpoly.intersects(ptrans):
                    # if allpoly.disjoint(ptrans):
                    # print('gothit')
                    # we do more good solutions, choose best out of them:
                    hits += 1
                    if best == None:
                        best = [x, y, rot, xmax, ymax]
                        besthit = hits
                    if direction == 'X':
                        if xmax < best[3]:
                            best = [x, y, rot, xmax, ymax]
                            besthit = hits
                    elif ymax < best[4]:
                        best = [x, y, rot, xmax, ymax]
                        besthit = hits

            if hits >= 15 or (
                    iter > 10000 and hits > 0):  # here was originally more, but 90% of best solutions are still 1
                placed = True
                pf[3].location.x = best[0]
                pf[3].location.y = best[1]
                pf[3].location.z = pf[4]
                pf[3].rotation_euler.z = best[2]

                pf[3].select_set(state=True)

                # print(mindist)
                mindist = mindist - 0.5 * (xmax - xmin)
                # print(mindist)
                # print(iter)

                # reset polygon to best position here:
                ptrans = affinity.rotate(porig, best[2], rotcenter, use_radians=True)
                # ptrans=srotate(porig,best[2],0,0)
                ptrans = affinity.translate(ptrans, best[0], best[1])
                # ptrans = translate(ptrans,best[0],best[1])

                # polygon_utils_cam.polyToMesh(p,0.1)#debug visualisation
                keep = []
                print(best[0], best[1])
                # print(len(ptrans.exterior))
                # npoly=allpoly.union(ptrans)
                '''
                for ci in range(0,len(allpoly)):
                    cminx,cmaxx,cminy,cmaxy=allpoly.boundingBox(ci)
                    if direction=='X' and cmaxx>mindist-.1:
                            npoly.addContour(allpoly[ci])
                    if direction=='Y' and cmaxy>mindist-.1:
                            npoly.addContour(allpoly[ci])
                '''
                # allpoly=npoly
                placedpolys.append(ptrans)
                allpoly = prepared.prep(sgeometry.MultiPolygon(placedpolys))
                # *** temporary fix until prepared geometry code is setup properly
                # allpoly=sgeometry.MultiPolygon(placedpolys)

                # polygon_utils_cam.polyToMesh(allpoly,0.1)#debug visualisation

                # for c in p:
                #	allpoly.addContour(c)
                # cleanup allpoly
                print(iter, hits, besthit)
            if not placed:
                if direction == 'Y':
                    x += shift
                    mindist = y
                    if xmax + shift > sheetsizex:
                        x = x - xmin
                        y += shift
                if direction == 'X':
                    y += shift
                    mindist = x
                    if ymax + shift > sheetsizey:
                        y = y - ymin
                        x += shift
                if rotate: rot += rotchange
            iter += 1
        i += 1
    t = time.time() - t

    polygon_utils_cam.shapelyToCurve('test', sgeometry.MultiPolygon(placedpolys), 0)
    print(t)
