"""Fabex 'chunk.py' © 2012 Vilem Novak

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

import numpy as np
from shapely.geometry import polygon as spolygon
from shapely import geometry as sgeometry

import bpy
from mathutils import Vector

from . import polygon_utils_cam
from .simple import (
    activate,
    distance_2d,
    progress,
)
from .exception import CamException
from .numba_wrapper import jit


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
    # parents=[]
    # children=[]
    # sorted=False

    # progressIndex=-1# for e.g. parallel strategy, when trying to save time..
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
                    d = chtest.dist(pos, o)
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
                print("turns %i" % turns)
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
                        print("turns %i" % turns)
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
            print("Path Direction Is Clockwise")
        else:
            print("Path Direction Is Counter Clockwise")
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


def set_chunks_z(chunks, z):
    newchunks = []
    for ch in chunks:
        chunk = ch.copy()
        chunk.set_z(z)
        newchunks.append(chunk)
    return newchunks


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
                print("joining stuff")
            if len(nch.points) > 0:
                nchunks.append(nch.to_chunk())
        return nchunks
    else:
        return chunks


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
    progress("Processing Curve - START - Vertices: " + str(vtotal))
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
    seq = polygon_utils_cam.shapely_to_coordinates(p)
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


def chunk_to_shapely(chunk):
    p = spolygon.Polygon(chunk.points)
    return p


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
