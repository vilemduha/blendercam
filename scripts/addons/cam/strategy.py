# blender CAM strategy.py (c) 2012 Vilem Novak
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

# here is the strategy functionality of Blender CAM. The functions here are called with operators defined in ops.py.

import bpy
from bpy.props import *
import time
import math
from math import *
from bpy_extras import object_utils
from cam import chunk
from cam.chunk import *
from cam import collision
from cam.collision import *
from cam import simple
from cam.simple import *
from cam import pattern
from cam.pattern import *
from cam import utils, bridges, ops
from cam.utils import *
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
from cam import image_utils
from cam.image_utils import *

from shapely.geometry import polygon as spolygon
from shapely import geometry as sgeometry
from shapely import affinity

SHAPELY = True


# cutout strategy is completely here:
def cutout(o):
    max_depth = checkminz(o)
    cutter_angle = math.radians(o.cutter_tip_angle / 2)
    c_offset = o.cutter_diameter / 2  # cutter ofset
    print("cuttertype:", o.cutter_type, "max_depth:", max_depth)
    if o.cutter_type == 'VCARVE':
        c_offset = -max_depth * math.tan(cutter_angle)
    elif o.cutter_type == 'CYLCONE':
        c_offset = -max_depth * math.tan(cutter_angle) + o.cylcone_diameter / 2
    elif o.cutter_type == 'BALLCONE':
        c_offset = -max_depth * math.tan(cutter_angle) + o.ball_radius
    elif o.cutter_type == 'BALLNOSE':
        r = o.cutter_diameter / 2
        print("cutter radius:", r)
        if -max_depth < r:
            c_offset = math.sqrt(r ** 2 - (r + max_depth) ** 2)
            print("offset:", c_offset)
    if c_offset > o.cutter_diameter / 2:
        c_offset = o.cutter_diameter / 2
    if o.straight:
        join = 2
    else:
        join = 1
    print('operation: cutout')
    offset = True
    if o.cut_type == 'ONLINE' and o.onlycurves:  # is separate to allow open curves :)
        print('separate')
        chunksFromCurve = []
        for ob in o.objects:
            chunksFromCurve.extend(curveToChunks(ob, o.use_modifiers))
        for ch in chunksFromCurve:
            # print(ch.points)

            if len(ch.points) > 2:
                ch.poly = chunkToShapely(ch)

    # p.addContour(ch.poly)
    else:
        chunksFromCurve = []
        if o.cut_type == 'ONLINE':
            p = utils.getObjectOutline(0, o, True)

        else:
            offset = True
            if o.cut_type == 'INSIDE':
                offset = False

            p = utils.getObjectOutline(c_offset, o, offset)
            if o.outlines_count > 1:
                for i in range(1, o.outlines_count):
                    chunksFromCurve.extend(shapelyToChunks(p, -1))
                    p = p.buffer(distance=o.dist_between_paths * offset, resolution=o.circle_detail, join_style=join,
                                 mitre_limit=2)

        chunksFromCurve.extend(shapelyToChunks(p, -1))
        if o.outlines_count > 1 and o.movement_insideout == 'OUTSIDEIN':
            chunksFromCurve.reverse()

    # parentChildPoly(chunksFromCurve,chunksFromCurve,o)
    chunksFromCurve = limitChunks(chunksFromCurve, o)
    if not o.dont_merge:
        parentChildPoly(chunksFromCurve, chunksFromCurve, o)
    if o.outlines_count == 1:
        chunksFromCurve = utils.sortChunks(chunksFromCurve, o)

    if (o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CCW') or (
            o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CW'):
        for ch in chunksFromCurve:
            ch.points.reverse()

    if o.cut_type == 'INSIDE':  # there would bee too many conditions above,
        # so for now it gets reversed once again when inside cutting.
        for ch in chunksFromCurve:
            ch.points.reverse()

    layers = getLayers(o, o.maxz, checkminz(o))
    extendorder = []

    if o.first_down:  # each shape gets either cut all the way to bottom,
        # or every shape gets cut 1 layer, then all again. has to create copies,
        # because same chunks are worked with on more layers usually
        for chunk in chunksFromCurve:
            dir_switch = False  # needed to avoid unnecessary lifting of cutter with open chunks
            # and movement set to "MEANDER"
            for layer in layers:
                chunk_copy = chunk.copy()
                if dir_switch:
                    chunk_copy.points.reverse()
                extendorder.append([chunk_copy, layer])
                if (not chunk.closed) and o.movement_type == "MEANDER":
                    dir_switch = not dir_switch
    else:
        for layer in layers:
            for chunk in chunksFromCurve:
                extendorder.append([chunk.copy(), layer])

    for chl in extendorder:  # Set Z for all chunks
        chunk = chl[0]
        layer = chl[1]
        print(layer[1])
        chunk.setZ(layer[1])

    chunks = []

    if o.use_bridges:  # add bridges to chunks
        print('using bridges')
        simple.remove_multiple(o.name+'_cut_bridges')
        print("old briddge cut removed")

        bridgeheight = min(o.max.z, o.min.z + abs(o.bridges_height))

        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]
            if layer[1] < bridgeheight:
                bridges.useBridges(chunk, o)

    if o.profile_start > 0:
        print("cutout change profile start")
        for chl in extendorder:
            chunk = chl[0]
            if chunk.closed:
                chunk.changePathStart(o)

    # Lead in
    if o.lead_in > 0.0 or o.lead_out > 0:
        print("cutout leadin")
        for chl in extendorder:
            chunk = chl[0]
            if chunk.closed:
                chunk.breakPathForLeadinLeadout(o)
                chunk.leadContour(o)

    if o.ramp:  # add ramps or simply add chunks
        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]
            if chunk.closed:
                chunk.rampContour(layer[0], layer[1], o)
                chunks.append(chunk)
            else:
                chunk.rampZigZag(layer[0], layer[1], o)
                chunks.append(chunk)
    else:
        for chl in extendorder:
            chunks.append(chl[0])

    chunksToMesh(chunks, o)


def curve(o):
    print('operation: curve')
    pathSamples = []
    utils.getOperationSources(o)
    if not o.onlycurves:
        o.warnings += 'at least one of assigned objects is not a curve\n'

    for ob in o.objects:
        pathSamples.extend(curveToChunks(ob))  # make the chunks from curve here
    pathSamples = utils.sortChunks(pathSamples, o)  # sort before sampling
    pathSamples = chunksRefine(pathSamples, o)  # simplify

    # layers here
    if o.use_layers:
        layers = getLayers(o, o.maxz, round(checkminz(o), 6))
        # layers is a list of lists [[0.00,l1],[l1,l2],[l2,l3]] containg the start and end of each layer
        extendorder = []
        chunks = []
        for layer in layers:
            for ch in pathSamples:
                extendorder.append([ch.copy(), layer])  # include layer information to chunk list

        for chl in extendorder:  # Set offset Z for all chunks according to the layer information,
            chunk = chl[0]
            layer = chl[1]
            print('layer: ' + str(layer[1]))
            chunk.offsetZ(o.maxz * 2 - o.minz + layer[1])
            chunk.clampZ(o.minz)  # safety to not cut lower than minz
            chunk.clampmaxZ(o.free_movement_height)  # safety, not higher than free movement height

        for chl in extendorder:  # strip layer information from extendorder and transfer them to chunks
            chunks.append(chl[0])

        chunksToMesh(chunks, o)  # finish by converting to mesh

    else:  # no layers, old curve
        for ch in pathSamples:
            ch.clampZ(o.minz)  # safety to not cut lower than minz
            ch.clampmaxZ(o.free_movement_height)  # safety, not higher than free movement height
        chunksToMesh(pathSamples, o)


def proj_curve(s, o):
    print('operation: projected curve')
    pathSamples = []
    chunks = []
    ob = bpy.data.objects[o.curve_object]
    pathSamples.extend(curveToChunks(ob))

    targetCurve = s.objects[o.curve_object1]

    from cam import chunk
    if targetCurve.type != 'CURVE':
        o.warnings = o.warnings + 'Projection target and source have to be curve objects!\n '
        return

    if 1:
        extend_up = 0.1
        extend_down = 0.04
        tsamples = curveToChunks(targetCurve)
        for chi, ch in enumerate(pathSamples):
            cht = tsamples[chi].points
            ch.depth = 0
            for i, s in enumerate(ch.points):
                # move the points a bit
                ep = Vector(cht[i])
                sp = Vector(ch.points[i])
                # extend startpoint
                vecs = sp - ep
                vecs.normalize()
                vecs *= extend_up
                sp += vecs
                ch.startpoints.append(sp)

                # extend endpoint
                vece = sp - ep
                vece.normalize()
                vece *= extend_down
                ep -= vece
                ch.endpoints.append(ep)

                ch.rotations.append((0, 0, 0))

                vec = sp - ep
                ch.depth = min(ch.depth, -vec.length)
                ch.points[i] = sp.copy()

    layers = getLayers(o, 0, ch.depth)

    chunks.extend(utils.sampleChunksNAxis(o, pathSamples, layers))
    chunksToMesh(chunks, o)


def pocket(o):
    print('operation: pocket')
    scene = bpy.context.scene

    simple.remove_multiple("3D_poc")

    max_depth = checkminz(o)
    cutter_angle = math.radians(o.cutter_tip_angle / 2)
    c_offset = o.cutter_diameter / 2
    if o.cutter_type == 'VCARVE':
        c_offset = -max_depth * math.tan(cutter_angle)
    elif o.cutter_type == 'CYLCONE':
        c_offset = -max_depth * math.tan(cutter_angle) + o.cylcone_diameter / 2
    elif o.cutter_type == 'BALLCONE':
        c_offset = -max_depth * math.tan(cutter_angle) + o.ball_radius
    if c_offset > o.cutter_diameter / 2:
        c_offset = o.cutter_diameter / 2

    p = utils.getObjectOutline(c_offset, o, False)
    approxn = (min(o.max.x - o.min.x, o.max.y - o.min.y) / o.dist_between_paths) / 2
    print("approximative:" + str(approxn))
    print(o)

    i = 0
    chunks = []
    chunksFromCurve = []
    lastchunks = []
    centers = None
    firstoutline = p  # for testing in the end.
    prest = p.buffer(-c_offset, o.circle_detail)
    while not p.is_empty:
        if o.pocketToCurve:
            polygon_utils_cam.shapelyToCurve('3dpocket', p, 0.0)  # make a curve starting with _3dpocket

        nchunks = shapelyToChunks(p, o.min.z)
        # print("nchunks")
        pnew = p.buffer(-o.dist_between_paths, o.circle_detail)
        if pnew.is_empty:
            
            pt = p.buffer(-c_offset, o.circle_detail)     # test if the last curve will leave material
            if not pt.is_empty:
                pnew = pt
        # print("pnew")

        nchunks = limitChunks(nchunks, o)
        chunksFromCurve.extend(nchunks)
        parentChildDist(lastchunks, nchunks, o)
        lastchunks = nchunks

        percent = int(i / approxn * 100)
        progress('outlining polygons ', percent)
        p = pnew

        i += 1

    # if (o.poc)#TODO inside outside!
    if (o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CW') or (
            o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CCW'):
        for ch in chunksFromCurve:
            ch.points.reverse()

    chunksFromCurve = utils.sortChunks(chunksFromCurve, o)

    chunks = []
    layers = getLayers(o, o.maxz, checkminz(o))

    for l in layers:
        lchunks = setChunksZ(chunksFromCurve, l[1])
        if o.ramp:
            for ch in lchunks:
                ch.zstart = l[0]
                ch.zend = l[1]

        # helix_enter first try here TODO: check if helix radius is not out of operation area.
        if o.helix_enter:
            helix_radius = c_offset * o.helix_diameter * 0.01  # 90 percent of cutter radius
            helix_circumference = helix_radius * pi * 2

            revheight = helix_circumference * tan(o.ramp_in_angle)
            for chi, ch in enumerate(lchunks):
                if not chunksFromCurve[chi].children:
                    p = ch.points[0]  # TODO:intercept closest next point when it should stay low
                    # first thing to do is to check if helix enter can really enter.
                    checkc = Circle(helix_radius + c_offset, o.circle_detail)
                    checkc = affinity.translate(checkc, p[0], p[1])
                    covers = False
                    for poly in o.silhouete:
                        if poly.contains(checkc):
                            covers = True
                            break

                    if covers:
                        revolutions = (l[0] - p[2]) / revheight
                        # print(revolutions)
                        h = Helix(helix_radius, o.circle_detail, l[0], p, revolutions)
                        # invert helix if not the typical direction
                        if (o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CW') or (
                                o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CCW'):
                            nhelix = []
                            for v in h:
                                nhelix.append((2 * p[0] - v[0], v[1], v[2]))
                            h = nhelix
                        ch.points = h + ch.points
                    else:
                        o.warnings = o.warnings + 'Helix entry did not fit! \n '
                        ch.closed = True
                        ch.rampZigZag(l[0], l[1], o)
        # Arc retract here first try:
        if o.retract_tangential:  # TODO: check for entry and exit point before actual computing... will be much better.
            # TODO: fix this for CW and CCW!
            for chi, ch in enumerate(lchunks):
                # print(chunksFromCurve[chi])
                # print(chunksFromCurve[chi].parents)
                if chunksFromCurve[chi].parents == [] or len(chunksFromCurve[chi].parents) == 1:

                    revolutions = 0.25
                    v1 = Vector(ch.points[-1])
                    i = -2
                    v2 = Vector(ch.points[i])
                    v = v1 - v2
                    while v.length == 0:
                        i = i - 1
                        v2 = Vector(ch.points[i])
                        v = v1 - v2

                    v.normalize()
                    rotangle = Vector((v.x, v.y)).angle_signed(Vector((1, 0)))
                    e = Euler((0, 0, pi / 2.0))  # TODO:#CW CLIMB!
                    v.rotate(e)
                    p = v1 + v * o.retract_radius
                    center = p
                    p = (p.x, p.y, p.z)

                    # progress(str((v1,v,p)))
                    h = Helix(o.retract_radius, o.circle_detail, p[2] + o.retract_height, p, revolutions)

                    e = Euler((0, 0, rotangle + pi))  # angle to rotate whole retract move
                    rothelix = []
                    c = []  # polygon for outlining and checking collisions.
                    for p in h:  # rotate helix to go from tangent of vector
                        v1 = Vector(p)

                        v = v1 - center
                        v.x = -v.x  # flip it here first...
                        v.rotate(e)
                        p = center + v
                        rothelix.append(p)
                        c.append((p[0], p[1]))

                    c = sgeometry.Polygon(c)
                    # print('çoutline')
                    # print(c)
                    coutline = c.buffer(c_offset, o.circle_detail)
                    # print(h)
                    # print('çoutline')
                    # print(coutline)
                    # polyToMesh(coutline,0)
                    rothelix.reverse()

                    covers = False
                    for poly in o.silhouete:
                        if poly.contains(coutline):
                            covers = True
                            break

                    if covers:
                        ch.points.extend(rothelix)

        chunks.extend(lchunks)

    if o.ramp:
        for ch in chunks:
            ch.rampZigZag(ch.zstart, ch.points[0][2], o)

    if o.first_down:
        chunks = utils.sortChunks(chunks, o)

    if o.pocketToCurve:  # make curve instead of a path
        simple.join_multiple("3dpocket")

    else:
        chunksToMesh(chunks, o)  # make normal pocket path


def drill(o):
    print('operation: Drill')
    chunks = []
    for ob in o.objects:
        activate(ob)

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                      TRANSFORM_OT_translate={"value": (0, 0, 0),
                                                              "constraint_axis": (False, False, False),
                                                              "orient_type": 'GLOBAL', "mirror": False,
                                                              "use_proportional_edit": False,
                                                              "proportional_edit_falloff": 'SMOOTH',
                                                              "proportional_size": 1, "snap": False,
                                                              "snap_target": 'CLOSEST', "snap_point": (0, 0, 0),
                                                              "snap_align": False, "snap_normal": (0, 0, 0),
                                                              "texture_space": False, "release_confirm": False})
        # bpy.ops.collection.objects_remove_all()
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        ob = bpy.context.active_object
        if ob.type == 'CURVE':
            ob.data.dimensions = '3D'
        try:
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        except:
            pass
        l = ob.location

        if ob.type == 'CURVE':

            for c in ob.data.splines:
                maxx, minx, maxy, miny, maxz, minz = -10000, 10000, -10000, 10000, -10000, 10000
                for p in c.points:
                    if o.drill_type == 'ALL_POINTS':
                        chunks.append(camPathChunk([(p.co.x + l.x, p.co.y + l.y, p.co.z + l.z)]))
                    minx = min(p.co.x, minx)
                    maxx = max(p.co.x, maxx)
                    miny = min(p.co.y, miny)
                    maxy = max(p.co.y, maxy)
                    minz = min(p.co.z, minz)
                    maxz = max(p.co.z, maxz)
                for p in c.bezier_points:
                    if o.drill_type == 'ALL_POINTS':
                        chunks.append(camPathChunk([(p.co.x + l.x, p.co.y + l.y, p.co.z + l.z)]))
                    minx = min(p.co.x, minx)
                    maxx = max(p.co.x, maxx)
                    miny = min(p.co.y, miny)
                    maxy = max(p.co.y, maxy)
                    minz = min(p.co.z, minz)
                    maxz = max(p.co.z, maxz)
                cx = (maxx + minx) / 2
                cy = (maxy + miny) / 2
                cz = (maxz + minz) / 2

                center = (cx, cy)
                aspect = (maxx - minx) / (maxy - miny)
                if (1.3 > aspect > 0.7 and o.drill_type == 'MIDDLE_SYMETRIC') or o.drill_type == 'MIDDLE_ALL':
                    chunks.append(camPathChunk([(center[0] + l.x, center[1] + l.y, cz + l.z)]))

        elif ob.type == 'MESH':
            for v in ob.data.vertices:
                chunks.append(camPathChunk([(v.co.x + l.x, v.co.y + l.y, v.co.z + l.z)]))
        delob(ob)  # delete temporary object with applied transforms

    layers = getLayers(o, o.maxz, checkminz(o))

    chunklayers = []
    for layer in layers:
        for chunk in chunks:
            # If using object for minz then use z from points in object
            if o.minz_from_ob:
                z = chunk.points[0][2]
            else:  # using operation minz
                z = o.minz
            # only add a chunk layer if the chunk z point is in or lower than the layer
            if z <= layer[0]:
                if z <= layer[1]:
                    z = layer[1]
                # perform peck drill
                newchunk = chunk.copy()
                newchunk.setZ(z)
                chunklayers.append(newchunk)
                # retract tool to maxz (operation depth start in ui)
                newchunk = chunk.copy()
                newchunk.setZ(o.maxz)
                chunklayers.append(newchunk)

    chunklayers = utils.sortChunks(chunklayers, o)
    chunksToMesh(chunklayers, o)


def medial_axis(o):
    print('operation: Medial Axis')

    simple.remove_multiple("medialMesh")

    from cam.voronoi import Site, computeVoronoiDiagram

    chunks = []

    gpoly = spolygon.Polygon()
    angle = o.cutter_tip_angle
    slope = math.tan(math.pi * (90 - angle / 2) / 180)  # angle in degrees
    # slope = math.tan((math.pi-angle)/2) #angle in radian
    new_cutter_diameter = o.cutter_diameter
    m_o_ob = o.object_source
    if o.cutter_type == 'VCARVE':
        angle = o.cutter_tip_angle
        # start the max depth calc from the "start depth" of the operation.
        maxdepth = o.maxz - slope * o.cutter_diameter / 2
        # don't cut any deeper than the "end depth" of the operation.
        if maxdepth < o.minz:
            maxdepth = o.minz
            # the effective cutter diameter can be reduced from it's max
            # since we will be cutting shallower than the original maxdepth
            # without this, the curve is calculated as if the diameter was at the original maxdepth and we get the bit
            # pulling away from the desired cut surface
            new_cutter_diameter = (maxdepth - o.maxz) / (- slope) * 2
    elif o.cutter_type == 'BALLNOSE':
        maxdepth = - new_cutter_diameter / 2
    else:
        o.warnings += 'Only Ballnose, Ball and V-carve cutters\n are supported'
        return
    # remember resolutions of curves, to refine them,
    # otherwise medial axis computation yields too many branches in curved parts
    resolutions_before = []

    for ob in o.objects:
        if ob.type == 'CURVE' or ob.type == 'FONT':
            resolutions_before.append(ob.data.resolution_u)
            if ob.data.resolution_u < 64:
                ob.data.resolution_u = 64

    polys = utils.getOperationSilhouete(o)
    mpoly = sgeometry.shape(polys)
    mpoly_boundary = mpoly.boundary
    ipol = 0
    for poly in polys.geoms:
        ipol = ipol + 1
        print("polygon:", ipol)
        schunks = shapelyToChunks(poly, -1)
        schunks = chunksRefineThreshold(schunks, o.medial_axis_subdivision,
                                        o.medial_axis_threshold)  # chunksRefine(schunks,o)

        verts = []
        for ch in schunks:
            for pt in ch.points:
                # pvoro = Site(pt[0], pt[1])
                verts.append(pt)  # (pt[0], pt[1]), pt[2])
        # verts= points#[[vert.x, vert.y, vert.z] for vert in vertsPts]
        nDupli, nZcolinear = unique(verts)
        nVerts = len(verts)
        print(str(nDupli) + " duplicates points ignored")
        print(str(nZcolinear) + " z colinear points excluded")
        if nVerts < 3:
            print("Not enough points")
            return {'FINISHED'}
        # Check colinear
        xValues = [pt[0] for pt in verts]
        yValues = [pt[1] for pt in verts]
        if checkEqual(xValues) or checkEqual(yValues):
            print("Points are colinear")
            return {'FINISHED'}
        # Create diagram
        print("Tesselation... (" + str(nVerts) + " points)")
        xbuff, ybuff = 5, 5  # %
        zPosition = 0
        vertsPts = [Point(vert[0], vert[1], vert[2]) for vert in verts]
        # vertsPts= [Point(vert[0], vert[1]) for vert in verts]

        pts, edgesIdx = computeVoronoiDiagram(vertsPts, xbuff, ybuff, polygonsOutput=False, formatOutput=True)

        # pts=[[pt[0], pt[1], zPosition] for pt in pts]
        newIdx = 0
        vertr = []
        filteredPts = []
        print('filter points')
        ipts = 0
        for p in pts:
            ipts = ipts + 1
            if ipts % 500 == 0:
                sys.stdout.write('\r')
                # the exact output you're looking for:
                prog_message = "points: " + str(ipts) + " / " + str(len(pts)) + " " + str(
                    round(100 * ipts / len(pts))) + "%"
                sys.stdout.write(prog_message)
                sys.stdout.flush()

            if not poly.contains(sgeometry.Point(p)):
                vertr.append((True, -1))
            else:
                vertr.append((False, newIdx))
                if o.cutter_type == 'VCARVE':
                    # start the z depth calc from the "start depth" of the operation.
                    z = o.maxz - mpoly.boundary.distance(sgeometry.Point(p)) * slope
                    if z < maxdepth:
                        z = maxdepth
                elif o.cutter_type == 'BALL' or o.cutter_type == 'BALLNOSE':
                    d = mpoly_boundary.distance(sgeometry.Point(p))
                    r = new_cutter_diameter / 2.0
                    if d >= r:
                        z = -r
                    else:
                        # print(r, d)
                        z = -r + sqrt(r * r - d * d)
                else:
                    z = 0  #
                # print(mpoly.distance(sgeometry.Point(0,0)))
                # if(z!=0):print(z)
                filteredPts.append((p[0], p[1], z))
                newIdx += 1

        print('filter edges')
        filteredEdgs = []
        ledges = []
        for e in edgesIdx:
            do = True
            # p1 = pts[e[0]]
            # p2 = pts[e[1]]
            # print(p1,p2,len(vertr))
            if vertr[e[0]][0]:  # exclude edges with allready excluded points
                do = False
            elif vertr[e[1]][0]:
                do = False
            if do:
                filteredEdgs.append((vertr[e[0]][1], vertr[e[1]][1]))
                ledges.append(sgeometry.LineString((filteredPts[vertr[e[0]][1]], filteredPts[vertr[e[1]][1]])))
        # print(ledges[-1].has_z)

        bufpoly = poly.buffer(-new_cutter_diameter / 2, resolution=64)

        lines = shapely.ops.linemerge(ledges)
        # print(lines.type)

        if bufpoly.type == 'Polygon' or bufpoly.type == 'MultiPolygon':
            lines = lines.difference(bufpoly)
            chunks.extend(shapelyToChunks(bufpoly, maxdepth))
        chunks.extend(shapelyToChunks(lines, 0))

        # generate a mesh from the medial calculations
        if o.add_mesh_for_medial:
            polygon_utils_cam.shapelyToCurve('medialMesh', lines, 0.0)
            bpy.ops.object.convert(target='MESH')

    oi = 0
    for ob in o.objects:
        if ob.type == 'CURVE' or ob.type == 'FONT':
            ob.data.resolution_u = resolutions_before[oi]
            oi += 1

    # bpy.ops.object.join()
    chunks = utils.sortChunks(chunks, o)

    layers = getLayers(o, o.maxz, o.min.z)

    chunklayers = []

    for layer in layers:
        for chunk in chunks:
            if chunk.isbelowZ(layer[0]):
                newchunk = chunk.copy()
                newchunk.clampZ(layer[1])
                chunklayers.append(newchunk)

    if o.first_down:
        chunklayers = utils.sortChunks(chunklayers, o)

    if o.add_mesh_for_medial:  # make curve instead of a path
        simple.join_multiple("medialMesh")

    chunksToMesh(chunklayers, o)
    # add pocket operation for medial if add pocket checked
    if o.add_pocket_for_medial:
        #        o.add_pocket_for_medial = False
        # export medial axis parameter to pocket op
        ops.Add_Pocket(None, maxdepth, m_o_ob, new_cutter_diameter)


def getLayers(operation, startdepth, enddepth):
    """returns a list of layers bounded by startdepth and enddepth
       uses operation.stepdown to determine number of layers.
    """
    if operation.use_layers:
        layers = []
        n = math.ceil((startdepth - enddepth) / operation.stepdown)
        print("start " + str(startdepth) + " end " + str(enddepth) + " n " + str(n))

        layerstart = operation.maxz
        for x in range(0, n):
            layerend = round(max(startdepth - ((x + 1) * operation.stepdown), enddepth), 6)
            if int(layerstart * 10 ** 8) != int(layerend * 10 ** 8):
                # it was possible that with precise same end of operation,
                # last layer was done 2x on exactly same level...
                layers.append([layerstart, layerend])
            layerstart = layerend
    else:
        layers = [[round(startdepth, 6), round(enddepth, 6)]]

    return layers


def chunksToMesh(chunks, o):
    """convert sampled chunks to path, optimization of paths"""
    t = time.time()
    s = bpy.context.scene
    m = s.cam_machine
    verts = []

    free_movement_height = o.free_movement_height  # o.max.z +

    if o.machine_axes == '3':
        if m.use_position_definitions:
            origin = (m.starting_position.x, m.starting_position.y, m.starting_position.z)  # dhull
        else:
            origin = (0, 0, free_movement_height)

        verts = [origin]
    if o.machine_axes != '3':
        verts_rotations = []  # (0,0,0)
    if (o.machine_axes == '5' and o.strategy5axis == 'INDEXED') or (
            o.machine_axes == '4' and o.strategy4axis == 'INDEXED'):
        extendChunks5axis(chunks, o)

    if o.array:
        nchunks = []
        for x in range(0, o.array_x_count):
            for y in range(0, o.array_y_count):
                print(x, y)
                for ch in chunks:
                    ch = ch.copy()
                    ch.shift(x * o.array_x_distance, y * o.array_y_distance, 0)
                    nchunks.append(ch)
        chunks = nchunks

    progress('building paths from chunks')
    e = 0.0001
    lifted = True

    for chi in range(0, len(chunks)):

        # print(chi)

        ch = chunks[chi]
        # print(chunks)
        # print (ch)
        if len(ch.points) > 0:  # TODO: there is a case where parallel+layers+zigzag ramps send empty chunks here...
            # print(len(ch.points))
            nverts = []
            if o.optimize:
                ch = optimizeChunk(ch, o)

            # lift and drop

            if lifted:  # did the cutter lift before? if yes, put a new position above of the first point of next chunk.
                if o.machine_axes == '3' or (o.machine_axes == '5' and o.strategy5axis == 'INDEXED') or (
                        o.machine_axes == '4' and o.strategy4axis == 'INDEXED'):
                    v = (ch.points[0][0], ch.points[0][1], free_movement_height)
                else:  # otherwise, continue with the next chunk without lifting/dropping
                    v = ch.startpoints[0]  # startpoints=retract points
                    verts_rotations.append(ch.rotations[0])
                verts.append(v)

            # add whole chunk
            verts.extend(ch.points)

            # add rotations for n-axis
            if o.machine_axes != '3':
                verts_rotations.extend(ch.rotations)

            lift = True
            # check if lifting should happen
            if chi < len(chunks) - 1 and len(chunks[chi + 1].points) > 0:
                # TODO: remake this for n axis, and this check should be somewhere else...
                last = Vector(ch.points[-1])
                first = Vector(chunks[chi + 1].points[0])
                vect = first - last
                if (o.machine_axes == '3' and (o.strategy == 'PARALLEL' or o.strategy == 'CROSS')
                    and vect.z == 0 and vect.length < o.dist_between_paths * 2.5) \
                        or (o.machine_axes == '4' and vect.length < o.dist_between_paths * 2.5):
                    # case of neighbouring paths
                    lift = False
                if abs(vect.x) < e and abs(vect.y) < e:  # case of stepdown by cutting.
                    lift = False

            if lift:
                if o.machine_axes == '3' or (o.machine_axes == '5' and o.strategy5axis == 'INDEXED') or (
                        o.machine_axes == '4' and o.strategy4axis == 'INDEXED'):
                    v = (ch.points[-1][0], ch.points[-1][1], free_movement_height)
                else:
                    v = ch.startpoints[-1]
                    verts_rotations.append(ch.rotations[-1])
                verts.append(v)
            lifted = lift
    # print(verts_rotations)
    if o.use_exact and not o.use_opencamlib:
        cleanupBulletCollision(o)
    print(time.time() - t)
    t = time.time()

    # actual blender object generation starts here:
    edges = []
    for a in range(0, len(verts) - 1):
        edges.append((a, a + 1))

    oname = "cam_path_{}".format(o.name)

    mesh = bpy.data.meshes.new(oname)
    mesh.name = oname
    mesh.from_pydata(verts, edges, [])

    if oname in s.objects:
        s.objects[oname].data = mesh
        ob = s.objects[oname]
    else:
        ob = object_utils.object_data_add(bpy.context, mesh, operator=None)

    if o.machine_axes != '3':
        # store rotations into shape keys, only way to store large arrays with correct floating point precision
        # - object/mesh attributes can only store array up to 32000 intems.

        ob.shape_key_add()
        ob.shape_key_add()
        shapek = mesh.shape_keys.key_blocks[1]
        shapek.name = 'rotations'
        print(len(shapek.data))
        print(len(verts_rotations))

        for i, co in enumerate(verts_rotations):  # TODO: optimize this. this is just rewritten too many times...
            shapek.data[i].co = co

    print(time.time() - t)

    ob.location = (0, 0, 0)
    o.path_object_name = oname

    # parent the path object to source object if object mode
    if (o.geometry_source == 'OBJECT') and o.parent_path_to_object:
        activate(o.objects[0])
        ob.select_set(state=True, view_layer=None)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    else:
        ob.select_set(state=True, view_layer=None)


def checkminz(o):
    if o.minz_from_material:
        return o.min.z
    else:
        return o.minz
