"""Fabex 'chunk_utils.py' © 2012 Vilem Novak
"""

from math import (
    ceil,
    cos,
    hypot,
    pi,
    sin,
    sqrt,
    tan,
)

import numpy as np
from shapely.geometry import polygon as spolygon
from shapely import geometry as sgeometry
import sys
import time

import bpy
from mathutils import Vector

from .async_utils import progress_async
from .numba_utils import jit
from .simple_utils import (
    activate,
    progress,
    tuple_add,
    tuple_multiply,
    tuple_subtract,
    union,
)

from ..exception import CamException


def chunks_refine(chunks, o):
    """Add Extra Points in Between for Chunks"""
    for ch in chunks:
        # print('before',len(ch))
        newchunk = []
        v2 = Vector(ch.points[0])
        # print(ch.points)
        for s in ch.points:
            v1 = Vector(s)
            v = v1 - v2

            if v.length > o.distance_along_paths:
                d = v.length
                v.normalize()
                i = 0
                vref = Vector((0, 0, 0))

                while vref.length < d:
                    i += 1
                    vref = v * o.distance_along_paths * i
                    if vref.length < d:
                        p = v2 + vref

                        newchunk.append((p.x, p.y, p.z))

            newchunk.append(s)
            v2 = v1
        ch.points = np.array(newchunk)

    return chunks


def chunks_refine_threshold(chunks, distance, limitdistance):
    """Add Extra Points in Between for Chunks. for Medial Axis Strategy only!"""
    for ch in chunks:
        newchunk = []
        v2 = Vector(ch.points[0])

        for s in ch.points:
            v1 = Vector(s)
            v = v1 - v2

            if v.length > limitdistance:
                d = v.length
                v.normalize()
                i = 1
                vref = Vector((0, 0, 0))
                while vref.length < d / 2:
                    vref = v * distance * i
                    if vref.length < d:
                        p = v2 + vref

                        newchunk.append((p.x, p.y, p.z))
                    i += 1
                    # because of the condition, so it doesn't run again.
                    vref = v * distance * i
                while i > 0:
                    vref = v * distance * i
                    if vref.length < d:
                        p = v1 - vref

                        newchunk.append((p.x, p.y, p.z))
                    i -= 1

            newchunk.append(s)
            v2 = v1
        ch.points = np.array(newchunk)

    return chunks


def chunk_to_shapely(chunk):
    p = spolygon.Polygon(chunk.points)
    return p


def mesh_from_curve(o, use_modifiers=False):
    activate(o)
    bpy.ops.object.duplicate()

    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")

    co = bpy.context.active_object

    # support for text objects is only and only here, just convert them to curves.
    if co.type == "FONT":
        bpy.ops.object.convert(target="CURVE", keep_original=False)
    elif co.type != "CURVE":  # curve must be a curve...
        bpy.ops.object.delete()  # delete temporary object
        raise CamException("Source Curve Object Must Be of Type Curve")
    co.data.dimensions = "3D"
    co.data.bevel_depth = 0
    co.data.extrude = 0
    co.data.resolution_u = 100

    # first, convert to mesh to avoid parenting issues with hooks, then apply locrotscale.
    bpy.ops.object.convert(target="MESH", keep_original=False)

    if use_modifiers:
        eval_object = co.evaluated_get(bpy.context.evaluated_depsgraph_get())
        newmesh = bpy.data.meshes.new_from_object(eval_object)
        oldmesh = co.data
        co.modifiers.clear()
        co.data = newmesh
        bpy.data.meshes.remove(oldmesh)

    try:
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    except:
        pass

    return bpy.context.active_object


def make_visible(o):
    storage = [True, []]

    if not o.visible_get():
        storage[0] = False

    cam_collection = bpy.data.collections.new("cam")
    bpy.context.scene.collection.children.link(cam_collection)
    cam_collection.objects.link(bpy.context.object)

    for i in range(0, 20):
        storage[1].append(o.layers[i])

        o.layers[i] = bpy.context.scene.layers[i]

    return storage


def restore_visibility(o, storage):
    o.hide_viewport = storage[0]
    # print(storage)
    for i in range(0, 20):
        o.layers[i] = storage[1][i]


# this does more cleve chunks to Poly with hierarchies... ;)
def chunks_to_shapely(chunks):
    # print ('analyzing paths')
    for ch in chunks:  # first convert chunk to poly
        if len(ch.points) > 2:
            # pchunk=[]
            ch.poly = sgeometry.Polygon(ch.points[:, 0:2])
            if not ch.poly.is_valid:
                ch.poly = sgeometry.Polygon()
        else:
            ch.poly = sgeometry.Polygon()

    for ppart in chunks:  # then add hierarchy relations
        for ptest in chunks:
            if ppart != ptest:
                if not ppart.poly.is_empty and not ptest.poly.is_empty:
                    if ptest.poly.contains(ppart.poly):
                        # hierarchy works like this: - children get milled first.
                        ppart.parents.append(ptest)

    for ch in chunks:  # now make only simple polygons with holes, not more polys inside others
        found = False
        if len(ch.parents) % 2 == 1:
            for parent in ch.parents:
                if len(parent.parents) + 1 == len(ch.parents):
                    # nparents serves as temporary storage for parents,
                    ch.nparents = [parent]
                    # not to get mixed with the first parenting during the check
                    found = True
                    break

        if not found:
            ch.nparents = []

    for ch in chunks:  # then subtract the 1st level holes
        ch.parents = ch.nparents
        ch.nparents = None
        if len(ch.parents) > 0:
            try:
                ch.parents[0].poly = ch.parents[0].poly.difference(
                    ch.poly
                )  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)
            except:
                print("chunksToShapely oops!")

                lastPt = None
                tolerance = 0.0000003
                newPoints = []

                for pt in ch.points:
                    toleranceXok = True
                    toleranceYok = True
                    if lastPt is not None:
                        if abs(pt[0] - lastPt[0]) < tolerance:
                            toleranceXok = False
                        if abs(pt[1] - lastPt[1]) < tolerance:
                            toleranceYok = False

                        if toleranceXok or toleranceYok:
                            newPoints.append(pt)
                            lastPt = pt
                    else:
                        newPoints.append(pt)
                        lastPt = pt

                toleranceXok = True
                toleranceYok = True
                if abs(newPoints[0][0] - lastPt[0]) < tolerance:
                    toleranceXok = False
                if abs(newPoints[0][1] - lastPt[1]) < tolerance:
                    toleranceYok = False

                if not toleranceXok and not toleranceYok:
                    newPoints.pop()

                ch.points = np.array(newPoints)
                ch.poly = sgeometry.Polygon(ch.points)

                try:
                    ch.parents[0].poly = ch.parents[0].poly.difference(ch.poly)
                except:
                    # print('chunksToShapely double oops!')

                    lastPt = None
                    tolerance = 0.0000003
                    newPoints = []

                    for pt in ch.parents[0].points:
                        toleranceXok = True
                        toleranceYok = True
                        # print( '{0:.9f}, {0:.9f}, {0:.9f}'.format(pt[0], pt[1], pt[2]) )
                        # print(pt)
                        if lastPt is not None:
                            if abs(pt[0] - lastPt[0]) < tolerance:
                                toleranceXok = False
                            if abs(pt[1] - lastPt[1]) < tolerance:
                                toleranceYok = False

                            if toleranceXok or toleranceYok:
                                newPoints.append(pt)
                                lastPt = pt
                        else:
                            newPoints.append(pt)
                            lastPt = pt

                    toleranceXok = True
                    toleranceYok = True
                    if abs(newPoints[0][0] - lastPt[0]) < tolerance:
                        toleranceXok = False
                    if abs(newPoints[0][1] - lastPt[1]) < tolerance:
                        toleranceYok = False

                    if not toleranceXok and not toleranceYok:
                        newPoints.pop()
                    # print('starting and ending points too close, removing ending point')

                    ch.parents[0].points = np.array(newPoints)
                    ch.parents[0].poly = sgeometry.Polygon(ch.parents[0].points)

                    ch.parents[0].poly = ch.parents[0].poly.difference(
                        ch.poly
                    )  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)

    returnpolys = []

    for polyi in range(0, len(chunks)):  # export only the booleaned polygons
        ch = chunks[polyi]
        if not ch.poly.is_empty:
            if len(ch.parents) == 0:
                returnpolys.append(ch.poly)
    from shapely.geometry import MultiPolygon

    polys = MultiPolygon(returnpolys)
    return polys


def set_chunks_z(chunks, z):
    newchunks = []
    for ch in chunks:
        chunk = ch.copy()
        chunk.set_z(z)
        newchunks.append(chunk)
    return newchunks


def rotate_point_by_point(originp, p, ang):  # rotate point around another point with angle
    ox, oy, oz = originp
    px, py, oz = p

    if ang == abs(pi / 2):
        d = ang / abs(ang)
        qx = ox + d * (oy - py)
        qy = oy + d * (px - ox)
    else:
        qx = ox + cos(ang) * (px - ox) - sin(ang) * (py - oy)
        qy = oy + sin(ang) * (px - ox) + cos(ang) * (py - oy)
    rot_p = [qx, qy, oz]
    return rot_p


@jit(nopython=True, parallel=True, fastmath=True, cache=True)
def _internal_x_y_distance_to(ourpoints, theirpoints, cutoff):
    v1 = ourpoints[0]
    v2 = theirpoints[0]
    minDistSq = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2
    cutoffSq = cutoff**2
    for v1 in ourpoints:
        for v2 in theirpoints:
            distSq = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2
            if distSq < cutoffSq:
                return sqrt(distSq)
            minDistSq = min(distSq, minDistSq)
    return sqrt(minDistSq)


# don't make this @jit parallel, because it sometimes gets called with small N
# and the overhead of threading is too much.
@jit(nopython=True, fastmath=True, cache=True)
def _optimize_internal(points, keep_points, e, protect_vertical, protect_vertical_limit):
    # inlined so that numba can optimize it nicely
    def _mag_sq(v1):
        return v1[0] ** 2 + v1[1] ** 2 + v1[2] ** 2

    def _dot_pr(v1, v2):
        return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

    def _applyVerticalLimit(v1, v2, cos_limit):
        """Test Path Segment on Verticality Threshold, for Protect_vertical Option"""
        z = abs(v1[2] - v2[2])
        if z > 0:
            # don't use this vector because dot product of 0,0,1 is trivially just v2[2]
            #            vec_up = np.array([0, 0, 1])
            vec_diff = v1 - v2
            vec_diff2 = v2 - v1
            vec_diff_mag = np.sqrt(_mag_sq(vec_diff))
            # dot product = cos(angle) * mag1 * mag2
            cos1_times_mag = vec_diff[2]
            cos2_times_mag = vec_diff2[2]
            if cos1_times_mag > cos_limit * vec_diff_mag:
                # vertical, moving down
                v1[0] = v2[0]
                v1[1] = v2[1]
            elif cos2_times_mag > cos_limit * vec_diff_mag:
                # vertical, moving up
                v2[0] = v1[0]
                v2[1] = v1[1]

    cos_limit = cos(protect_vertical_limit)
    prev_i = 0
    for i in range(1, points.shape[0] - 1):
        v1 = points[prev_i]
        v2 = points[i + 1]
        vmiddle = points[i]

        line_direction = v2 - v1
        line_length = sqrt(_mag_sq(line_direction))
        if line_length == 0:
            # don't keep duplicate points
            keep_points[i] = False
            continue
        # normalize line direction
        line_direction *= 1.0 / line_length  # N in formula below
        # X = A + tN (line formula) Distance to point P
        # A = v1, N = line_direction, P = vmiddle
        # distance = || (P - A) - ((P-A).N)N ||
        point_offset = vmiddle - v1
        distance_sq = _mag_sq(
            point_offset - (line_direction * _dot_pr(point_offset, line_direction))
        )
        # compare on squared distance to save a sqrt
        if distance_sq < e * e:
            keep_points[i] = False
        else:
            keep_points[i] = True
            if protect_vertical:
                _applyVerticalLimit(points[prev_i], points[i], cos_limit)
            prev_i = i


def optimize_chunk(chunk, operation):
    if len(chunk.points) > 2:
        points = chunk.points
        naxispoints = False
        if len(chunk.startpoints) > 0:
            startpoints = chunk.startpoints
            endpoints = chunk.endpoints
            naxispoints = True

        protect_vertical = operation.movement.protect_vertical and operation.machine_axes == "3"
        keep_points = np.full(points.shape[0], True)
        # shape points need to be on line,
        # but we need to protect vertical - which
        # means changing point values
        # bits of this are moved from simple.py so that
        # numba can optimize as a whole
        _optimize_internal(
            points,
            keep_points,
            operation.optimisation.optimize_threshold * 0.000001,
            protect_vertical,
            operation.movement.protect_vertical_limit,
        )

        # now do numpy select by boolean array
        chunk.points = points[keep_points]
        if naxispoints:
            # list comprehension so we don't have to do tons of appends
            chunk.startpoints = [
                chunk.startpoints[i] for i, b in enumerate(keep_points) if b == True
            ]
            chunk.endpoints = [chunk.endpoints[i] for i, b in enumerate(keep_points) if b == True]
            chunk.rotations = [chunk.rotations[i] for i, b in enumerate(keep_points) if b == True]
    return chunk


def parent_child_distance(parents, children, o, distance=None):
    # parenting based on x,y distance between chunks
    # hierarchy works like this: - children get milled first.

    if distance is None:
        dlim = o.distance_between_paths * 2
        if (o.strategy == "PARALLEL" or o.strategy == "CROSS") and o.movement.parallel_step_back:
            dlim = dlim * 2
    else:
        dlim = distance

    for child in children:
        for parent in parents:
            isrelation = False
            if parent != child:
                if parent.x_y_distance_within(child, cutoff=dlim):
                    parent.children.append(child)
                    child.parents.append(parent)


def parent_child(parents, children, o):
    # connect all children to all parents. Useful for any type of defining hierarchy.
    # hierarchy works like this: - children get milled first.

    for child in children:
        for parent in parents:
            if parent != child:
                parent.children.append(child)
                child.parents.append(parent)


def parent_child_poly(parents, children, o):
    # hierarchy based on polygons - a polygon inside another is his child.
    # hierarchy works like this: - children get milled first.

    for parent in parents:
        if parent.poly is None:
            parent.update_poly()
        for child in children:
            if child.poly is None:
                child.update_poly()
            if child != parent:  # and len(child.poly)>0
                if parent.poly.contains(sgeometry.Point(child.poly.boundary.coords[0])):
                    parent.children.append(child)
                    child.parents.append(parent)


def extend_chunks_5_axis(chunks, o):
    """Extend chunks with 5-axis cutter start and end points.

    This function modifies the provided chunks by appending calculated start
    and end points for a cutter based on the specified orientation and
    movement parameters. It determines the starting position of the cutter
    based on the machine's settings and the object's movement constraints.
    The function iterates through each point in the chunks and updates their
    start and end points accordingly.

    Args:
        chunks (list): A list of chunk objects that will be modified.
        o (object): An object containing movement and orientation data.
    """

    s = bpy.context.scene
    m = s.cam_machine
    s = bpy.context.scene
    free_height = o.movement.free_height  # o.max.z +
    if m.use_position_definitions:  # dhull
        cutterstart = Vector(
            (m.starting_position.x, m.starting_position.y, max(o.max.z, m.starting_position.z))
        )  # start point for casting
    else:
        # start point for casting
        cutterstart = Vector((0, 0, max(o.max.z, free_height)))
    cutterend = Vector((0, 0, o.min.z))
    oriname = o.name + " orientation"
    ori = s.objects[oriname]
    # rotationaxes = rotTo2axes(ori.rotation_euler,'CA')#warning-here it allready is reset to 0!!
    print("rot", o.rotationaxes)
    a, b = o.rotationaxes  # this is all nonsense by now.
    for chunk in chunks:
        for v in chunk.points:
            cutterstart.x = v[0]
            cutterstart.y = v[1]
            cutterend.x = v[0]
            cutterend.y = v[1]
            chunk.startpoints.append(cutterstart.to_tuple())
            chunk.endpoints.append(cutterend.to_tuple())
            chunk.rotations.append(
                (a, b, 0)
            )  # TODO: this is a placeholder. It does 99.9% probably write total nonsense.


def get_closest_chunk(o, pos, chunks):
    """Find the closest chunk to a given position.

    This function iterates through a list of chunks and determines which
    chunk is closest to the specified position. It checks if each chunk's
    children are sorted before calculating the distance. The chunk with the
    minimum distance to the given position is returned.

    Args:
        o: An object representing the origin point.
        pos: A position to which the closest chunk is calculated.
        chunks (list): A list of chunk objects to evaluate.

    Returns:
        Chunk: The closest chunk object to the specified position, or None if no valid
            chunk is found.
    """

    # ch=-1
    mind = 2000
    d = 100000000000
    ch = None
    for chtest in chunks:
        cango = True
        # here was chtest.getNext==chtest, was doing recursion error and slowing down.
        for child in chtest.children:
            if not child.sorted:
                cango = False
                break
        if cango:
            d = chtest.distance(pos, o)
            if d < mind:
                ch = chtest
                mind = d
    return ch
