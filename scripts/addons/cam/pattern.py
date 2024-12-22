"""Fabex 'pattern.py' © 2012 Vilem Novak

Functions to read CAM path patterns and return CAM path chunks.
"""

from math import (
    ceil,
    floor,
    pi,
    sqrt,
)
import time

import numpy

import bpy
from mathutils import Euler, Vector

from .cam_chunk import (
    CamPathChunk,
    CamPathChunkBuilder,
    shapely_to_chunks,
)

from .utilities.chunk_utils import (
    chunks_refine,
    parent_child_distance,
)
from .utilities.simple_utils import progress


def get_path_pattern_parallel(o, angle):
    """Generate path chunks for parallel movement based on object dimensions
    and angle.

    This function calculates a series of path chunks for a given object,
    taking into account its dimensions and the specified angle. It utilizes
    both a traditional method and an alternative algorithm (currently
    disabled) to generate these paths. The paths are constructed by
    iterating over calculated vectors and applying transformations based on
    the object's properties. The resulting path chunks can be used for
    various movement types, including conventional and climb movements.

    Args:
        o (object): An object containing properties such as dimensions and movement type.
        angle (float): The angle to rotate the path generation.

    Returns:
        list: A list of path chunks generated based on the object's dimensions and
            angle.
    """

    zlevel = 1
    pathd = o.distance_between_paths
    pathstep = o.distance_along_paths
    pathchunks = []

    xm = (o.max.x + o.min.x) / 2
    ym = (o.max.y + o.min.y) / 2
    vm = Vector((xm, ym, 0))
    xdim = o.max.x - o.min.x
    ydim = o.max.y - o.min.y
    dim = (xdim + ydim) / 2.0
    e = Euler((0, 0, angle))
    reverse = False
    if bpy.app.debug_value == 0:  # by default off
        # this is the original pattern method, slower, but well tested:
        dirvect = Vector((0, 1, 0))
        dirvect.rotate(e)
        dirvect.normalize()
        dirvect *= pathstep
        for a in range(
            int(-dim / pathd), int(dim / pathd)
        ):  # this is highly ineffective, computes path2x the area needed...
            chunk = CamPathChunkBuilder([])
            v = Vector((a * pathd, int(-dim / pathstep) * pathstep, 0))
            v.rotate(e)
            # shifting for the rotation, so pattern rotates around middle...
            v += vm
            for b in range(int(-dim / pathstep), int(dim / pathstep)):
                v += dirvect

                if v.x > o.min.x and v.x < o.max.x and v.y > o.min.y and v.y < o.max.y:
                    chunk.points.append((v.x, v.y, zlevel))
            if (
                (reverse and o.movement.type == "MEANDER")
                or (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW")
                or (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW")
            ):
                chunk.points.reverse()

            if len(chunk.points) > 0:
                pathchunks.append(chunk.to_chunk())
            if (
                len(pathchunks) > 1
                and reverse
                and o.movement.parallel_step_back
                and not o.use_layers
            ):
                # parallel step back - for finishing, best with climb movement, saves cutter life by going into
                # material with climb, while using move back on the surface to improve finish
                # (which would otherwise be a conventional move in the material)

                if o.movement.type == "CONVENTIONAL" or o.movement.type == "CLIMB":
                    pathchunks[-2].reverse()
                changechunk = pathchunks[-1]
                pathchunks[-1] = pathchunks[-2]
                pathchunks[-2] = changechunk

            reverse = not reverse
        # print (chunk.points)
    else:  # alternative algorithm with numpy, didn't work as should so blocked now...
        v = Vector((0, 1, 0))
        v.rotate(e)
        e1 = Euler((0, 0, -pi / 2))
        v1 = v.copy()
        v1.rotate(e1)

        axis_across_paths = numpy.array(
            (
                numpy.arange(int(-dim / pathd), int(dim / pathd)) * pathd * v1.x + xm,
                numpy.arange(int(-dim / pathd), int(dim / pathd)) * pathd * v1.y + ym,
                numpy.arange(int(-dim / pathd), int(dim / pathd)) * 0,
            )
        )

        axis_along_paths = numpy.array(
            (
                numpy.arange(int(-dim / pathstep), int(dim / pathstep)) * pathstep * v.x,
                numpy.arange(int(-dim / pathstep), int(dim / pathstep)) * pathstep * v.y,
                numpy.arange(int(-dim / pathstep), int(dim / pathstep)) * 0 + zlevel,
            )
        )  # rotate this first
        progress(axis_along_paths)
        chunks = []
        for a in range(0, len(axis_across_paths[0])):
            # progress(chunks[a,...,...].shape)
            # progress(axis_along_paths.shape)
            nax = axis_along_paths.copy()
            # progress(nax.shape)
            nax[0] += axis_across_paths[0][a]
            nax[1] += axis_across_paths[1][a]
            # progress(a)
            # progress(nax.shape)
            # progress(chunks.shape)
            # progress(chunks[...,a,...].shape)
            xfitmin = nax[0] > o.min.x
            xfitmax = nax[0] < o.max.x
            xfit = xfitmin & xfitmax
            # print(xfit,nax)
            nax = numpy.array([nax[0][xfit], nax[1][xfit], nax[2][xfit]])
            yfitmin = nax[1] > o.min.y
            yfitmax = nax[1] < o.max.y
            yfit = yfitmin & yfitmax
            nax = numpy.array([nax[0][yfit], nax[1][yfit], nax[2][yfit]])
            chunks.append(nax.swapaxes(0, 1))
        # chunks
        pathchunks = []
        for ch in chunks:
            ch = ch.tolist()
            pathchunks.append(CamPathChunk(ch))
        # print (ch)
    return pathchunks


def get_path_pattern(operation):
    """Generate a path pattern based on the specified operation strategy.

    This function constructs a path pattern for a given operation by
    analyzing its parameters and applying different strategies such as
    'PARALLEL', 'CROSS', 'BLOCK', 'SPIRAL', 'CIRCLES', and 'OUTLINEFILL'.
    Each strategy dictates how the path is built, utilizing various
    geometric calculations and conditions to ensure the path adheres to the
    specified operational constraints. The function also handles the
    orientation and direction of the path based on the movement settings
    provided in the operation.

    Args:
        operation (object): An object containing parameters for path generation,
            including strategy, movement type, and geometric bounds.

    Returns:
        list: A list of path chunks representing the generated path pattern.
    """

    o = operation
    t = time.time()
    progress("Building Path Pattern")
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    pathchunks = []

    zlevel = 1  # minz#this should do layers...
    if o.strategy == "PARALLEL":
        pathchunks = get_path_pattern_parallel(o, o.parallel_angle)
    elif o.strategy == "CROSS":
        pathchunks.extend(get_path_pattern_parallel(o, o.parallel_angle))
        pathchunks.extend(get_path_pattern_parallel(o, o.parallel_angle - pi / 2.0))

    elif o.strategy == "BLOCK":
        pathd = o.distance_between_paths
        pathstep = o.distance_along_paths
        maxxp = maxx
        maxyp = maxy
        minxp = minx
        minyp = miny
        x = 0.0
        y = 0.0
        incx = 1
        incy = 0
        chunk = CamPathChunkBuilder([])
        i = 0
        while maxxp - minxp > 0 and maxyp - minyp > 0:
            y = minyp
            for a in range(ceil(minxp / pathstep), ceil(maxxp / pathstep), 1):
                x = a * pathstep
                chunk.points.append((x, y, zlevel))

            if i > 0:
                minxp += pathd
            chunk.points.append((maxxp, minyp, zlevel))

            x = maxxp

            for a in range(ceil(minyp / pathstep), ceil(maxyp / pathstep), 1):
                y = a * pathstep
                chunk.points.append((x, y, zlevel))

            minyp += pathd
            chunk.points.append((maxxp, maxyp, zlevel))

            y = maxyp
            for a in range(floor(maxxp / pathstep), ceil(minxp / pathstep), -1):
                x = a * pathstep
                chunk.points.append((x, y, zlevel))

            maxxp -= pathd
            chunk.points.append((minxp, maxyp, zlevel))

            x = minxp
            for a in range(floor(maxyp / pathstep), ceil(minyp / pathstep), -1):
                y = a * pathstep
                chunk.points.append((x, y, zlevel))
            chunk.points.append((minxp, minyp, zlevel))

            maxyp -= pathd

            i += 1
        if o.movement.insideout == "INSIDEOUT":
            chunk.points.reverse()
        if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW") or (
            o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW"
        ):
            for si in range(0, len(chunk.points)):
                s = chunk.points[si]
                chunk.points[si] = (o.max.x + o.min.x - s[0], s[1], s[2])
        pathchunks = [chunk.to_chunk()]

    elif o.strategy == "SPIRAL":
        chunk = CamPathChunkBuilder([])
        pathd = o.distance_between_paths
        pathstep = o.distance_along_paths
        midx = (o.max.x + o.min.x) / 2
        midy = (o.max.y + o.min.y) / 2
        x = pathd / 4
        y = pathd / 4
        v = Vector((pathd / 4, 0, 0))

        # progress(x,y,midx,midy)
        e = Euler((0, 0, 0))
        # pi = pi
        chunk.points.append((midx + v.x, midy + v.y, zlevel))
        while midx + v.x > o.min.x or midy + v.y > o.min.y:
            # v.x=x-midx
            # v.y=y-midy
            offset = 2 * v.length * pi
            e.z = 2 * pi * (pathstep / offset)
            v.rotate(e)

            v.length = v.length + pathd / (offset / pathstep)
            # progress(v.x,v.y)
            if o.max.x > midx + v.x > o.min.x and o.max.y > midy + v.y > o.min.y:
                chunk.points.append((midx + v.x, midy + v.y, zlevel))
            else:
                pathchunks.append(chunk.to_chunk())
                chunk = CamPathChunkBuilder([])
        if len(chunk.points) > 0:
            pathchunks.append(chunk.to_chunk())
        if o.movement.insideout == "OUTSIDEIN":
            pathchunks.reverse()
        for chunk in pathchunks:
            if o.movement.insideout == "OUTSIDEIN":
                chunk.reverse()

            if (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW") or (
                o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW"
            ):
                # TODO
                chunk.flip_x(o.max.x + o.min.x)
                # for si in range(0, len(chunk.points)):
                #     s = chunk.points[si]
                #     chunk.points[si] = (o.max.x + o.min.x - s[0], s[1], s[2])

    elif o.strategy == "CIRCLES":
        pathd = o.distance_between_paths
        pathstep = o.distance_along_paths
        midx = (o.max.x + o.min.x) / 2
        midy = (o.max.y + o.min.y) / 2
        rx = o.max.x - o.min.x
        ry = o.max.y - o.min.y
        maxr = sqrt(rx * rx + ry * ry)

        # progress(x,y,midx,midy)
        e = Euler((0, 0, 0))
        # pi = pi
        chunk = CamPathChunkBuilder([])
        chunk.points.append((midx, midy, zlevel))
        pathchunks.append(chunk.to_chunk())
        r = 0

        while r < maxr:
            r += pathd
            chunk = CamPathChunkBuilder([])
            firstchunk = chunk
            v = Vector((-r, 0, 0))
            steps = 2 * pi * r / pathstep
            e.z = 2 * pi / steps
            laststepchunks = []
            currentstepchunks = []
            for a in range(0, int(steps)):
                laststepchunks = currentstepchunks
                currentstepchunks = []

                if o.max.x > midx + v.x > o.min.x and o.max.y > midy + v.y > o.min.y:
                    chunk.points.append((midx + v.x, midy + v.y, zlevel))
                else:
                    if len(chunk.points) > 0:
                        chunk.closed = False
                        chunk = chunk.to_chunk()
                        pathchunks.append(chunk)
                        currentstepchunks.append(chunk)
                        chunk = CamPathChunkBuilder([])
                v.rotate(e)

            if len(chunk.points) > 0:
                chunk.points.append(firstchunk.points[0])
                if chunk == firstchunk:
                    chunk.closed = True
                chunk = chunk.to_chunk()
                pathchunks.append(chunk)
                currentstepchunks.append(chunk)
                chunk = CamPathChunkBuilder([])
            for ch in laststepchunks:
                for p in currentstepchunks:
                    parent_child_distance(p, ch, o)

        if o.movement.insideout == "OUTSIDEIN":
            pathchunks.reverse()
        for chunk in pathchunks:
            if o.movement.insideout == "OUTSIDEIN":
                chunk.reverse()
            if (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW") or (
                o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW"
            ):
                chunk.reverse()
    # pathchunks=sort_chunks(pathchunks,o)not until they get hierarchy parents!
    elif o.strategy == "OUTLINEFILL":
        polys = o.silhouette.geoms
        pathchunks = []
        chunks = []
        for p in polys:
            p = p.buffer(-o.distance_between_paths / 10, o.optimisation.circle_detail)
            # first, move a bit inside, because otherwise the border samples go crazy very often changin between
            # hit/non hit and making too many jumps in the path.
            chunks.extend(shapely_to_chunks(p, 0))

        pathchunks.extend(chunks)
        lastchunks = chunks
        firstchunks = chunks

        approxn = (min(maxx - minx, maxy - miny) / o.distance_between_paths) / 2
        i = 0

        for porig in polys:
            p = porig
            while not p.is_empty:
                p = p.buffer(-o.distance_between_paths, o.optimisation.circle_detail)
                if not p.is_empty:
                    nchunks = shapely_to_chunks(p, zlevel)

                    if o.movement.insideout == "INSIDEOUT":
                        parent_child_distance(lastchunks, nchunks, o)
                    else:
                        parent_child_distance(nchunks, lastchunks, o)
                    pathchunks.extend(nchunks)
                    lastchunks = nchunks
                percent = int(i / approxn * 100)
                progress("Outlining Polygons ", percent)
                i += 1
        pathchunks.reverse()
        if not o.inverse:  # dont do ambient for inverse milling
            lastchunks = firstchunks
            for p in polys:
                d = o.distance_between_paths
                steps = o.ambient_radius / o.distance_between_paths
                for a in range(0, int(steps)):
                    dist = d
                    if a == int(o.cutter_diameter / 2 / o.distance_between_paths):
                        if o.optimisation.use_exact:
                            dist += o.optimisation.pixsize * 0.85
                            # this is here only because silhouette is still done with zbuffer method,
                            # even if we use bullet collisions.
                        else:
                            dist += o.optimisation.pixsize * 2.5
                    p = p.buffer(dist, o.optimisation.circle_detail)
                    if not p.is_empty:
                        nchunks = shapely_to_chunks(p, zlevel)
                        if o.movement.insideout == "INSIDEOUT":
                            parent_child_distance(nchunks, lastchunks, o)
                        else:
                            parent_child_distance(lastchunks, nchunks, o)
                        pathchunks.extend(nchunks)
                        lastchunks = nchunks

        if o.movement.insideout == "OUTSIDEIN":
            pathchunks.reverse()

        for chunk in pathchunks:
            if o.movement.insideout == "OUTSIDEIN":
                chunk.reverse()
            if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW") or (
                o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW"
            ):
                chunk.reverse()

        chunks_refine(pathchunks, o)
    progress(time.time() - t)
    return pathchunks


def get_path_pattern_4_axis(operation):
    """Generate path patterns for a specified operation along a rotary axis.

    This function constructs a series of path chunks based on the provided
    operation's parameters, including the rotary axis, strategy, and
    dimensions. It calculates the necessary angles and positions for the
    cutter based on the specified strategy (PARALLELR, PARALLEL, or HELIX)
    and generates the corresponding path chunks for machining operations.

    Args:
        operation (object): An object containing parameters for the machining operation,
            including min and max coordinates, rotary axis configuration,
            distance settings, and movement strategy.

    Returns:
        list: A list of path chunks generated for the specified operation.
    """

    o = operation
    t = time.time()
    progress("Building Path Pattern")
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pathchunks = []
    zlevel = 1  # minz#this should do layers...

    # set axes for various options, Z option is obvious nonsense now.
    if o.rotary_axis_1 == "X":
        a1 = 0
        a2 = 1
        a3 = 2
    if o.rotary_axis_1 == "Y":
        a1 = 1
        a2 = 0
        a3 = 2
    if o.rotary_axis_1 == "Z":
        a1 = 2
        a2 = 0
        a3 = 1

    o.max.z = o.max_z
    # set radius for all types of operation
    radius = max(o.max.z, 0.0001)
    radiusend = o.min.z

    mradius = max(radius, radiusend)
    circlesteps = (mradius * pi * 2) / o.distance_along_paths
    circlesteps = max(4, circlesteps)
    anglestep = 2 * pi / circlesteps
    # generalized rotation
    e = Euler((0, 0, 0))
    e[a1] = anglestep

    # generalized length of the operation
    maxl = o.max[a1]
    minl = o.min[a1]
    steps = (maxl - minl) / o.distance_between_paths

    # set starting positions for cutter e.t.c.
    cutterstart = Vector((0, 0, 0))
    cutterend = Vector((0, 0, 0))  # end point for casting

    if o.strategy_4_axis == "PARALLELR":
        for a in range(0, floor(steps) + 1):
            chunk = CamPathChunkBuilder([])

            cutterstart[a1] = o.min[a1] + a * o.distance_between_paths
            cutterend[a1] = cutterstart[a1]

            cutterstart[a2] = 0  # radius
            cutterend[a2] = 0  # radiusend

            cutterstart[a3] = radius
            cutterend[a3] = radiusend

            for b in range(0, floor(circlesteps) + 1):
                # print(cutterstart,cutterend)
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())
                rot = [0, 0, 0]
                rot[a1] = a * 2 * pi + b * anglestep

                chunk.rotations.append(rot)
                cutterstart.rotate(e)
                cutterend.rotate(e)

            chunk.depth = radiusend - radius
            # last point = first
            chunk.startpoints.append(chunk.startpoints[0])
            chunk.endpoints.append(chunk.endpoints[0])
            chunk.rotations.append(chunk.rotations[0])

            pathchunks.append(chunk.to_chunk())

    if o.strategy_4_axis == "PARALLEL":
        circlesteps = (mradius * pi * 2) / o.distance_between_paths
        steps = (maxl - minl) / o.distance_along_paths

        anglestep = 2 * pi / circlesteps
        # generalized rotation
        e = Euler((0, 0, 0))
        e[a1] = anglestep

        reverse = False

        for b in range(0, floor(circlesteps) + 1):
            chunk = CamPathChunkBuilder([])
            cutterstart[a2] = 0
            cutterstart[a3] = radius

            cutterend[a2] = 0
            cutterend[a3] = radiusend

            e[a1] = anglestep * b

            cutterstart.rotate(e)
            cutterend.rotate(e)

            for a in range(0, floor(steps) + 1):
                cutterstart[a1] = o.min[a1] + a * o.distance_along_paths
                cutterend[a1] = cutterstart[a1]
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())
                rot = [0, 0, 0]
                rot[a1] = b * anglestep
                chunk.rotations.append(rot)

            chunk = chunk.to_chunk()
            chunk.depth = radiusend - radius
            pathchunks.append(chunk)

            if (
                (reverse and o.movement.type == "MEANDER")
                or (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW")
                or (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW")
            ):
                chunk.reverse()

            reverse = not reverse

    if o.strategy_4_axis == "HELIX":
        print("Helix")

        a1step = o.distance_between_paths / circlesteps

        chunk = CamPathChunkBuilder([])  # only one chunk, init here

        for a in range(0, floor(steps) + 1):
            cutterstart[a1] = o.min[a1] + a * o.distance_between_paths
            cutterend[a1] = cutterstart[a1]
            cutterstart[a2] = 0
            cutterstart[a3] = radius
            cutterend[a3] = radiusend

            for b in range(0, floor(circlesteps) + 1):
                # print(cutterstart,cutterend)
                cutterstart[a1] += a1step
                cutterend[a1] += a1step
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())

                rot = [0, 0, 0]
                rot[a1] = a * 2 * pi + b * anglestep
                chunk.rotations.append(rot)

                cutterstart.rotate(e)
                cutterend.rotate(e)

            chunk = chunk.to_chunk()
            chunk.depth = radiusend - radius

        pathchunks.append(chunk)

    return pathchunks
