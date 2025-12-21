"""Fabex 'cam_chunk.py' © 2012 Vilem Novak

Classes and Functions to build, store and optimize CAM path chunks.
"""

from math import (
    ceil,
    hypot,
    pi,
    sqrt,
    tan,
)

import numpy as np
from shapely.geometry import Polygon

from mathutils import Vector

from .utilities.internal_utils import _internal_x_y_distance_to
from .utilities.logging_utils import log
from .utilities.simple_utils import (
    distance_2d,
    rotate_point_by_point,
)


# for building points - stores points as lists for easy insert /append behaviour
class CamPathChunkBuilder:
    def __init__(self, inpoints=None, startpoints=None, endpoints=None, rotations=None):
        self.points = [] if inpoints is None else inpoints
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
        self.points = np.empty(shape=(0, 3)) if len(inpoints) == 0 else np.array(inpoints)
        self.poly = None  # get polygon just in time
        self.simppoly = None
        # from where the sweep test begins, but also retract point for given path
        self.startpoints = startpoints if startpoints else []
        self.endpoints = endpoints if endpoints else []
        # where sweep test ends
        self.rotations = rotations if rotations else []
        # rotation of the machine axes
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
        self.poly = Polygon(self.points[:, 0:2]) if len(self.points) > 2 else Polygon()

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
            # Divide by Zero Exception
            with np.errstate(invalid="raise"):
                try:
                    return self.poly.dwithin(other.poly, cutoff)
                # Suppress RuntimeWarning 'Divide by Zero'
                # Doesn't affect path calculation, but keeps logs cleaner
                except FloatingPointError:
                    pass
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
        testlist = tested = [child for child in self.children]
        ch = None

        while len(testlist) > 0:
            chtest = testlist.pop()

            if not chtest.sorted:
                self.cango = False
                cango = True

                [
                    testlist.append(child)
                    for child in chtest.children
                    if not child.sorted and child not in tested
                ]
                [
                    tested.append(child)
                    for child in chtest.children
                    if not child.sorted and child not in tested
                ]

                for child in chtest.children:
                    if not child.sorted:
                        cango = False

                if cango:
                    d = chtest.distance(pos, o)

                    if d < mind:
                        ch = chtest
                        mind = d

        return ch if ch is not None else None

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
        log.warning("Popping from Chunk Is Slow", self, index)
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
            self.points = np.concatenate(
                (
                    self.points,
                    np.array(points),
                )
            )
            if startpoints is not None:
                self.startpoints.extend(startpoints)
            if endpoints is not None:
                self.endpoints.extend(endpoints)
            if rotations is not None:
                self.rotations.extend(rotations)
        else:
            self.points = np.concatenate(
                (
                    self.points[0:at_index],
                    np.array(points),
                    self.points[at_index:],
                )
            )
            if startpoints is not None:
                self.startpoints[at_index:at_index] = startpoints
            if endpoints is not None:
                self.endpoints[at_index:at_index] = endpoints
            if rotations is not None:
                self.rotations[at_index:at_index] = rotations

    def clip_points(self, minx, maxx, miny, maxy):
        """Remove Any Points Outside This Range"""
        in_range_x = (self.points[:, 0] >= minx) and (self.points[:, 0] <= maxx)
        in_range_y = (self.points[:, 1] >= maxy) and (self.points[:, 1] <= maxy)
        included_values = in_range_x and in_range_y
        self.points = self.points[included_values]

    def ramp_contour(self, zstart, zend, o):
        stepdown = zstart - zend
        chunk_points = []
        estlength = (zstart - zend) / tan(o.movement.ramp_in_angle)
        self.get_length()
        ramplength = estlength
        ltraveled = 0
        endpoint = None
        i = 0
        znew = 10
        rounds = 0  # for counting if ramping makes more layers

        while endpoint is None and not (znew == zend and i == 0):
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

            znew = max(znew, zend, s[2])
            chunk_points.append((s[0], s[1], znew))
            z = znew

            if endpoint is not None:
                break
            i += 1

            if i >= len(self.points):
                i = 0
                rounds += 1

        if endpoint is not None:  # append final contour on the bottom z level
            i = endpoint
            started = False

            if i == len(self.points):
                i = 0

            while i != endpoint or not started:
                started = True
                s = self.points[i]
                chunk_points.append((s[0], s[1], s[2]))
                i += 1

                if i == len(self.points):
                    i = 0
        # ramp out
        if o.movement.ramp_out and (
            not o.use_layers or not o.first_down or (o.first_down and endpoint is not None)
        ):
            z = zend

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

        # this check here is only for stupid setup,
        # when the chunks lie actually above operation start z.
        if zend < zstart:
            stepdown = zstart - zend
            estlength = (zstart - zend) / tan(o.movement.ramp_in_angle)
            self.get_length()

            if self.length > 0:  # for single point chunks..
                ramplength = estlength
                zigzaglength = ramplength / 2.000
                turns = 1

                log.info(f"Turns: {turns}")

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
                        p1 = ramppoints[-1]
                        p2 = self.points[i]
                        d = distance_2d(p1, p2)
                        zigzagtraveled += d

                        if zigzagtraveled >= zigzaglength or i + 1 == len(self.points):
                            ratio = 1 - (zigzagtraveled - zigzaglength) / d

                            # this condition is for a rare case of combined layers+bridges+ramps..
                            if i + 1 == len(self.points):
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

                        log.info(f"Turns: {turns}")

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
                                p1 = ramppoints[-1]
                                p2 = self.points[i]
                                d = distance_2d(p1, p2)
                                zigzagtraveled += d

                                if zigzagtraveled >= zigzaglength or i + 1 == len(self.points):
                                    ratio = 1 - (zigzagtraveled - zigzaglength) / d

                                    # this condition is for a rare case of
                                    # combined layers+bridges+ramps...
                                    if i + 1 == len(self.points):
                                        ratio = 1

                                    v = p1 + ratio * (p2 - p1)
                                    ramppoints.append(v.tolist())
                                    haspoints = True

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
                                # max value here is so that it doesn't go below surface in the case of 3d paths
                                chunk_points.append((p2[0], p2[1], max(p2[2], znew)))

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

                if segmentLength > 2 * max(iradius, oradius):
                    # Be certain there is enough room for the leadin and leadiout
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
        # 1 is Clockwise, 0 is CCW
        perimeterDirection = 1
        if o.movement.spindle_rotation == "CW":
            if o.movement.type == "CONVENTIONAL":
                perimeterDirection = 0

        if self.parents:  # if it is inside another parent
            perimeterDirection ^= 1  # toggle with a bitwise XOR
            log.info("Has Parent")

        if perimeterDirection == 1:
            log.info("Path Direction is Clockwise")
        else:
            log.info("Path Direction is Counter Clockwise")

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

        # add lead out arc to the end
        if round(o.lead_in, 6) > 0.0:
            for i in range(15):
                iangle = i * (pi / 2) / 15
                arc_p = rotate_point_by_point(arc_c, start, iangle)
                chunk_points.append(arc_p)

        self.points = np.array(chunk_points)
