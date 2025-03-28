"""Fabex 'cam_chunk.py' © 2012 Vilem Novak

Classes and Functions to build, store and optimize CAM path chunks.
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
import sys
import time
import random

import numpy as np
import shapely
from shapely import ops as sops
from shapely import geometry as sgeometry
from shapely.geometry import polygon as spolygon
from shapely.geometry import MultiPolygon

try:
    import ocl
except ImportError:
    try:
        import opencamlib as ocl
    except ImportError:
        pass

import bpy
from mathutils import Vector, Euler

try:
    import bl_ext.blender_org.simplify_curves_plus as curve_simplify
except ImportError:
    pass

from .collision import (
    get_sample_bullet,
    get_sample_bullet_n_axis,
    prepare_bullet_collision,
)
from .constants import OCL_SCALE
from .exception import CamException

from .utilities.async_utils import progress_async
from .utilities.chunk_utils import (
    rotate_point_by_point,
    _internal_x_y_distance_to,
    mesh_from_curve,
    chunks_to_shapely,
    parent_child,
    parent_child_distance,
    get_closest_chunk,
)
from .utilities.image_utils import (
    get_sample_image,
    prepare_area,
    render_sample_image,
    get_circle_binary,
)
from .utilities.numba_utils import jit
from .utilities.ocl_utils import (
    oclSample,
    get_oclSTL,
    ocl_sample,
    oclWaterlineLayerHeights,
)
from .utilities.shapely_utils import (
    shapely_to_coordinates,
    shapely_to_curve,
    shapely_to_multipolygon,
)
from .utilities.simple_utils import (
    activate,
    distance_2d,
    progress,
    select_multiple,
    timing_add,
    timing_init,
    timing_start,
    tuple_add,
    tuple_multiply,
    tuple_subtract,
    is_vertical_limit,
    get_cache_path,
)


# for building points - stores points as lists for easy insert /append behaviour
class CamPathChunkBuilder:
    def __init__(self, inpoints=None, startpoints=None, endpoints=None, rotations=None):
        if inpoints is None:
            inpoints = []
        self.points = inpoints
        self.startpoints = startpoints or []
        self.endpoints = endpoints or []
        self.rotations = rotations or []
        self.depth = None

    def to_chunk(self):
        chunk = CamPathChunk(self.points, self.startpoints, self.endpoints, self.rotations)
        if len(self.points) > 2 and np.array_equal(self.points[0], self.points[-1]):
            chunk.closed = True
        if self.depth is not None:
            chunk.depth = self.depth

        return chunk


# an actual chunk - stores points as numpy arrays
class CamPathChunk:
    def __init__(self, inpoints, startpoints=None, endpoints=None, rotations=None):
        # name this as _points so nothing external accesses it directly
        # for 3 axes, this is only storage of points. For N axes, here go the sampled points
        if len(inpoints) == 0:
            self.points = np.empty(shape=(0, 3))
        else:
            self.points = np.array(inpoints)
        self.poly = None  # get polygon just in time
        self.simppoly = None
        if startpoints:
            # from where the sweep test begins, but also retract point for given path
            self.startpoints = startpoints
        else:
            self.startpoints = []
        if endpoints:
            self.endpoints = endpoints
        else:
            self.endpoints = []  # where sweep test ends
        if rotations:
            self.rotations = rotations
        else:
            self.rotations = []  # rotation of the machine axes
        self.closed = False
        self.children = []
        self.parents = []
        # self.unsortedchildren=False
        self.sorted = False  # if the chunk has allready been milled in the simulation
        self.length = 0  # this is total length of this chunk.
        self.zstart = 0  # this is stored for ramps mainly,
        # because they are added afterwards, but have to use layer info
        self.zend = 0  #

    def update_poly(self):
        if len(self.points) > 2:
            self.poly = sgeometry.Polygon(self.points[:, 0:2])
        else:
            self.poly = sgeometry.Polygon()

    def get_point(self, n):
        return self.points[n].tolist()

    def get_points(self):
        return self.points.tolist()

    def get_points_np(self):
        return self.points

    def set_points(self, points):
        self.points = np.array(points)

    def count(self):
        return len(self.points)

    def copy(self):
        nchunk = CamPathChunk(
            inpoints=self.points.copy(),
            startpoints=self.startpoints,
            endpoints=self.endpoints,
            rotations=self.rotations,
        )
        nchunk.closed = self.closed
        nchunk.children = self.children
        nchunk.parents = self.parents
        nchunk.sorted = self.sorted
        nchunk.length = self.length
        return nchunk

    def shift(self, x, y, z):
        self.points = self.points + np.array([x, y, z])
        for i, p in enumerate(self.startpoints):
            self.startpoints[i] = (p[0] + x, p[1] + y, p[2] + z)
        for i, p in enumerate(self.endpoints):
            self.endpoints[i] = (p[0] + x, p[1] + y, p[2] + z)

    def set_z(self, z, if_bigger=False):
        if if_bigger:
            self.points[:, 2] = z if z > self.points[:, 2] else self.points[:, 2]
        else:
            self.points[:, 2] = z

    def offset_z(self, z):
        self.points[:, 2] += z

    def flip_x(self, x_centre):
        self.points[:, 0] = x_centre - self.points[:, 0]

    def is_below_z(self, z):
        return np.any(self.points[:, 2] < z)

    def clamp_z(self, z):
        np.clip(self.points[:, 2], z, None, self.points[:, 2])

    def clamp_max_z(self, z):
        np.clip(self.points[:, 2], None, z, self.points[:, 2])

    def distance(self, pos, o):
        if self.closed:
            dist_sq = (pos[0] - self.points[:, 0]) ** 2 + (pos[1] - self.points[:, 1]) ** 2
            return sqrt(np.min(dist_sq))
        else:
            if o.movement.type == "MEANDER":
                d1 = distance_2d(pos, self.points[0])
                d2 = distance_2d(pos, self.points[-1])
                # if d2<d1:
                #   ch.points.reverse()
                return min(d1, d2)
            else:
                return distance_2d(pos, self.points[0])

    def distance_start(self, pos, o):
        return distance_2d(pos, self.points[0])

    def x_y_distance_within(self, other, cutoff):
        if self.poly is None:
            self.update_poly()
        if other.poly is None:
            other.update_poly()
        if not self.poly.is_empty and not other.poly.is_empty:
            # print(other.poly, cutoff)
            return self.poly.dwithin(other.poly, cutoff)
        else:
            return _internal_x_y_distance_to(self.points, other.points, cutoff) < cutoff

    # if cutoff is set, then the first distance < cutoff is returned
    def x_y_distance_to(self, other, cutoff=0):
        if self.poly is None:
            self.update_poly()
        if other.poly is None:
            other.update_poly()
        if not self.poly.is_empty and not other.poly.is_empty:
            # both polygons have >2 points
            # simplify them if they aren't already, to speed up distance finding
            if self.simppoly is None:
                self.simppoly = self.poly.simplify(0.0003).boundary
            if other.simppoly is None:
                other.simppoly = other.poly.simplify(0.0003).boundary
            return self.simppoly.distance(other.simppoly)
        else:  # this is the old method, preferably should be replaced in most cases except parallel
            # where this method works probably faster.
            # print('warning, sorting will be slow due to bad parenting in parentChildDist')
            return _internal_x_y_distance_to(self.points, other.points, cutoff)

    def adapt_distance(self, pos, o):
        # reorders chunk so that it starts at the closest point to pos.
        if self.closed:
            dist_sq = (pos[0] - self.points[:, 0]) ** 2 + (pos[1] - self.points[:, 1]) ** 2
            point_idx = np.argmin(dist_sq)
            new_points = np.concatenate((self.points[point_idx:], self.points[: point_idx + 1]))
            self.points = new_points
        else:
            if o.movement.type == "MEANDER":
                d1 = distance_2d(pos, self.points[0])
                d2 = distance_2d(pos, self.points[-1])
                if d2 < d1:
                    self.points = np.flip(self.points, axis=0)

    def get_next_closest(self, o, pos):
        # finds closest chunk that can be milled, when inside sorting hierarchy.
        mind = 100000000000

        self.cango = False
        closest = None
        testlist = []
        testlist.extend(self.children)
        tested = []
        tested.extend(self.children)
        ch = None
        while len(testlist) > 0:
            chtest = testlist.pop()
            if not chtest.sorted:
                self.cango = False
                cango = True

                for child in chtest.children:
                    if not child.sorted:
                        if child not in tested:
                            testlist.append(child)
                            tested.append(child)
                        cango = False

                if cango:
                    d = chtest.distance(pos, o)
                    if d < mind:
                        ch = chtest
                        mind = d
        if ch is not None:
            # print('found some')
            return ch
        # print('returning none')
        return None

    def get_length(self):
        # computes length of the chunk - in 3d

        point_differences = self.points[0:-1, :] - self.points[1:, :]
        distances = np.linalg.norm(point_differences, axis=1)
        self.length = np.sum(distances)

    def reverse(self):
        self.points = np.flip(self.points, axis=0)
        self.startpoints.reverse()
        self.endpoints.reverse()
        self.rotations.reverse()

    def pop(self, index):
        print("WARNING: Popping from Chunk Is Slow", self, index)
        self.points = np.concatenate((self.points[0:index], self.points[index + 1 :]), axis=0)
        if len(self.startpoints) > 0:
            self.startpoints.pop(index)
            self.endpoints.pop(index)
            self.rotations.pop(index)

    def dedupe_points(self):
        if len(self.points) > 1:
            keep_points = np.empty(self.points.shape[0], dtype=bool)
            keep_points[0] = True
            diff_points = np.sum((self.points[1:] - self.points[:1]) ** 2, axis=1)
            keep_points[1:] = diff_points > 0.000000001
            self.points = self.points[keep_points, :]

    def insert(self, at_index, point, startpoint=None, endpoint=None, rotation=None):
        self.append(
            point,
            startpoint=startpoint,
            endpoint=endpoint,
            rotation=rotation,
            at_index=at_index,
        )

    def append(self, point, startpoint=None, endpoint=None, rotation=None, at_index=None):
        if at_index is None:
            self.points = np.concatenate((self.points, np.array([point])))
            if startpoint is not None:
                self.startpoints.append(startpoint)
            if endpoint is not None:
                self.endpoints.append(endpoint)
            if rotation is not None:
                self.rotations.append(rotation)
        else:
            self.points = np.concatenate(
                (self.points[0:at_index], np.array([point]), self.points[at_index:])
            )
            if startpoint is not None:
                self.startpoints[at_index:at_index] = [startpoint]
            if endpoint is not None:
                self.endpoints[at_index:at_index] = [endpoint]
            if rotation is not None:
                self.rotations[at_index:at_index] = [rotation]

    def extend(self, points, startpoints=None, endpoints=None, rotations=None, at_index=None):
        if len(points) == 0:
            return
        if at_index is None:
            self.points = np.concatenate((self.points, np.array(points)))
            if startpoints is not None:
                self.startpoints.extend(startpoints)
            if endpoints is not None:
                self.endpoints.extend(endpoints)
            if rotations is not None:
                self.rotations.extend(rotations)
        else:
            self.points = np.concatenate(
                (self.points[0:at_index], np.array(points), self.points[at_index:])
            )
            if startpoints is not None:
                self.startpoints[at_index:at_index] = startpoints
            if endpoints is not None:
                self.endpoints[at_index:at_index] = endpoints
            if rotations is not None:
                self.rotations[at_index:at_index] = rotations

    def clip_points(self, minx, maxx, miny, maxy):
        """Remove Any Points Outside This Range"""
        included_values = (self.points[:, 0] >= minx) and (
            (self.points[:, 0] <= maxx)
            and (self.points[:, 1] >= maxy)
            and (self.points[:, 1] <= maxy)
        )
        self.points = self.points[included_values]

    def ramp_contour(self, zstart, zend, o):
        stepdown = zstart - zend
        chunk_points = []
        estlength = (zstart - zend) / tan(o.movement.ramp_in_angle)
        self.get_length()
        ramplength = estlength  # min(ch.length,estlength)
        ltraveled = 0
        endpoint = None
        i = 0
        # z=zstart
        znew = 10
        rounds = 0  # for counting if ramping makes more layers
        while endpoint is None and not (znew == zend and i == 0):  #
            # for i,s in enumerate(ch.points):
            # print(i, znew, zend, len(ch.points))
            s = self.points[i]

            if i > 0:
                s2 = self.points[i - 1]
                ltraveled += distance_2d(s, s2)
                ratio = ltraveled / ramplength
            elif rounds > 0 and i == 0:
                s2 = self.points[-1]
                ltraveled += distance_2d(s, s2)
                ratio = ltraveled / ramplength
            else:
                ratio = 0
            znew = zstart - stepdown * ratio
            if znew <= zend:
                ratio = (z - zend) / (z - znew)
                v1 = Vector(chunk_points[-1])
                v2 = Vector((s[0], s[1], znew))
                v = v1 + ratio * (v2 - v1)
                chunk_points.append((v.x, v.y, max(s[2], v.z)))

                if zend == o.min.z and endpoint is None and self.closed:
                    endpoint = i + 1
                    if endpoint == len(self.points):
                        endpoint = 0
            # print(endpoint,len(ch.points))
            # else:
            znew = max(znew, zend, s[2])
            chunk_points.append((s[0], s[1], znew))
            z = znew
            if endpoint is not None:
                break
            i += 1
            if i >= len(self.points):
                i = 0
                rounds += 1
        # if not o.use_layers:
        # endpoint=0
        if endpoint is not None:  # append final contour on the bottom z level
            i = endpoint
            started = False
            # print('finaliz')
            if i == len(self.points):
                i = 0
            while i != endpoint or not started:
                started = True
                s = self.points[i]
                chunk_points.append((s[0], s[1], s[2]))
                # print(i,endpoint)
                i += 1
                if i == len(self.points):
                    i = 0
        # ramp out
        if o.movement.ramp_out and (
            not o.use_layers or not o.first_down or (o.first_down and endpoint is not None)
        ):
            z = zend
            # i=endpoint

            while z < o.max_z:
                if i == len(self.points):
                    i = 0
                s1 = self.points[i]
                i2 = i - 1
                if i2 < 0:
                    i2 = len(self.points) - 1
                s2 = self.points[i2]
                l = distance_2d(s1, s2)
                znew = z + tan(o.movement.ramp_out_angle) * l
                if znew > o.max_z:
                    ratio = (z - o.max_z) / (z - znew)
                    v1 = Vector(chunk_points[-1])
                    v2 = Vector((s1[0], s1[1], znew))
                    v = v1 + ratio * (v2 - v1)
                    chunk_points.append((v.x, v.y, v.z))

                else:
                    chunk_points.append((s1[0], s1[1], znew))
                z = znew
                i += 1

        # TODO: convert to numpy properly
        self.points = np.array(chunk_points)

    def ramp_zig_zag(self, zstart, zend, o):
        # TODO: convert to numpy properly
        if zend == None:
            zend = self.points[0][2]
        chunk_points = []
        # print(zstart,zend)
        if zend < zstart:  # this check here is only for stupid setup,
            # when the chunks lie actually above operation start z.

            stepdown = zstart - zend

            estlength = (zstart - zend) / tan(o.movement.ramp_in_angle)
            self.get_length()
            if self.length > 0:  # for single point chunks..
                ramplength = estlength
                zigzaglength = ramplength / 2.000
                turns = 1
                print("Turns %i" % turns)
                if zigzaglength > self.length:
                    turns = ceil(zigzaglength / self.length)
                    ramplength = turns * self.length * 2.0
                    zigzaglength = self.length
                    ramppoints = self.points.tolist()

                else:
                    zigzagtraveled = 0.0
                    haspoints = False
                    ramppoints = [(self.points[0][0], self.points[0][1], self.points[0][2])]
                    i = 1
                    while not haspoints:
                        # print(i,zigzaglength,zigzagtraveled)
                        p1 = ramppoints[-1]
                        p2 = self.points[i]
                        d = distance_2d(p1, p2)
                        zigzagtraveled += d
                        if zigzagtraveled >= zigzaglength or i + 1 == len(self.points):
                            ratio = 1 - (zigzagtraveled - zigzaglength) / d
                            if i + 1 == len(
                                self.points
                            ):  # this condition is for a rare case of combined layers+bridges+ramps..
                                ratio = 1
                            v = p1 + ratio * (p2 - p1)
                            ramppoints.append(v.tolist())
                            haspoints = True
                        else:
                            ramppoints.append(p2)
                        i += 1
                negramppoints = ramppoints.copy()
                negramppoints.reverse()
                ramppoints.extend(negramppoints[1:])

                traveled = 0.0
                chunk_points.append(
                    (
                        self.points[0][0],
                        self.points[0][1],
                        max(self.points[0][2], zstart),
                    )
                )
                for r in range(turns):
                    for p in range(0, len(ramppoints)):
                        p1 = chunk_points[-1]
                        p2 = ramppoints[p]
                        d = distance_2d(p1, p2)
                        traveled += d
                        ratio = traveled / ramplength
                        znew = zstart - stepdown * ratio
                        # max value here is so that it doesn't go
                        chunk_points.append((p2[0], p2[1], max(p2[2], znew)))
                        # below surface in the case of 3d paths

                # chunks = setChunksZ([ch],zend)
                chunk_points.extend(self.points.tolist())

            ######################################
            # ramp out - this is the same thing, just on the other side..
            if o.movement.ramp_out:
                zstart = o.max_z
                zend = self.points[-1][2]
                # again, sometimes a chunk could theoretically end above the starting level.
                if zend < zstart:
                    stepdown = zstart - zend

                    estlength = (zstart - zend) / tan(o.movement.ramp_out_angle)
                    self.get_length()
                    if self.length > 0:
                        ramplength = estlength
                        zigzaglength = ramplength / 2.000
                        turns = 1
                        print("Turns %i" % turns)
                        if zigzaglength > self.length:
                            turns = ceil(zigzaglength / self.length)
                            ramplength = turns * self.length * 2.0
                            zigzaglength = self.length
                            ramppoints = self.points.tolist()
                            # revert points here, we go the other way.
                            ramppoints.reverse()

                        else:
                            zigzagtraveled = 0.0
                            haspoints = False
                            ramppoints = [
                                (
                                    self.points[-1][0],
                                    self.points[-1][1],
                                    self.points[-1][2],
                                )
                            ]
                            i = len(self.points) - 2
                            while not haspoints:
                                # print(i,zigzaglength,zigzagtraveled)
                                p1 = ramppoints[-1]
                                p2 = self.points[i]
                                d = distance_2d(p1, p2)
                                zigzagtraveled += d
                                if zigzagtraveled >= zigzaglength or i + 1 == len(self.points):
                                    ratio = 1 - (zigzagtraveled - zigzaglength) / d
                                    if i + 1 == len(
                                        self.points
                                    ):  # this condition is for a rare case of
                                        # combined layers+bridges+ramps...
                                        ratio = 1
                                    # print((ratio,zigzaglength))
                                    v = p1 + ratio * (p2 - p1)
                                    ramppoints.append(v.tolist())
                                    haspoints = True
                                # elif :

                                else:
                                    ramppoints.append(p2)
                                i -= 1
                        negramppoints = ramppoints.copy()
                        negramppoints.reverse()
                        ramppoints.extend(negramppoints[1:])

                        traveled = 0.0
                        for r in range(turns):
                            for p in range(0, len(ramppoints)):
                                p1 = chunk_points[-1]
                                p2 = ramppoints[p]
                                d = distance_2d(p1, p2)
                                traveled += d
                                ratio = 1 - (traveled / ramplength)
                                znew = zstart - stepdown * ratio
                                chunk_points.append((p2[0], p2[1], max(p2[2], znew)))
                                # max value here is so that it doesn't go below surface in the case of 3d paths
        self.points = np.array(chunk_points)

    #  modify existing path start point
    def change_path_start(self, o):
        if o.profile_start > 0:
            newstart = o.profile_start
            chunkamt = len(self.points)
            newstart = newstart % chunkamt
            self.points = np.concatenate((self.points[newstart:], self.points[:newstart]))

    def break_path_for_leadin_leadout(self, o):
        iradius = o.lead_in
        oradius = o.lead_out
        if iradius + oradius > 0:
            chunkamt = len(self.points)

            for i in range(chunkamt - 1):
                apoint = self.points[i]
                bpoint = self.points[i + 1]
                bmax = bpoint[0] - apoint[0]
                bmay = bpoint[1] - apoint[1]
                segmentLength = hypot(bmax, bmay)  # find segment length

                if segmentLength > 2 * max(
                    iradius, oradius
                ):  # Be certain there is enough room for the leadin and leadiout
                    # add point on the line here
                    # average of the two x points to find center
                    newpointx = (bpoint[0] + apoint[0]) / 2
                    # average of the two y points to find center
                    newpointy = (bpoint[1] + apoint[1]) / 2
                    self.points = np.concatenate(
                        (
                            self.points[: i + 1],
                            np.array([[newpointx, newpointy, apoint[2]]]),
                            self.points[i + 1 :],
                        )
                    )

    def lead_contour(self, o):
        perimeterDirection = 1  # 1 is clockwise, 0 is CCW
        if o.movement.spindle_rotation == "CW":
            if o.movement.type == "CONVENTIONAL":
                perimeterDirection = 0

        if self.parents:  # if it is inside another parent
            perimeterDirection ^= 1  # toggle with a bitwise XOR
            print("Has Parent")

        if perimeterDirection == 1:
            print("Path Direction is Clockwise")
        else:
            print("Path Direction is Counter Clockwise")
        iradius = o.lead_in
        oradius = o.lead_out
        start = self.points[0]
        nextp = self.points[1]
        rpoint = rotate_point_by_point(start, nextp, pi / 2)
        dx = rpoint[0] - start[0]
        dy = rpoint[1] - start[1]
        la = hypot(dx, dy)
        pvx = (iradius * dx) / la + start[0]  # arc center(x)
        pvy = (iradius * dy) / la + start[1]  # arc center(y)
        arc_c = [pvx, pvy, start[2]]

        # TODO: this could easily be numpy
        chunk_points = []  # create a new cutting path

        # add lead in arc in the begining
        if round(o.lead_in, 6) > 0.0:
            for i in range(15):
                iangle = -i * (pi / 2) / 15
                arc_p = rotate_point_by_point(arc_c, start, iangle)
                chunk_points.insert(0, arc_p)

        # glue rest of the path to the arc
        chunk_points.extend(self.points.tolist())
        # for i in range(len(self.points)):
        #     chunk_points.append(self.points[i])

        # add lead out arc to the end
        if round(o.lead_in, 6) > 0.0:
            for i in range(15):
                iangle = i * (pi / 2) / 15
                arc_p = rotate_point_by_point(arc_c, start, iangle)
                chunk_points.append(arc_p)

        self.points = np.array(chunk_points)


def chunks_coherency(chunks):
    # checks chunks for their stability, for pencil path.
    # it checks if the vectors direction doesn't jump too much too quickly,
    # if this happens it splits the chunk on such places,
    # too much jumps = deletion of the chunk. this is because otherwise the router has to slow down too often,
    # but also means that some parts detected by cavity algorithm won't be milled
    nchunks = []
    for chunk in chunks:
        if len(chunk.points) > 2:
            nchunk = CamPathChunkBuilder()

            # doesn't check for 1 point chunks here, they shouldn't get here at all.
            lastvec = Vector(chunk.points[1]) - Vector(chunk.points[0])
            for i in range(0, len(chunk.points) - 1):
                nchunk.points.append(chunk.points[i])
                vec = Vector(chunk.points[i + 1]) - Vector(chunk.points[i])
                angle = vec.angle(lastvec, vec)
                # print(angle,i)
                if angle > 1.07:  # 60 degrees is maximum toleration for pencil paths.
                    if len(nchunk.points) > 4:  # this is a testing threshold
                        nchunks.append(nchunk.to_chunk())
                    nchunk = CamPathChunkBuilder()
                lastvec = vec
            if len(nchunk.points) > 4:  # this is a testing threshold
                nchunk.points = np.array(nchunk.points)
                nchunks.append(nchunk)
    return nchunks


def limit_chunks(chunks, o, force=False):  # TODO: this should at least add point on area border...
    # but shouldn't be needed at all at the first place...
    if o.use_limit_curve or force:
        nchunks = []
        for ch in chunks:
            prevsampled = True
            nch = CamPathChunkBuilder()
            nch1 = None
            closed = True
            for s in ch.points:
                sampled = o.ambient.contains(sgeometry.Point(s[0], s[1]))
                if not sampled and len(nch.points) > 0:
                    nch.closed = False
                    closed = False
                    nchunks.append(nch.to_chunk())
                    if nch1 is None:
                        nch1 = nchunks[-1]
                    nch = CamPathChunkBuilder()
                elif sampled:
                    nch.points.append(s)
                prevsampled = sampled
            if (
                len(nch.points) > 2
                and closed
                and ch.closed
                and np.array_equal(ch.points[0], ch.points[-1])
            ):
                nch.closed = True
            elif (
                ch.closed
                and nch1 is not None
                and len(nch.points) > 1
                and np.array_equal(nch.points[-1], nch1.points[0])
            ):
                # here adds beginning of closed chunk to the end, if the chunks were split during limiting
                nch.points.extend(nch1.points.tolist())
                nchunks.remove(nch1)
                print("Joining")
            if len(nch.points) > 0:
                nchunks.append(nch.to_chunk())
        return nchunks
    else:
        return chunks


def mesh_from_curve_to_chunk(object):
    mesh = object.data
    # print('detecting contours from curve')
    chunks = []
    chunk = CamPathChunkBuilder()
    ek = mesh.edge_keys
    d = {}
    for e in ek:
        d[e] = 1  #
    dk = d.keys()
    x = object.location.x
    y = object.location.y
    z = object.location.z
    lastvi = 0
    vtotal = len(mesh.vertices)
    perc = 0
    progress(f"Processing Curve - START - Vertices: {vtotal}")
    for vi in range(0, len(mesh.vertices) - 1):
        co = (mesh.vertices[vi].co + object.location).to_tuple()
        if not dk.isdisjoint([(vi, vi + 1)]) and d[(vi, vi + 1)] == 1:
            chunk.points.append(co)
        else:
            chunk.points.append(co)
            if len(chunk.points) > 2 and (
                not (dk.isdisjoint([(vi, lastvi)])) or not (dk.isdisjoint([(lastvi, vi)]))
            ):  # this was looping chunks of length of only 2 points...
                # print('itis')

                chunk.closed = True
                chunk.points.append((mesh.vertices[lastvi].co + object.location).to_tuple())
                # add first point to end#originally the z was mesh.vertices[lastvi].co.z+z
            lastvi = vi + 1
            chunk = chunk.to_chunk()
            chunk.dedupe_points()
            if chunk.count() >= 1:
                # dump single point chunks
                chunks.append(chunk)
            chunk = CamPathChunkBuilder()

    progress("Processing Curve - FINISHED")

    vi = len(mesh.vertices) - 1
    chunk.points.append(
        (
            mesh.vertices[vi].co.x + x,
            mesh.vertices[vi].co.y + y,
            mesh.vertices[vi].co.z + z,
        )
    )
    if not (dk.isdisjoint([(vi, lastvi)])) or not (dk.isdisjoint([(lastvi, vi)])):
        chunk.closed = True
        chunk.points.append(
            (
                mesh.vertices[lastvi].co.x + x,
                mesh.vertices[lastvi].co.y + y,
                mesh.vertices[lastvi].co.z + z,
            )
        )
    chunk = chunk.to_chunk()
    chunk.dedupe_points()
    if chunk.count() >= 1:
        # dump single point chunks
        chunks.append(chunk)
    return chunks


def curve_to_chunks(o, use_modifiers=False):
    co = mesh_from_curve(o, use_modifiers)
    chunks = mesh_from_curve_to_chunk(co)

    co = bpy.context.active_object

    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[co.name].select_set(True)
    bpy.ops.object.delete()

    return chunks


def shapely_to_chunks(p, zlevel):  #
    chunk_builders = []
    # p=sortContours(p)
    seq = shapely_to_coordinates(p)
    i = 0
    for s in seq:
        # progress(p[i])
        if len(s) > 1:
            chunk = CamPathChunkBuilder([])
            for v in s:
                if p.has_z:
                    chunk.points.append((v[0], v[1], v[2]))
                else:
                    chunk.points.append((v[0], v[1], zlevel))

            chunk_builders.append(chunk)
        i += 1
    chunk_builders.reverse()  # this is for smaller shapes first.
    return [c.to_chunk() for c in chunk_builders]


def curve_to_shapely(cob, use_modifiers=False):
    """Convert a curve object to Shapely polygons.

    This function takes a curve object and converts it into a list of
    Shapely polygons. It first breaks the curve into chunks and then
    transforms those chunks into Shapely-compatible polygon representations.
    The `use_modifiers` parameter allows for additional processing of the
    curve before conversion, depending on the specific requirements of the
    application.

    Args:
        cob: The curve object to be converted.
        use_modifiers (bool): A flag indicating whether to apply modifiers
            during the conversion process. Defaults to False.

    Returns:
        list: A list of Shapely polygons created from the curve object.
    """

    chunks = curve_to_chunks(cob, use_modifiers)
    polys = chunks_to_shapely(chunks)
    return polys


async def sample_chunks_n_axis(o, pathSamples, layers):
    """Sample chunks along a specified axis based on provided paths and layers.

    This function processes a set of path samples and organizes them into
    chunks according to specified layers. It prepares the collision world if
    necessary, updates the cutter's rotation based on the path samples, and
    handles the sampling of points along the paths. The function also
    manages the relationships between the sampled points and their
    respective layers, ensuring that the correct points are added to each
    chunk. The resulting chunks can be used for further processing in a 3D
    environment.

    Args:
        o (object): An object containing properties such as min/max coordinates,
            cutter shape, and other relevant parameters.
        pathSamples (list): A list of path samples, each containing start points,
            end points, and rotations.
        layers (list): A list of layer definitions that specify the boundaries
            for sampling.

    Returns:
        list: A list of sampled chunks organized by layers.
    """

    #
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    # prepare collision world
    if o.update_bullet_collision_tag:
        prepare_bullet_collision(o)
        # print('getting ambient')
        get_ambient(o)
        o.update_bullet_collision_tag = False
    # print (o.ambient)
    cutter = o.cutter_shape
    cutterdepth = cutter.dimensions.z / 2

    t = time.time()
    print("Sampling Paths")

    totlen = 0  # total length of all chunks, to estimate sampling time.
    for chs in pathSamples:
        totlen += len(chs.startpoints)
    layerchunks = []
    minz = o.min_z
    layeractivechunks = []
    lastrunchunks = []

    for l in layers:
        layerchunks.append([])
        layeractivechunks.append(CamPathChunkBuilder([]))
        lastrunchunks.append([])
    n = 0

    last_percent = -1
    lastz = minz
    for patternchunk in pathSamples:
        # print (patternchunk.endpoints)
        thisrunchunks = []
        for l in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None
        # threads_count=4
        lastrotation = (0, 0, 0)
        # for t in range(0,threads):
        # print(len(patternchunk.startpoints),len( patternchunk.endpoints))
        spl = len(patternchunk.startpoints)
        # ,startp in enumerate(patternchunk.startpoints):
        for si in range(0, spl):
            # #TODO: seems we are writing into the source chunk ,
            #  and that is why we need to write endpoints everywhere too?

            percent = int(100 * n / totlen)
            if percent != last_percent:
                await progress_async("Sampling Paths", percent)
                last_percent = percent
            n += 1
            sampled = False
            # print(si)

            # get the vector to sample
            startp = Vector(patternchunk.startpoints[si])
            endp = Vector(patternchunk.endpoints[si])
            rotation = patternchunk.rotations[si]
            sweepvect = endp - startp
            sweepvect.normalize()
            # sampling
            if rotation != lastrotation:
                cutter.rotation_euler = rotation
                # cutter.rotation_euler.x=-cutter.rotation_euler.x
                # print(rotation)

                if o.cutter_type == "VCARVE":  # Bullet cone is always pointing Up Z in the object
                    cutter.rotation_euler.x += pi
                cutter.update_tag()
                # this has to be :( it resets the rigidbody world.
                bpy.context.scene.frame_set(1)
                # No other way to update it probably now :(
                # actually 2 frame jumps are needed.
                bpy.context.scene.frame_set(2)
                bpy.context.scene.frame_set(0)

            newsample = get_sample_bullet_n_axis(cutter, startp, endp, rotation, cutterdepth)

            # print('totok',startp,endp,rotation,newsample)
            ################################
            # handling samples
            ############################################
            # this is weird, but will leave it this way now.. just prototyping here.
            if newsample is not None:
                sampled = True
            else:  # TODO: why was this here?
                newsample = startp
                sampled = True
            # print(newsample)

            # elif o.ambient_behaviour=='ALL' and not o.inverse:#handle ambient here
            # newsample=(x,y,minz)
            if sampled:
                for i, l in enumerate(layers):
                    terminatechunk = False
                    ch = layeractivechunks[i]

                    # print(i,l)
                    # print(l[1],l[0])
                    v = startp - newsample
                    distance = -v.length

                    if l[1] <= distance <= l[0]:
                        lastlayer = currentlayer
                        currentlayer = i

                        if (
                            lastsample is not None
                            and lastlayer is not None
                            and currentlayer is not None
                            and lastlayer != currentlayer
                        ):  # sampling for sorted paths in layers-
                            # to go to the border of the sampled layer at least...
                            # there was a bug here, but should be fixed.
                            if currentlayer < lastlayer:
                                growing = True
                                r = range(currentlayer, lastlayer)
                                spliti = 1
                            else:
                                r = range(lastlayer, currentlayer)
                                growing = False
                                spliti = 0
                            # print(r)
                            li = 0

                            for ls in r:
                                splitdistance = layers[ls][1]

                                ratio = (splitdistance - lastdistance) / (distance - lastdistance)
                                # print(ratio)
                                betweensample = lastsample + (newsample - lastsample) * ratio
                                # this probably doesn't work at all!!!! check this algoritm>
                                betweenrotation = tuple_add(
                                    lastrotation,
                                    tuple_multiply(tuple_subtract(rotation, lastrotation), ratio),
                                )
                                # startpoint = retract point, it has to be always available...
                                betweenstartpoint = (
                                    laststartpoint + (startp - laststartpoint) * ratio
                                )
                                # here, we need to have also possible endpoints always..
                                betweenendpoint = lastendpoint + (endp - lastendpoint) * ratio
                                if growing:
                                    if li > 0:
                                        layeractivechunks[ls].points.insert(-1, betweensample)
                                        layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                        layeractivechunks[ls].startpoints.insert(
                                            -1, betweenstartpoint
                                        )
                                        layeractivechunks[ls].endpoints.insert(-1, betweenendpoint)
                                    else:
                                        layeractivechunks[ls].points.append(betweensample)
                                        layeractivechunks[ls].rotations.append(betweenrotation)
                                        layeractivechunks[ls].startpoints.append(betweenstartpoint)
                                        layeractivechunks[ls].endpoints.append(betweenendpoint)
                                    layeractivechunks[ls + 1].points.append(betweensample)
                                    layeractivechunks[ls + 1].rotations.append(betweenrotation)
                                    layeractivechunks[ls + 1].startpoints.append(betweenstartpoint)
                                    layeractivechunks[ls + 1].endpoints.append(betweenendpoint)
                                else:
                                    layeractivechunks[ls].points.insert(-1, betweensample)
                                    layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                    layeractivechunks[ls].startpoints.insert(-1, betweenstartpoint)
                                    layeractivechunks[ls].endpoints.insert(-1, betweenendpoint)

                                    layeractivechunks[ls + 1].points.append(betweensample)
                                    layeractivechunks[ls + 1].rotations.append(betweenrotation)
                                    layeractivechunks[ls + 1].startpoints.append(betweenstartpoint)
                                    layeractivechunks[ls + 1].endpoints.append(betweenendpoint)

                                # layeractivechunks[ls+1].points.insert(0,betweensample)
                                li += 1
                        # this chunk is terminated, and allready in layerchunks /

                        # ch.points.append(betweensample)#
                        ch.points.append(newsample)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)
                        lastdistance = distance

                    elif l[1] > distance:
                        v = sweepvect * l[1]
                        p = startp - v
                        ch.points.append(p)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)
                    elif l[0] < distance:  # retract to original track
                        ch.points.append(startp)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)

            lastsample = newsample
            lastrotation = rotation
            laststartpoint = startp
            lastendpoint = endp

        # convert everything to actual chunks
        # rather than chunkBuilders
        for i, l in enumerate(layers):
            layeractivechunks[i] = (
                layeractivechunks[i].to_chunk() if layeractivechunks[i] is not None else None
            )

        for i, l in enumerate(layers):
            ch = layeractivechunks[i]
            if ch.count() > 0:
                layerchunks[i].append(ch)
                thisrunchunks[i].append(ch)
                layeractivechunks[i] = CamPathChunkBuilder([])

            if o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "OUTLINEFILL":
                parent_child_distance(thisrunchunks[i], lastrunchunks[i], o)

        lastrunchunks = thisrunchunks

    # print(len(layerchunks[i]))

    progress("Checking Relations Between Paths")
    """#this algorithm should also work for n-axis, but now is "sleeping"
    if (o.strategy=='PARALLEL' or o.strategy=='CROSS'):
        if len(layers)>1:# sorting help so that upper layers go first always
            for i in range(0,len(layers)-1):
                #print('layerstuff parenting')
                parentChild(layerchunks[i+1],layerchunks[i],o)
    """
    chunks = []
    for i, l in enumerate(layers):
        chunks.extend(layerchunks[i])

    return chunks


def sample_path_low(o, ch1, ch2, dosample):
    """Generate a sample path between two channels.

    This function computes a series of points that form a path between two
    given channels. It calculates the direction vector from the end of the
    first channel to the start of the second channel and generates points
    along this vector up to a specified distance. If sampling is enabled, it
    modifies the z-coordinate of the generated points based on the cutter
    shape or image sampling, ensuring that the path accounts for any
    obstacles or features in the environment.

    Args:
        o: An object containing optimization parameters and properties related to
            the path generation.
        ch1: The first channel object, which provides a point for the starting
            location of the path.
        ch2: The second channel object, which provides a point for the ending
            location of the path.
        dosample (bool): A flag indicating whether to perform sampling along the generated path.

    Returns:
        CamPathChunk: An object representing the generated path points.
    """

    v1 = Vector(ch1.get_point(-1))
    v2 = Vector(ch2.get_point(0))

    v = v2 - v1
    d = v.length
    v.normalize()

    vref = Vector((0, 0, 0))
    bpath_points = []
    i = 0
    while vref.length < d:
        i += 1
        vref = v * o.distance_along_paths * i
        if vref.length < d:
            p = v1 + vref
            bpath_points.append([p.x, p.y, p.z])
    # print('between path')
    # print(len(bpath))
    pixsize = o.optimisation.pixsize
    if dosample:
        if not (o.optimisation.use_opencamlib and o.optimisation.use_exact):
            if o.optimisation.use_exact:
                if o.update_bullet_collision_tag:
                    prepare_bullet_collision(o)
                    o.update_bullet_collision_tag = False

                cutterdepth = o.cutter_shape.dimensions.z / 2
                for p in bpath_points:
                    z = get_sample_bullet(o.cutter_shape, p[0], p[1], cutterdepth, 1, o.min_z)
                    if z > p[2]:
                        p[2] = z
            else:
                for p in bpath_points:
                    xs = (p[0] - o.min.x) / pixsize + o.borderwidth + pixsize / 2  # -m
                    ys = (p[1] - o.min.y) / pixsize + o.borderwidth + pixsize / 2  # -m
                    z = get_sample_image((xs, ys), o.offset_image, o.min_z) + o.skin
                    if z > p[2]:
                        p[2] = z
    return CamPathChunk(bpath_points)


def polygon_boolean(context, boolean_type):
    """Perform a boolean operation on selected polygons.

    This function takes the active object and applies a specified boolean
    operation (UNION, DIFFERENCE, or INTERSECT) with respect to other
    selected objects in the Blender context. It first converts the polygons
    of the active object and the selected objects into a Shapely
    MultiPolygon. Depending on the boolean type specified, it performs the
    corresponding boolean operation and then converts the result back into a
    Blender curve.

    Args:
        context (bpy.context): The Blender context containing scene and object data.
        boolean_type (str): The type of boolean operation to perform.
            Must be one of 'UNION', 'DIFFERENCE', or 'INTERSECT'.

    Returns:
        dict: A dictionary indicating the operation result, typically {'FINISHED'}.
    """

    bpy.context.scene.cursor.location = (0, 0, 0)
    ob = bpy.context.active_object
    obs = []
    for ob1 in bpy.context.selected_objects:
        if ob1 != ob:
            obs.append(ob1)
    plist = curve_to_shapely(ob)
    p1 = MultiPolygon(plist)
    polys = []
    for o in obs:
        plist = curve_to_shapely(o)
        p2 = MultiPolygon(plist)
        polys.append(p2)
    # print(polys)
    if boolean_type == "UNION":
        for p2 in polys:
            p1 = p1.union(p2)
    elif boolean_type == "DIFFERENCE":
        for p2 in polys:
            p1 = p1.difference(p2)
    elif boolean_type == "INTERSECT":
        for p2 in polys:
            p1 = p1.intersection(p2)

    shapely_to_curve("boolean", p1, ob.location.z)

    return {"FINISHED"}


def polygon_convex_hull(context):
    """Generate the convex hull of a polygon from the given context.

    This function duplicates the current object, joins it, and converts it
    into a 3D mesh. It then extracts the X and Y coordinates of the vertices
    to create a MultiPoint data structure using Shapely. Finally, it
    computes the convex hull of these points and converts the result back
    into a curve named 'ConvexHull'. Temporary objects created during this
    process are deleted to maintain a clean workspace.

    Args:
        context: The context in which the operation is performed, typically
            related to Blender's current state.

    Returns:
        dict: A dictionary indicating the operation's completion status.
    """

    coords = []

    bpy.ops.object.duplicate()
    bpy.ops.object.join()
    bpy.context.object.data.dimensions = "3D"  # force curve to be a 3D curve
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.name = "_tmp"

    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.view_layer.objects.active

    for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
        c = (v.co.x, v.co.y)
        coords.append(c)

    select_multiple("_tmp")  # delete temporary mesh
    select_multiple("ConvexHull")  # delete old hull

    # convert coordinates to shapely MultiPoint datastructure
    points = sgeometry.MultiPoint(coords)

    hull = points.convex_hull
    shapely_to_curve("ConvexHull", hull, 0.0)

    return {"FINISHED"}


# separate function in blender, so you can offset any curve.
# FIXME: same algorithms as the cutout strategy, because that is hierarchy-respecting.
def silhouette_offset(context, offset, style=1, mitrelimit=1.0):
    """Offset the silhouette of a curve or font object in Blender.

    This function takes an active curve or font object in Blender and
    creates an offset silhouette based on the specified parameters. It first
    retrieves the silhouette of the object and then applies a buffer
    operation to create the offset shape. The resulting shape is then
    converted back into a curve object in the Blender scene.

    Args:
        context (bpy.context): The current Blender context.
        offset (float): The distance to offset the silhouette.
        style (int?): The join style for the offset. Defaults to 1.
        mitrelimit (float?): The mitre limit for the offset. Defaults to 1.0.

    Returns:
        dict: A dictionary indicating the operation is finished.
    """

    bpy.context.scene.cursor.location = (0, 0, 0)
    ob = bpy.context.active_object
    if ob.type == "CURVE" or ob.type == "FONT":
        silhs = curve_to_shapely(ob)
    else:
        silhs = get_object_silhouette("OBJECTS", [ob])
    mp = silhs.buffer(offset, cap_style=1, join_style=style, resolution=16, mitre_limit=mitrelimit)
    shapely_to_curve(ob.name + "_offset_" + str(round(offset, 5)), mp, ob.location.z)
    bpy.ops.object.curve_remove_doubles()
    return {"FINISHED"}


def get_object_silhouette(stype, objects=None, use_modifiers=False):
    """Get the silhouette of objects based on the specified type.

    This function computes the silhouette of a given set of objects in
    Blender based on the specified type. It can handle both curves and mesh
    objects, converting curves to polygon format and calculating the
    silhouette for mesh objects. The function also considers the use of
    modifiers if specified. The silhouette is generated by processing the
    geometry of the objects and returning a Shapely representation of the
    silhouette.

    Args:
        stype (str): The type of silhouette to generate ('CURVES' or 'OBJECTS').
        objects (list?): A list of Blender objects to process. Defaults to None.
        use_modifiers (bool?): Whether to apply modifiers to the objects. Defaults to False.

    Returns:
        shapely.geometry.MultiPolygon: The computed silhouette as a Shapely MultiPolygon.
    """

    print("Silhouette Type:", stype)
    if stype == "CURVES":  # curve conversion to polygon format
        allchunks = []
        for ob in objects:
            chunks = curve_to_chunks(ob)
            allchunks.extend(chunks)
        silhouette = chunks_to_shapely(allchunks)

    elif stype == "OBJECTS":
        totfaces = 0
        for ob in objects:
            totfaces += len(ob.data.polygons)

        if (
            totfaces < 20000000
        ):  # boolean polygons method originaly was 20 000 poly limit, now limitless,
            t = time.time()
            print("Shapely Getting Silhouette")
            polys = []
            for ob in objects:
                print("Object:", ob.name)
                if use_modifiers:
                    ob = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
                    m = ob.to_mesh()
                else:
                    m = ob.data
                mw = ob.matrix_world
                mwi = mw.inverted()
                r = ob.rotation_euler
                m.calc_loop_triangles()
                id = 0
                e = 0.000001
                scaleup = 100
                for tri in m.loop_triangles:
                    n = tri.normal.copy()
                    n.rotate(r)

                    if tri.area > 0 and n.z != 0:  # n.z>0.0 and f.area>0.0 :
                        s = []
                        c = mw @ tri.center
                        c = c.xy
                        for vert_index in tri.vertices:
                            v = mw @ m.vertices[vert_index].co
                            s.append((v.x, v.y))
                        if len(s) > 2:
                            # print(s)
                            p = spolygon.Polygon(s)
                            # print(dir(p))
                            if p.is_valid:
                                # polys.append(p)
                                polys.append(p.buffer(e, resolution=0))
                        id += 1
            ob.select_set(False)
            if totfaces < 20000:
                p = sops.unary_union(polys)
            else:
                print("Computing in Parts")
                bigshapes = []
                i = 1
                part = 20000
                while i * part < totfaces:
                    print(i)
                    ar = polys[(i - 1) * part : i * part]
                    bigshapes.append(sops.unary_union(ar))
                    i += 1
                if (i - 1) * part < totfaces:
                    last_ar = polys[(i - 1) * part :]
                    bigshapes.append(sops.unary_union(last_ar))
                print("Joining")
                p = sops.unary_union(bigshapes)

            print("Time:", time.time() - t)

            t = time.time()
            silhouette = shapely_to_multipolygon(p)  # [polygon_utils_cam.Shapely2Polygon(p)]

    return silhouette


def get_operation_silhouette(operation):
    """Gets the silhouette for the given operation.

    This function determines the silhouette of an operation using image
    thresholding techniques. It handles different geometry sources, such as
    objects or images, and applies specific methods based on the type of
    geometry. If the geometry source is 'OBJECT' or 'COLLECTION', it checks
    whether to process curves or not. The function also considers the number
    of faces in mesh objects to decide on the appropriate method for
    silhouette extraction.

    Args:
        operation (Operation): An object containing the necessary data

    Returns:
        Silhouette: The computed silhouette for the operation.
    """
    if operation.update_silhouette_tag:
        image = None
        objects = None
        if operation.geometry_source == "OBJECT" or operation.geometry_source == "COLLECTION":
            if not operation.onlycurves:
                stype = "OBJECTS"
            else:
                stype = "CURVES"
        else:
            stype = "IMAGE"

        totfaces = 0
        if stype == "OBJECTS":
            for ob in operation.objects:
                if ob.type == "MESH":
                    totfaces += len(ob.data.polygons)

        if (stype == "OBJECTS" and totfaces > 200000) or stype == "IMAGE":
            print("Image Method")
            samples = render_sample_image(operation)
            if stype == "OBJECTS":
                i = samples > operation.min_z - 0.0000001
                # np.min(operation.zbuffer_image)-0.0000001#
                # #the small number solves issue with totally flat meshes, which people tend to mill instead of
                # proper pockets. then the minimum was also maximum, and it didn't detect contour.
            else:
                # this fixes another numeric imprecision.
                i = samples > np.min(operation.zbuffer_image)

            chunks = image_to_chunks(operation, i)
            operation.silhouette = chunks_to_shapely(chunks)
        # print(operation.silhouette)
        # this conversion happens because we need the silh to be oriented, for milling directions.
        else:
            print("Object Method for Retrieving Silhouette")
            operation.silhouette = get_object_silhouette(
                stype, objects=operation.objects, use_modifiers=operation.use_modifiers
            )

        operation.update_silhouette_tag = False
    return operation.silhouette


def get_object_outline(radius, o, Offset):
    """Get the outline of a geometric object based on specified parameters.

    This function generates an outline for a given geometric object by
    applying a buffer operation to its polygons. The buffer radius can be
    adjusted based on the `radius` parameter, and the operation can be
    offset based on the `Offset` flag. The function also considers whether
    the polygons should be merged or not, depending on the properties of the
    object `o`.

    Args:
        radius (float): The radius for the buffer operation.
        o (object): An object containing properties that influence the outline generation.
        Offset (bool): A flag indicating whether to apply a positive or negative offset.

    Returns:
        MultiPolygon: The resulting outline of the geometric object as a MultiPolygon.
    """
    # FIXME: make this one operation independent
    # circle detail, optimize, optimize thresold.

    polygons = get_operation_silhouette(o)

    i = 0
    # print('offseting polygons')

    if Offset:
        offset = 1
    else:
        offset = -1

    outlines = []
    i = 0
    if o.straight:
        join = 2
    else:
        join = 1

    if isinstance(polygons, list):
        polygon_list = polygons
    else:
        polygon_list = polygons.geoms

    for p1 in polygon_list:  # sort by size before this???
        # print(p1.type, len(polygons))
        i += 1
        if radius > 0:
            p1 = p1.buffer(
                radius * offset,
                resolution=o.optimisation.circle_detail,
                join_style=join,
                mitre_limit=2,
            )
        outlines.append(p1)

    # print(outlines)
    if o.dont_merge:
        outline = sgeometry.MultiPolygon(outlines)
    else:
        outline = shapely.ops.unary_union(outlines)
    return outline


def get_ambient(o):
    """Calculate and update the ambient geometry based on the provided object.

    This function computes the ambient shape for a given object based on its
    properties, such as cutter restrictions and ambient behavior. It
    determines the appropriate radius and creates the ambient geometry
    either from the silhouette or as a polygon defined by the object's
    minimum and maximum coordinates. If a limit curve is specified, it will
    also intersect the ambient shape with the limit polygon.

    Args:
        o (object): An object containing properties that define the ambient behavior,
            cutter restrictions, and limit curve.

    Returns:
        None: The function updates the ambient property of the object in place.
    """

    if o.update_ambient_tag:
        if o.ambient_cutter_restrict:  # cutter stays in ambient & limit curve
            m = o.cutter_diameter / 2
        else:
            m = 0

        if o.ambient_behaviour == "AROUND":
            r = o.ambient_radius - m
            # in this method we need ambient from silhouette
            o.ambient = get_object_outline(r, o, True)
        else:
            o.ambient = spolygon.Polygon(
                (
                    (o.min.x + m, o.min.y + m),
                    (o.min.x + m, o.max.y - m),
                    (o.max.x - m, o.max.y - m),
                    (o.max.x - m, o.min.y + m),
                )
            )

        if o.use_limit_curve:
            if o.limit_curve != "":
                limit_curve = bpy.data.objects[o.limit_curve]
                polys = curve_to_shapely(limit_curve)
                o.limit_poly = shapely.ops.unary_union(polys)

                if o.ambient_cutter_restrict:
                    o.limit_poly = o.limit_poly.buffer(
                        o.cutter_diameter / 2, resolution=o.optimisation.circle_detail
                    )
            o.ambient = o.ambient.intersection(o.limit_poly)
    o.update_ambient_tag = False


# samples in both modes now - image and bullet collision too.
async def sample_chunks(o, pathSamples, layers):
    """Sample chunks of paths based on the provided parameters.

    This function processes the given path samples and layers to generate
    chunks of points that represent the sampled paths. It takes into account
    various optimization settings and strategies to determine how the points
    are sampled and organized into layers. The function handles different
    scenarios based on the object's properties and the specified layers,
    ensuring that the resulting chunks are correctly structured for further
    processing.

    Args:
        o (object): An object containing various properties and settings
            related to the sampling process.
        pathSamples (list): A list of path samples to be processed.
        layers (list): A list of layers defining the z-coordinate ranges
            for sampling.

    Returns:
        list: A list of sampled chunks, each containing points that represent
            the sampled paths.
    """

    #
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    get_ambient(o)

    if o.optimisation.use_exact:  # prepare collision world
        if o.optimisation.use_opencamlib:
            await oclSample(o, pathSamples)
            cutterdepth = 0
        else:
            if o.update_bullet_collision_tag:
                prepare_bullet_collision(o)

                o.update_bullet_collision_tag = False
            # print (o.ambient)
            cutter = o.cutter_shape
            cutterdepth = cutter.dimensions.z / 2
    else:
        # or prepare offset image, but not in some strategies.
        if o.strategy != "WATERLINE":
            await prepare_area(o)

        pixsize = o.optimisation.pixsize

        coordoffset = o.borderwidth + pixsize / 2  # -m

        res = ceil(o.cutter_diameter / o.optimisation.pixsize)
        m = res / 2

    t = time.time()
    # print('sampling paths')

    totlen = 0  # total length of all chunks, to estimate sampling time.
    for ch in pathSamples:
        totlen += ch.count()
    layerchunks = []
    minz = o.min_z - 0.000001  # correction for image method problems
    layeractivechunks = []
    lastrunchunks = []

    for l in layers:
        layerchunks.append([])
        layeractivechunks.append(CamPathChunkBuilder([]))
        lastrunchunks.append([])

    zinvert = 0
    if o.inverse:
        ob = bpy.data.objects[o.object_name]
        zinvert = ob.location.z + maxz  # ob.bound_box[6][2]

    print(f"Total Sample Points {totlen}")

    n = 0
    last_percent = -1
    # timing for optimisation
    samplingtime = timing_init()
    sortingtime = timing_init()
    totaltime = timing_init()
    timing_start(totaltime)
    lastz = minz
    for patternchunk in pathSamples:
        thisrunchunks = []
        for l in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None
        # threads_count=4

        # for t in range(0,threads):
        our_points = patternchunk.get_points_np()
        ambient_contains = shapely.contains(o.ambient, shapely.points(our_points[:, 0:2]))
        for s, in_ambient in zip(our_points, ambient_contains):
            if o.strategy != "WATERLINE" and int(100 * n / totlen) != last_percent:
                last_percent = int(100 * n / totlen)
                await progress_async("Sampling Paths", last_percent)
            n += 1
            x = s[0]
            y = s[1]
            if not in_ambient:
                newsample = (x, y, 1)
            else:
                if o.optimisation.use_opencamlib and o.optimisation.use_exact:
                    z = s[2]
                    if minz > z:
                        z = minz
                    newsample = (x, y, z)
                # ampling
                elif o.optimisation.use_exact and not o.optimisation.use_opencamlib:
                    if lastsample is not None:  # this is an optimalization,
                        # search only for near depths to the last sample. Saves about 30% of sampling time.
                        z = get_sample_bullet(
                            cutter, x, y, cutterdepth, 1, lastsample[2] - o.distance_along_paths
                        )  # first try to the last sample
                        if z < minz - 1:
                            z = get_sample_bullet(
                                cutter,
                                x,
                                y,
                                cutterdepth,
                                lastsample[2] - o.distance_along_paths,
                                minz,
                            )
                    else:
                        z = get_sample_bullet(cutter, x, y, cutterdepth, 1, minz)

                # print(z)
                else:
                    timing_start(samplingtime)
                    xs = (x - minx) / pixsize + coordoffset
                    ys = (y - miny) / pixsize + coordoffset
                    timing_add(samplingtime)
                    z = get_sample_image((xs, ys), o.offset_image, minz) + o.skin

                ################################
                # handling samples
                ############################################

                if minz > z:
                    z = minz
                newsample = (x, y, z)

            for i, l in enumerate(layers):
                terminatechunk = False

                ch = layeractivechunks[i]

                if l[1] <= newsample[2] <= l[0]:
                    lastlayer = None  # rather the last sample here ? has to be set to None,
                    # since sometimes lastsample vs lastlayer didn't fit and did ugly ugly stuff....
                    if lastsample is not None:
                        for i2, l2 in enumerate(layers):
                            if l2[1] <= lastsample[2] <= l2[0]:
                                lastlayer = i2

                    currentlayer = i
                    # and lastsample[2]!=newsample[2]:
                    if lastlayer is not None and lastlayer != currentlayer:
                        # #sampling for sorted paths in layers- to go to the border of the sampled layer at least...
                        # there was a bug here, but should be fixed.
                        if currentlayer < lastlayer:
                            growing = True
                            r = range(currentlayer, lastlayer)
                            spliti = 1
                        else:
                            r = range(lastlayer, currentlayer)
                            growing = False
                            spliti = 0
                        # print(r)
                        li = 0
                        for ls in r:
                            splitz = layers[ls][1]
                            # print(ls)

                            v1 = lastsample
                            v2 = newsample
                            if o.movement.protect_vertical:
                                v1, v2 = is_vertical_limit(
                                    v1, v2, o.movement.protect_vertical_limit
                                )
                            v1 = Vector(v1)
                            v2 = Vector(v2)
                            # print(v1,v2)
                            ratio = (splitz - v1.z) / (v2.z - v1.z)
                            # print(ratio)
                            betweensample = v1 + (v2 - v1) * ratio

                            # ch.points.append(betweensample.to_tuple())

                            if growing:
                                if li > 0:
                                    layeractivechunks[ls].points.insert(
                                        -1, betweensample.to_tuple()
                                    )
                                else:
                                    layeractivechunks[ls].points.append(betweensample.to_tuple())
                                layeractivechunks[ls + 1].points.append(betweensample.to_tuple())
                            else:
                                # print(v1,v2,betweensample,lastlayer,currentlayer)
                                layeractivechunks[ls].points.insert(-1, betweensample.to_tuple())
                                layeractivechunks[ls + 1].points.insert(0, betweensample.to_tuple())

                            li += 1
                    # this chunk is terminated, and allready in layerchunks /

                    # ch.points.append(betweensample.to_tuple())#
                    ch.points.append(newsample)
                elif l[1] > newsample[2]:
                    ch.points.append((newsample[0], newsample[1], l[1]))
                elif l[0] < newsample[2]:  # terminate chunk
                    terminatechunk = True

                if terminatechunk:
                    if len(ch.points) > 0:
                        as_chunk = ch.to_chunk()
                        layerchunks[i].append(as_chunk)
                        thisrunchunks[i].append(as_chunk)
                        layeractivechunks[i] = CamPathChunkBuilder([])
            lastsample = newsample

        for i, l in enumerate(layers):
            ch = layeractivechunks[i]
            if len(ch.points) > 0:
                as_chunk = ch.to_chunk()
                layerchunks[i].append(as_chunk)
                thisrunchunks[i].append(as_chunk)
                layeractivechunks[i] = CamPathChunkBuilder([])

            # PARENTING
            if o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "OUTLINEFILL":
                timing_start(sortingtime)
                parent_child_distance(thisrunchunks[i], lastrunchunks[i], o)
                timing_add(sortingtime)

        lastrunchunks = thisrunchunks

    # print(len(layerchunks[i]))
    progress("Checking Relations Between Paths")
    timing_start(sortingtime)

    if o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "OUTLINEFILL":
        if len(layers) > 1:  # sorting help so that upper layers go first always
            for i in range(0, len(layers) - 1):
                parents = []
                children = []
                # only pick chunks that should have connectivity assigned - 'last' and 'first' ones of the layer.
                for ch in layerchunks[i + 1]:
                    if not ch.children:
                        parents.append(ch)
                for ch1 in layerchunks[i]:
                    if not ch1.parents:
                        children.append(ch1)

                # parent only last and first chunk, before it did this for all.
                parent_child(parents, children, o)
    timing_add(sortingtime)
    chunks = []

    for i, l in enumerate(layers):
        if o.movement.ramp:
            for ch in layerchunks[i]:
                ch.zstart = layers[i][0]
                ch.zend = layers[i][1]
        chunks.extend(layerchunks[i])
    timing_add(totaltime)
    print(samplingtime)
    print(sortingtime)
    print(totaltime)
    return chunks


async def connect_chunks_low(chunks, o):
    """Connects chunks that are close to each other without lifting, sampling
    them 'low'.

    This function processes a list of chunks and connects those that are
    within a specified distance based on the provided options. It takes into
    account various strategies for connecting the chunks, including 'CARVE',
    'PENCIL', and 'MEDIAL_AXIS', and adjusts the merging distance
    accordingly. The function also handles specific movement settings, such
    as whether to stay low or to merge distances, and may resample chunks if
    certain optimization conditions are met.

    Args:
        chunks (list): A list of chunk objects to be connected.
        o (object): An options object containing movement and strategy parameters.

    Returns:
        list: A list of connected chunk objects.
    """
    if not o.movement.stay_low or (o.strategy == "CARVE" and o.carve_depth > 0):
        return chunks

    connectedchunks = []
    chunks_to_resample = []  # for OpenCAMLib sampling
    mergedist = 3 * o.distance_between_paths
    if (
        o.strategy == "PENCIL"
    ):  # this is bigger for pencil path since it goes on the surface to clean up the rests,
        # and can go to close points on the surface without fear of going deep into material.
        mergedist = 10 * o.distance_between_paths

    if o.strategy == "MEDIAL_AXIS":
        mergedist = 1 * o.medial_axis_subdivision

    if o.movement.parallel_step_back:
        mergedist *= 2

    if o.movement.merge_distance > 0:
        mergedist = o.movement.merge_distance
    # mergedist=10
    lastch = None
    i = len(chunks)
    pos = (0, 0, 0)

    for ch in chunks:
        if ch.count() > 0:
            if lastch is not None and (ch.distance_start(pos, o) < mergedist):
                # CARVE should lift allways, when it goes below surface...
                # print(mergedist,ch.distance(pos,o))
                if o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "PENCIL":
                    # for these paths sorting happens after sampling, thats why they need resample the connection
                    between = sample_path_low(o, lastch, ch, True)
                else:
                    # print('addbetwee')
                    between = sample_path_low(
                        o, lastch, ch, False
                    )  # other paths either dont use sampling or are sorted before it.
                if (
                    o.optimisation.use_opencamlib
                    and o.optimisation.use_exact
                    and (
                        o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "PENCIL"
                    )
                ):
                    chunks_to_resample.append(
                        (connectedchunks[-1], connectedchunks[-1].count(), between.count())
                    )

                connectedchunks[-1].extend(between.get_points_np())
                connectedchunks[-1].extend(ch.get_points_np())
            else:
                connectedchunks.append(ch)
            lastch = ch
            pos = lastch.get_point(-1)

    if (
        o.optimisation.use_opencamlib
        and o.optimisation.use_exact
        and o.strategy != "CUTOUT"
        and o.strategy != "POCKET"
        and o.strategy != "WATERLINE"
    ):
        await oclResampleChunks(o, chunks_to_resample, use_cached_mesh=True)

    return connectedchunks


async def sort_chunks(chunks, o, last_pos=None):
    """Sort a list of chunks based on a specified strategy.

    This function sorts a list of chunks according to the provided options
    and the current position. It utilizes a recursive approach to find the
    closest chunk to the current position and adapts its distance if it has
    not been sorted before. The function also handles progress updates
    asynchronously and adjusts the recursion limit to accommodate deep
    recursion scenarios.

    Args:
        chunks (list): A list of chunk objects to be sorted.
        o (object): An options object that contains sorting strategy and other parameters.
        last_pos (tuple?): The last known position as a tuple of coordinates.
            Defaults to None, which initializes the position to (0, 0, 0).

    Returns:
        list: A sorted list of chunk objects.
    """

    if o.strategy != "WATERLINE":
        await progress_async("Sorting Paths")
    # the getNext() function of CamPathChunk was running out of recursion limits.
    sys.setrecursionlimit(100000)
    sortedchunks = []
    chunks_to_resample = []

    lastch = None
    last_progress_time = time.time()
    total = len(chunks)
    i = len(chunks)
    pos = (0, 0, 0) if last_pos is None else last_pos
    while len(chunks) > 0:
        if o.strategy != "WATERLINE" and time.time() - last_progress_time > 0.1:
            await progress_async("Sorting Paths", 100.0 * (total - len(chunks)) / total)
            last_progress_time = time.time()
        ch = None
        if (
            len(sortedchunks) == 0 or len(lastch.parents) == 0
        ):  # first chunk or when there are no parents -> parents come after children here...
            ch = get_closest_chunk(o, pos, chunks)
        elif len(lastch.parents) > 0:  # looks in parents for next candidate, recursively
            for parent in lastch.parents:
                ch = parent.get_next_closest(o, pos)
                if ch is not None:
                    break
            if ch is None:
                ch = get_closest_chunk(o, pos, chunks)

        if ch is not None:  # found next chunk, append it to list
            # only adaptdist the chunk if it has not been sorted before
            if not ch.sorted:
                ch.adapt_distance(pos, o)
                ch.sorted = True
            # print(len(ch.parents),'children')
            chunks.remove(ch)
            sortedchunks.append(ch)
            lastch = ch
            pos = lastch.get_point(-1)
        # print(i, len(chunks))
        # experimental fix for infinite loop problem
        # else:
        # THIS PROBLEM WASN'T HERE AT ALL. but keeping it here, it might fix the problems somwhere else:)
        # can't find chunks close enough and still some chunks left
        # to be sorted. For now just move the remaining chunks over to
        # the sorted list.
        # This fixes an infinite loop condition that occurs sometimes.
        # This is a bandaid fix: need to find the root cause of this problem
        # suspect it has to do with the sorted flag?
        # print("no chunks found closest. Chunks not sorted: ", len(chunks))
        # sortedchunks.extend(chunks)
        # chunks[:] = []

        i -= 1
    if o.strategy == "POCKET" and o.pocket_option == "OUTSIDE":
        sortedchunks.reverse()

    sys.setrecursionlimit(1000)
    if o.strategy != "DRILL" and o.strategy != "OUTLINEFILL":
        # THIS SHOULD AVOID ACTUALLY MOST STRATEGIES, THIS SHOULD BE DONE MANUALLY,
        # BECAUSE SOME STRATEGIES GET SORTED TWICE.
        sortedchunks = await connect_chunks_low(sortedchunks, o)
    return sortedchunks


async def oclResampleChunks(operation, chunks_to_resample, use_cached_mesh):
    """Resample chunks of data using OpenCL operations.

    This function takes a list of chunks to resample and performs an OpenCL
    sampling operation on them. It first prepares a temporary chunk that
    collects points from the specified chunks. Then, it calls the
    `ocl_sample` function to perform the sampling operation. After obtaining
    the samples, it updates the z-coordinates of the points in each chunk
    based on the sampled values.

    Args:
        operation (OperationType): The OpenCL operation to be performed.
        chunks_to_resample (list): A list of tuples, where each tuple contains
            a chunk object and its corresponding start index and length for
            resampling.
        use_cached_mesh (bool): A flag indicating whether to use cached mesh
            data during the sampling process.

    Returns:
        None: This function does not return a value but modifies the input
            chunks in place.
    """

    tmp_chunks = list()
    tmp_chunks.append(CamPathChunk(inpoints=[]))
    for chunk, i_start, i_length in chunks_to_resample:
        tmp_chunks[0].extend(chunk.get_points_np()[i_start : i_start + i_length])
        print(i_start, i_length, len(tmp_chunks[0].points))

    samples = await ocl_sample(operation, tmp_chunks, use_cached_mesh=use_cached_mesh)

    sample_index = 0
    for chunk, i_start, i_length in chunks_to_resample:
        z = np.array([p.z for p in samples[sample_index : sample_index + i_length]]) / OCL_SCALE
        pts = chunk.get_points_np()
        pt_z = pts[i_start : i_start + i_length, 2]
        pt_z = np.where(z > pt_z, z, pt_z)

        sample_index += i_length


async def oclGetWaterline(operation, chunks):
    """Generate waterline paths for a given machining operation.

    This function calculates the waterline paths based on the provided
    machining operation and its parameters. It determines the appropriate
    cutter type and dimensions, sets up the waterline object with the
    corresponding STL file, and processes each layer to generate the
    machining paths. The resulting paths are stored in the provided chunks
    list. The function also handles different cutter types, including end
    mills, ball nose cutters, and V-carve cutters.

    Args:
        operation (Operation): An object representing the machining operation,
            containing details such as cutter type, diameter, and minimum Z height.
        chunks (list): A list that will be populated with the generated
            machining path chunks.
    """

    layers = oclWaterlineLayerHeights(operation)
    oclSTL = get_oclSTL(operation)

    op_cutter_type = operation.cutter_type
    op_cutter_diameter = operation.cutter_diameter
    op_minz = operation.min_z
    if op_cutter_type == "VCARVE":
        op_cutter_tip_angle = operation["cutter_tip_angle"]

    cutter = None
    # TODO: automatically determine necessary cutter length depending on object size
    cutter_length = 150

    if op_cutter_type == "END":
        cutter = ocl.CylCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == "BALLNOSE":
        cutter = ocl.BallCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == "VCARVE":
        cutter = ocl.ConeCutter(
            (op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle, cutter_length
        )
    else:
        print("Cutter Unsupported: {0}\n".format(op_cutter_type))
        quit()

    waterline = ocl.Waterline()
    waterline.setSTL(oclSTL)
    waterline.setCutter(cutter)
    waterline.setSampling(0.1)  # TODO: add sampling setting to UI
    last_pos = [0, 0, 0]
    for count, height in enumerate(layers):
        layer_chunks = []
        await progress_async("Waterline", int((100 * count) / len(layers)))
        waterline.reset()
        waterline.setZ(height * OCL_SCALE)
        waterline.run2()
        wl_loops = waterline.getLoops()
        for l in wl_loops:
            inpoints = []
            for p in l:
                inpoints.append((p.x / OCL_SCALE, p.y / OCL_SCALE, p.z / OCL_SCALE))
            inpoints.append(inpoints[0])
            chunk = CamPathChunk(inpoints=inpoints)
            chunk.closed = True
            layer_chunks.append(chunk)
        # sort chunks so that ordering is stable
        chunks.extend(await sort_chunks(layer_chunks, operation, last_pos=last_pos))
        if len(chunks) > 0:
            last_pos = chunks[-1].get_point(-1)


# search edges for pencil strategy, another try.
def image_edge_search_on_line(o, ar, zimage):
    """Search for edges in an image using a pencil strategy.

    This function implements an edge detection algorithm that simulates a
    pencil-like movement across the image represented by a 2D array. It
    identifies white pixels and builds chunks of points based on the
    detected edges. The algorithm iteratively explores possible directions
    to find and track the edges until a specified condition is met, such as
    exhausting the available white pixels or reaching a maximum number of
    tests.

    Args:
        o (object): An object containing parameters such as min, max coordinates, cutter
            diameter,
            border width, and optimisation settings.
        ar (np.ndarray): A 2D array representing the image where edge detection is to be
            performed.
        zimage (np.ndarray): A 2D array representing the z-coordinates corresponding to the image.

    Returns:
        list: A list of chunks representing the detected edges in the image.
    """

    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    r = ceil((o.cutter_diameter / 12) / o.optimisation.pixsize)  # was commented
    coef = 0.75
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    directions = ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))

    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()
    totpix = startpix
    chunk_builders = []
    xs = indices[0][0]
    ys = indices[1][0]
    nchunk = CamPathChunkBuilder([(xs, ys, zimage[xs, ys])])  # startposition
    dindex = 0  # index in the directions list
    last_direction = directions[dindex]
    test_direction = directions[dindex]
    i = 0
    perc = 0
    itests = 0
    totaltests = 0
    maxtotaltests = startpix * 4

    ar[xs, ys] = False

    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end
        if perc != int(100 - 100 * totpix / startpix):
            perc = int(100 - 100 * totpix / startpix)
            progress("Pencil Path Searching", perc)
        # progress('simulation ',int(100*i/l))
        success = False
        testangulardistance = 0  # distance from initial direction in the list of direction
        testleftright = False  # test both sides from last vector
        while not success:
            xs = nchunk.points[-1][0] + test_direction[0]
            ys = nchunk.points[-1][1] + test_direction[1]

            if xs > r and xs < ar.shape[0] - r and ys > r and ys < ar.shape[1] - r:
                test = ar[xs, ys]
                # print(test)
                if test:
                    success = True
            if success:
                nchunk.points.append([xs, ys, zimage[xs, ys]])
                last_direction = test_direction
                ar[xs, ys] = False
                if 0:
                    print("Success")
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(itests)
            else:
                # nappend([xs,ys])#for debugging purpose
                # ar.shape[0]
                test_direction = last_direction
                if testleftright:
                    testangulardistance = -testangulardistance
                    testleftright = False
                else:
                    testangulardistance = -testangulardistance
                    testangulardistance += 1  # increment angle
                    testleftright = True

                if abs(testangulardistance) > 6:  # /testlength
                    testangulardistance = 0
                    indices = ar.nonzero()
                    totpix = len(indices[0])
                    chunk_builders.append(nchunk)
                    if len(indices[0] > 0):
                        xs = indices[0][0]
                        ys = indices[1][0]
                        nchunk = CamPathChunkBuilder([(xs, ys, zimage[xs, ys])])  # startposition

                        ar[xs, ys] = False
                    else:
                        nchunk = CamPathChunkBuilder([])

                    test_direction = directions[3]
                    last_direction = directions[3]
                    success = True
                    itests = 0
                # print('reset')
                if len(nchunk.points) > 0:
                    if nchunk.points[-1][0] + test_direction[0] < r:
                        testvect.x = r
                    if nchunk.points[-1][1] + test_direction[1] < r:
                        testvect.y = r
                    if nchunk.points[-1][0] + test_direction[0] > maxarx - r:
                        testvect.x = maxarx - r
                    if nchunk.points[-1][1] + test_direction[1] > maxary - r:
                        testvect.y = maxary - r

                dindexmod = dindex + testangulardistance
                while dindexmod < 0:
                    dindexmod += len(directions)
                while dindexmod > len(directions):
                    dindexmod -= len(directions)

                test_direction = directions[dindexmod]
                if 0:
                    print(xs, ys, test_direction, last_direction, testangulardistance)
                    print(totpix)
            itests += 1
            totaltests += 1

        i += 1
        if i % 100 == 0:
            # print('100 succesfull tests done')
            totpix = ar.sum()
            # print(totpix)
            # print(totaltests)
            i = 0
    chunk_builders.append(nchunk)
    for ch in chunk_builders:
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = (
                (ch[i][0] + coef - o.borderwidth) * o.optimisation.pixsize + minx,
                (ch[i][1] + coef - o.borderwidth) * o.optimisation.pixsize + miny,
                ch[i][2],
            )
    return [c.to_chunk() for c in chunk_builders]


def get_offset_image_cavities(o, i):  # for pencil operation mainly
    """Detects areas in the offset image which are 'cavities' due to curvature
    changes.

    This function analyzes the input image to identify regions where the
    curvature changes, indicating the presence of cavities. It computes
    vertical and horizontal differences in pixel values to detect edges and
    applies a threshold to filter out insignificant changes. The resulting
    areas are then processed to remove any chunks that do not meet the
    minimum criteria for cavity detection. The function returns a list of
    valid chunks that represent the detected cavities.

    Args:
        o: An object containing parameters and thresholds for the detection
            process.
        i (np.ndarray): A 2D array representing the image data to be analyzed.

    Returns:
        list: A list of detected chunks representing the cavities in the image.
    """
    # i=np.logical_xor(lastislice , islice)
    progress("Detect Corners in the Offset Image")
    vertical = i[:-2, 1:-1] - i[1:-1, 1:-1] - o.pencil_threshold > i[1:-1, 1:-1] - i[2:, 1:-1]
    horizontal = i[1:-1, :-2] - i[1:-1, 1:-1] - o.pencil_threshold > i[1:-1, 1:-1] - i[1:-1, 2:]
    # if bpy.app.debug_value==2:

    ar = np.logical_or(vertical, horizontal)

    if 1:  # this is newer strategy, finds edges nicely, but pff.going exacty on edge,
        # it has tons of spikes and simply is not better than the old one
        iname = get_cache_path(o) + "_pencilthres.exr"
        # numpysave(ar,iname)#save for comparison before
        chunks = image_edge_search_on_line(o, ar, i)
        iname = get_cache_path(o) + "_pencilthres_comp.exr"
        print("New Pencil Strategy")

    # ##crop pixels that are on outer borders
    for chi in range(len(chunks) - 1, -1, -1):
        chunk = chunks[chi]
        chunk.clip_points(o.min.x, o.max.x, o.min.y, o.max.y)
        # for si in range(len(points) - 1, -1, -1):
        #     if not (o.min.x < points[si][0] < o.max.x and o.min.y < points[si][1] < o.max.y):
        #         points.pop(si)
        if chunk.count() < 2:
            chunks.pop(chi)

    return chunks


def crazy_stroke_image(o):
    """Generate a toolpath for a milling operation using a crazy stroke
    strategy.

    This function computes a path for a milling cutter based on the provided
    parameters and the offset image. It utilizes a circular cutter
    representation and evaluates potential cutting positions based on
    various thresholds. The algorithm iteratively tests different angles and
    lengths for the cutter's movement until the desired cutting area is
    achieved or the maximum number of tests is reached.

    Args:
        o (object): An object containing parameters such as cutter diameter,
            optimization settings, movement type, and thresholds for
            determining cutting effectiveness.

    Returns:
        list: A list of chunks representing the computed toolpath for the milling
            operation.
    """

    # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    # ceil((o.cutter_diameter/12)/o.optimisation.pixsize)
    r = int((o.cutter_diameter / 2.0) / o.optimisation.pixsize)
    d = 2 * r
    coef = 0.75

    ar = o.offset_image.copy()
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = get_circle_binary(r)
    cutterArrayNegative = -cutterArray

    cutterimagepix = cutterArray.sum()
    # a threshold which says if it is valuable to cut in a direction
    satisfypix = cutterimagepix * o.crazy_threshold_1
    toomuchpix = cutterimagepix * o.crazy_threshold_2
    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()  #
    totpix = startpix
    chunk_builders = []
    xs = indices[0][0] - r
    if xs < r:
        xs = r
    ys = indices[1][0] - r
    if ys < r:
        ys = r
    nchunk = CamPathChunkBuilder([(xs, ys)])  # startposition
    print(indices)
    print(indices[0][0], indices[1][0])
    # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    lastvect = Vector((r, 0, 0))
    # multiply *2 not to get values <1 pixel
    testvect = lastvect.normalized() * r / 2.0
    rot = Euler((0, 0, 1))
    i = 0
    perc = 0
    itests = 0
    totaltests = 0
    maxtests = 500
    maxtotaltests = 1000000

    print(xs, ys, indices[0][0], indices[1][0], r)
    ar[xs - r : xs - r + d, ys - r : ys - r + d] = (
        ar[xs - r : xs - r + d, ys - r : ys - r + d] * cutterArrayNegative
    )
    # range for angle of toolpath vector versus material vector
    anglerange = [-pi, pi]
    testangleinit = 0
    angleincrement = 0.05
    if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW") or (
        o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW"
    ):
        anglerange = [-pi, 0]
        testangleinit = 1
        angleincrement = -angleincrement
    elif (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW") or (
        o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW"
    ):
        anglerange = [0, pi]
        testangleinit = -1
        angleincrement = angleincrement
    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end
        success = False
        # define a vector which gets varied throughout the testing, growing and growing angle to sides.
        testangle = testangleinit
        testleftright = False
        testlength = r

        while not success:
            xs = nchunk.points[-1][0] + int(testvect.x)
            ys = nchunk.points[-1][1] + int(testvect.y)
            if xs > r + 1 and xs < ar.shape[0] - r - 1 and ys > r + 1 and ys < ar.shape[1] - r - 1:
                testar = ar[xs - r : xs - r + d, ys - r : ys - r + d] * cutterArray
                if 0:
                    print("Test")
                    print(testar.sum(), satisfypix)
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(totpix)

                eatpix = testar.sum()
                cindices = testar.nonzero()
                cx = cindices[0].sum() / eatpix
                cy = cindices[1].sum() / eatpix
                v = Vector((cx - r, cy - r))
                angle = testvect.to_2d().angle_signed(v)
                # this could be righthanded milling? lets see :)
                if anglerange[0] < angle < anglerange[1]:
                    if toomuchpix > eatpix > satisfypix:
                        success = True
            if success:
                nchunk.points.append([xs, ys])
                lastvect = testvect
                ar[xs - r : xs - r + d, ys - r : ys - r + d] = ar[
                    xs - r : xs - r + d, ys - r : ys - r + d
                ] * (-cutterArray)
                totpix -= eatpix
                itests = 0
                if 0:
                    print("Success")
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(itests)
            else:
                # TODO: after all angles were tested into material higher than toomuchpix, it should cancel,
                #  otherwise there is no problem with long travel in free space.....
                # TODO:the testing should start not from the same angle as lastvector, but more towards material.
                #  So values closer to toomuchpix are obtained rather than satisfypix
                testvect = lastvect.normalized() * testlength
                right = True
                if testangleinit == 0:  # meander
                    if testleftright:
                        testangle = -testangle
                        testleftright = False
                    else:
                        testangle = abs(testangle) + angleincrement  # increment angle
                        testleftright = True
                else:  # climb/conv.
                    testangle += angleincrement

                if abs(testangle) > o.crazy_threshold_3:  # /testlength
                    testangle = testangleinit
                    testlength += r / 4.0
                if nchunk.points[-1][0] + testvect.x < r:
                    testvect.x = r
                if nchunk.points[-1][1] + testvect.y < r:
                    testvect.y = r
                if nchunk.points[-1][0] + testvect.x > maxarx - r:
                    testvect.x = maxarx - r
                if nchunk.points[-1][1] + testvect.y > maxary - r:
                    testvect.y = maxary - r

                rot.z = testangle

                testvect.rotate(rot)
                # if 0:
                #     print(xs, ys, testlength, testangle)
                #     print(lastvect)
                #     print(testvect)
                #     print(totpix)
            itests += 1
            totaltests += 1

            if itests > maxtests or testlength > r * 1.5:
                # print('resetting location')
                indices = ar.nonzero()
                chunk_builders.append(nchunk)
                if len(indices[0]) > 0:
                    xs = indices[0][0] - r
                    if xs < r:
                        xs = r
                    ys = indices[1][0] - r
                    if ys < r:
                        ys = r
                    nchunk = CamPathChunkBuilder([(xs, ys)])  # startposition
                    ar[xs - r : xs - r + d, ys - r : ys - r + d] = (
                        ar[xs - r : xs - r + d, ys - r : ys - r + d] * cutterArrayNegative
                    )
                    r = random.random() * 2 * pi
                    e = Euler((0, 0, r))
                    testvect = lastvect.normalized() * 4  # multiply *2 not to get values <1 pixel
                    testvect.rotate(e)
                    lastvect = testvect.copy()
                success = True
                itests = 0
        i += 1
        if i % 100 == 0:
            print("100 Succesfull Tests Done")
            totpix = ar.sum()
            print(totpix)
            print(totaltests)
            i = 0
    chunk_builders.append(nchunk)
    for ch in chunk_builders:
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = (
                (ch[i][0] + coef - o.borderwidth) * o.optimisation.pixsize + minx,
                (ch[i][1] + coef - o.borderwidth) * o.optimisation.pixsize + miny,
                0,
            )
    return [c.to_chunk() for c in chunk_builders]


def crazy_stroke_image_binary(o, ar, avoidar):
    """Perform a milling operation using a binary image representation.

    This function implements a strategy for milling by navigating through a
    binary image. It starts from a defined point and attempts to move in
    various directions, evaluating the cutter load to determine the
    appropriate path. The algorithm continues until it either exhausts the
    available pixels to cut or reaches a predefined limit on the number of
    tests. The function modifies the input array to represent the areas that
    have been milled and returns the generated path as a list of chunks.

    Args:
        o (object): An object containing parameters for the milling operation, including
            cutter diameter, thresholds, and movement type.
        ar (np.ndarray): A 2D binary array representing the image to be milled.
        avoidar (np.ndarray): A 2D binary array indicating areas to avoid during milling.

    Returns:
        list: A list of chunks representing the path taken during the milling
            operation.
    """

    # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    # works like this:
    # start 'somewhere'
    # try to go in various directions.
    # if somewhere the cutter load is appropriate - it is correct magnitude and side, continue in that directon
    # try to continue straight or around that, looking
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    # TODO this should be somewhere else, but here it is now to get at least some ambient for start of the operation.
    ar[: o.borderwidth, :] = 0
    ar[-o.borderwidth :, :] = 0
    ar[:, : o.borderwidth] = 0
    ar[:, -o.borderwidth :] = 0

    # ceil((o.cutter_diameter/12)/o.optimisation.pixsize)
    r = int((o.cutter_diameter / 2.0) / o.optimisation.pixsize)
    d = 2 * r
    coef = 0.75
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = get_circle_binary(r)
    cutterArrayNegative = -cutterArray

    cutterimagepix = cutterArray.sum()

    anglelimit = o.crazy_threshold_3
    # a threshold which says if it is valuable to cut in a direction
    satisfypix = cutterimagepix * o.crazy_threshold_1
    toomuchpix = cutterimagepix * o.crazy_threshold_2  # same, but upper limit
    # (satisfypix+toomuchpix)/2.0# the ideal eating ratio
    optimalpix = cutterimagepix * o.crazy_threshold_5
    indices = ar.nonzero()  # first get white pixels

    startpix = ar.sum()  #
    totpix = startpix

    chunk_builders = []
    # try to find starting point here

    xs = indices[0][0] - r / 2
    if xs < r:
        xs = r
    ys = indices[1][0] - r
    if ys < r:
        ys = r

    nchunk = CamPathChunkBuilder([(xs, ys)])  # startposition
    print(indices)
    print(indices[0][0], indices[1][0])
    # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    lastvect = Vector((r, 0, 0))
    # multiply *2 not to get values <1 pixel
    testvect = lastvect.normalized() * r / 4.0
    rot = Euler((0, 0, 1))
    i = 0
    itests = 0
    totaltests = 0
    maxtests = 2000
    maxtotaltests = 20000  # 1000000

    margin = 0

    # print(xs,ys,indices[0][0],indices[1][0],r)
    ar[xs - r : xs + r, ys - r : ys + r] = (
        ar[xs - r : xs + r, ys - r : ys + r] * cutterArrayNegative
    )
    anglerange = [-pi, pi]
    # range for angle of toolpath vector versus material vector -
    # probably direction negative to the force applied on cutter by material.
    testangleinit = 0
    angleincrement = o.crazy_threshold_4

    if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW") or (
        o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW"
    ):
        anglerange = [-pi, 0]
        testangleinit = anglelimit
        angleincrement = -angleincrement
    elif (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW") or (
        o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW"
    ):
        anglerange = [0, pi]
        testangleinit = -anglelimit
        angleincrement = angleincrement

    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end
        success = False
        # define a vector which gets varied throughout the testing, growing and growing angle to sides.
        testangle = testangleinit
        testleftright = False
        testlength = r

        foundsolutions = []
        while not success:
            xs = int(nchunk.points[-1][0] + testvect.x)
            ys = int(nchunk.points[-1][1] + testvect.y)
            # print(xs,ys,ar.shape)
            # print(d)
            if (
                xs > r + margin
                and xs < ar.shape[0] - r - margin
                and ys > r + margin
                and ys < ar.shape[1] - r - margin
            ):
                # avoidtest=avoidar[xs-r:xs+r,ys-r:ys+r]*cutterArray
                if not avoidar[xs, ys]:
                    testar = ar[xs - r : xs + r, ys - r : ys + r] * cutterArray
                    eatpix = testar.sum()
                    cindices = testar.nonzero()
                    cx = cindices[0].sum() / eatpix
                    cy = cindices[1].sum() / eatpix
                    v = Vector((cx - r, cy - r))
                    # print(testvect.length,testvect)

                    if v.length != 0:
                        angle = testvect.to_2d().angle_signed(v)
                        if (
                            anglerange[0] < angle < anglerange[1]
                            and toomuchpix > eatpix > satisfypix
                        ) or (eatpix > 0 and totpix < startpix * 0.025):
                            # this could be righthanded milling?
                            # lets see :)
                            # print(xs,ys,angle)
                            foundsolutions.append([testvect.copy(), eatpix])
                            # or totpix < startpix*0.025:
                            if len(foundsolutions) >= 10:
                                success = True
            itests += 1
            totaltests += 1

            if success:
                # fist, try to inter/extrapolate the recieved results.
                closest = 100000000
                # print('evaluate')
                for s in foundsolutions:
                    # print(abs(s[1]-optimalpix),optimalpix,abs(s[1]))
                    if abs(s[1] - optimalpix) < closest:
                        bestsolution = s
                        closest = abs(s[1] - optimalpix)
                # print('closest',closest)

                # v1#+(v2-v1)*ratio#rewriting with interpolated vect.
                testvect = bestsolution[0]
                xs = int(nchunk.points[-1][0] + testvect.x)
                ys = int(nchunk.points[-1][1] + testvect.y)
                nchunk.points.append([xs, ys])
                lastvect = testvect

                ar[xs - r : xs + r, ys - r : ys + r] = (
                    ar[xs - r : xs + r, ys - r : ys + r] * cutterArrayNegative
                )
                totpix -= bestsolution[1]
                itests = 0
                # if 0:
                #     print('success')
                #     print(testar.sum(), satisfypix, toomuchpix)
                #     print(xs, ys, testlength, testangle)
                #     print(lastvect)
                #     print(testvect)
                #     print(itests)
                totaltests = 0
            else:
                # TODO: after all angles were tested into material higher than toomuchpix,
                #  it should cancel, otherwise there is no problem with long travel in free space.....
                # TODO:the testing should start not from the same angle as lastvector, but more towards material.
                #  So values closer to toomuchpix are obtained rather than satisfypix
                testvect = lastvect.normalized() * testlength

                if testangleinit == 0:  # meander
                    if testleftright:
                        testangle = -testangle - angleincrement
                        testleftright = False
                    else:
                        testangle = -testangle + angleincrement  # increment angle
                        testleftright = True
                else:  # climb/conv.
                    testangle += angleincrement

                if (abs(testangle) > o.crazy_threshold_3 and len(nchunk.points) > 1) or abs(
                    testangle
                ) > 2 * pi:  # /testlength
                    testangle = testangleinit
                    testlength += r / 4.0
                # print(itests,testlength)
                if nchunk.points[-1][0] + testvect.x < r:
                    testvect.x = r
                if nchunk.points[-1][1] + testvect.y < r:
                    testvect.y = r
                if nchunk.points[-1][0] + testvect.x > maxarx - r:
                    testvect.x = maxarx - r
                if nchunk.points[-1][1] + testvect.y > maxary - r:
                    testvect.y = maxary - r

                rot.z = testangle
                # if abs(testvect.normalized().y<-0.99):
                #   print(testvect,rot.z)
                testvect.rotate(rot)

                # if 0:
                #     print(xs, ys, testlength, testangle)
                #     print(lastvect)
                #     print(testvect)
                #     print(totpix)
                if itests > maxtests or testlength > r * 1.5:
                    # if len(foundsolutions)>0:

                    # print('resetting location')
                    # print(testlength,r)
                    andar = np.logical_and(ar, np.logical_not(avoidar))
                    indices = andar.nonzero()
                    if len(nchunk.points) > 1:
                        parent_child_distance([nchunk], chunks, o, distance=r)
                        chunk_builders.append(nchunk)

                    if totpix > startpix * 0.001:
                        found = False
                        ftests = 0
                        while not found:
                            # look for next start point:
                            index = random.randint(0, len(indices[0]) - 1)
                            # print(index,len(indices[0]))
                            # print(indices[index])
                            xs = indices[0][index]
                            ys = indices[1][index]
                            v = Vector((r - 1, 0, 0))
                            randomrot = random.random() * 2 * pi
                            e = Euler((0, 0, randomrot))
                            v.rotate(e)
                            xs += int(v.x)
                            ys += int(v.y)
                            if xs < r:
                                xs = r
                            if ys < r:
                                ys = r
                            if avoidar[xs, ys] == 0:
                                # print(toomuchpix,ar[xs-r:xs-r+d,ys-r:ys-r+d].sum()*pi/4,satisfypix)
                                testarsum = (
                                    ar[xs - r : xs - r + d, ys - r : ys - r + d].sum() * pi / 4
                                )
                                if toomuchpix > testarsum > 0 or (
                                    totpix < startpix * 0.025
                                ):  # 0 now instead of satisfypix
                                    found = True
                                    # print(xs,ys,indices[0][index],indices[1][index])

                                    nchunk = CamPathChunk([(xs, ys)])  # startposition
                                    ar[xs - r : xs + r, ys - r : ys + r] = (
                                        ar[xs - r : xs + r, ys - r : ys + r] * cutterArrayNegative
                                    )
                                    # lastvect=Vector((r,0,0))#vector is 3d,
                                    # blender somehow doesn't rotate 2d vectors with angles.
                                    randomrot = random.random() * 2 * pi
                                    e = Euler((0, 0, randomrot))
                                    testvect = (
                                        lastvect.normalized() * 2
                                    )  # multiply *2 not to get values <1 pixel
                                    testvect.rotate(e)
                                    lastvect = testvect.copy()
                            if ftests > 2000:
                                totpix = 0  # this quits the process now.
                            ftests += 1

                    success = True
                    itests = 0
        i += 1
        if i % 100 == 0:
            print("100 Succesfull Tests Done")
            totpix = ar.sum()
            print(totpix)
            print(totaltests)
            i = 0
    if len(nchunk.points) > 1:
        parent_child_distance([nchunk], chunks, o, distance=r)
        chunk_builders.append(nchunk)

    for ch in chunk_builders:
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = (
                (ch[i][0] + coef - o.borderwidth) * o.optimisation.pixsize + minx,
                (ch[i][1] + coef - o.borderwidth) * o.optimisation.pixsize + miny,
                o.min_z,
            )

    return [c.to_chunk for c in chunk_builders]


def image_to_chunks(o, image, with_border=False):
    """Convert an image into chunks based on detected edges.

    This function processes a given image to identify edges and convert them
    into polychunks, which are essentially collections of connected edge
    segments. It utilizes the properties of the input object `o` to
    determine the boundaries and size of the chunks. The function can
    optionally include borders in the edge detection process. The output is
    a list of chunks that represent the detected polygons in the image.

    Args:
        o (object): An object containing properties such as min, max, borderwidth,
            and optimisation settings.
        image (np.ndarray): A 2D array representing the image to be processed,
            expected to be in a format compatible with uint8.
        with_border (bool?): A flag indicating whether to include borders
            in the edge detection. Defaults to False.

    Returns:
        list: A list of chunks, where each chunk is represented as a collection of
            points that outline the detected edges in the image.
    """

    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.optimisation.pixsize

    image = image.astype(np.uint8)

    # progress('detecting outline')
    edges = []
    ar = image[:, :-1] - image[:, 1:]

    indices1 = ar.nonzero()
    borderspread = 2
    # o.cutter_diameter/o.optimisation.pixsize#when the border was excluded precisely, sometimes it did remove some silhouette parts
    r = o.borderwidth - borderspread
    # to prevent outline of the border was 3 before and also (o.cutter_diameter/2)/pixsize+o.borderwidth
    if with_border:
        #   print('border')
        r = 0
    w = image.shape[0]
    h = image.shape[1]
    coef = 0.75  # compensates for imprecisions
    for id in range(0, len(indices1[0])):
        a = indices1[0][id]
        b = indices1[1][id]
        if r < a < w - r and r < b < h - r:
            edges.append(((a - 1, b), (a, b)))

    ar = image[:-1, :] - image[1:, :]
    indices2 = ar.nonzero()
    for id in range(0, len(indices2[0])):
        a = indices2[0][id]
        b = indices2[1][id]
        if r < a < w - r and r < b < h - r:
            edges.append(((a, b - 1), (a, b)))

    polychunks = []
    # progress(len(edges))

    d = {}
    for e in edges:
        d[e[0]] = []
        d[e[1]] = []
    for e in edges:
        verts1 = d[e[0]]
        verts2 = d[e[1]]
        verts1.append(e[1])
        verts2.append(e[0])

    if len(edges) > 0:
        ch = [edges[0][0], edges[0][1]]  # first and his reference

        d[edges[0][0]].remove(edges[0][1])

        i = 0
        specialcase = 0
        # progress('condensing outline')
        while len(d) > 0 and i < 20000000:
            verts = d.get(ch[-1], [])
            closed = False
            # print(verts)

            if len(verts) <= 1:  # this will be good for not closed loops...some time
                closed = True
                if len(verts) == 1:
                    ch.append(verts[0])
                    verts.remove(verts[0])
            elif len(verts) >= 3:
                specialcase += 1
                v1 = ch[-1]
                v2 = ch[-2]
                white = image[v1[0], v1[1]]
                comesfromtop = v1[1] < v2[1]
                comesfrombottom = v1[1] > v2[1]
                comesfromleft = v1[0] > v2[0]
                comesfromright = v1[0] < v2[0]
                take = False
                for v in verts:
                    if v[0] == ch[-2][0] and v[1] == ch[-2][1]:
                        pass
                        verts.remove(v)

                    if not take:
                        if (not white and comesfromtop) or (
                            white and comesfrombottom
                        ):  # goes right
                            if v1[0] + 0.5 < v[0]:
                                take = True
                        elif (not white and comesfrombottom) or (
                            white and comesfromtop
                        ):  # goes left
                            if v1[0] > v[0] + 0.5:
                                take = True
                        elif (not white and comesfromleft) or (
                            white and comesfromright
                        ):  # goes down
                            if v1[1] > v[1] + 0.5:
                                take = True
                        elif (not white and comesfromright) or (white and comesfromleft):  # goes up
                            if v1[1] + 0.5 < v[1]:
                                take = True
                        if take:
                            ch.append(v)
                            verts.remove(v)

            else:  # here it has to be 2 always
                done = False
                for vi in range(len(verts) - 1, -1, -1):
                    if not done:
                        v = verts[vi]
                        if v[0] == ch[-2][0] and v[1] == ch[-2][1]:
                            pass
                            verts.remove(v)
                        else:
                            ch.append(v)
                            done = True
                            verts.remove(v)
                            # or len(verts)<=1:
                            if v[0] == ch[0][0] and v[1] == ch[0][1]:
                                closed = True

            if closed:
                polychunks.append(ch)
                for si, s in enumerate(ch):
                    # print(si)
                    if si > 0:  # first one was popped
                        if d.get(s, None) is not None and len(d[s]) == 0:
                            # this makes the case much less probable, but i think not impossible
                            d.pop(s)
                if len(d) > 0:
                    newch = False
                    while not newch:
                        v1 = d.popitem()
                        if len(v1[1]) > 0:
                            ch = [v1[0], v1[1][0]]
                            newch = True

            # print(' la problema grandiosa')
            i += 1
            if i % 10000 == 0:
                print(len(ch))
                # print(polychunks)
                print(i)

        vecchunks = []

        for ch in polychunks:
            vecchunk = []
            vecchunks.append(vecchunk)
            for i in range(0, len(ch)):
                ch[i] = (
                    (ch[i][0] + coef - o.borderwidth) * pixsize + minx,
                    (ch[i][1] + coef - o.borderwidth) * pixsize + miny,
                    0,
                )
                vecchunk.append(Vector(ch[i]))
        # print('optimizing outline')

        # print('directsimplify')
        reduxratio = 1.25  # was 1.25
        soptions = [
            "distance",
            "distance",
            o.optimisation.pixsize * reduxratio,
            5,
            o.optimisation.pixsize * reduxratio,
        ]
        nchunks = []
        for i, ch in enumerate(vecchunks):
            s = curve_simplify.simplify_RDP(ch, soptions)
            # print(s)
            nch = CamPathChunkBuilder([])
            for i in range(0, len(s)):
                nch.points.append((ch[s[i]].x, ch[s[i]].y))

            if len(nch.points) > 2:
                nchunks.append(nch.to_chunk())

        return nchunks
    else:
        return []


def image_to_shapely(o, i, with_border=False):
    """Convert an image to Shapely polygons.

    This function takes an image and converts it into a series of Shapely
    polygon objects. It first processes the image into chunks and then
    transforms those chunks into polygon geometries. The `with_border`
    parameter allows for the inclusion of borders in the resulting polygons.

    Args:
        o: The input image to be processed.
        i: Additional input parameters for processing the image.
        with_border (bool): A flag indicating whether to include
            borders in the resulting polygons. Defaults to False.

    Returns:
        list: A list of Shapely polygon objects created from the
            image chunks.
    """

    polychunks = image_to_chunks(o, i, with_border)
    polys = chunks_to_shapely(polychunks)

    return polys
