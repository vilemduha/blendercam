from math import (
    floor,
    pi,
)

from mathutils import Euler, Vector

from ..chunk_builder import CamPathChunkBuilder

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    sample_chunks_n_axis,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.simple_utils import progress


async def parallel_four_axis(o):
    """Generate path patterns for a specified operation along a rotary axis.

    This function constructs a series of path chunks based on the provided
    operation's parameters, including the rotary axis, strategy, and
    dimensions. It calculates the necessary angles and positions for the
    cutter based on the specified strategy (PARALLELR, PARALLEL)
    and generates the corresponding path chunks for machining operations.

    Args:
        operation (object): An object containing parameters for the machining operation,
            including min and max coordinates, rotary axis configuration,
            distance settings, and movement strategy.

    Returns:
        list: A list of path chunks generated for the specified operation.
    """

    log.info("~ Strategy: Parallel 4 Axis ~")
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

    path_samples = pathchunks

    depth = path_samples[0].depth
    chunks = []

    layers = get_layers(o, 0, depth)

    chunks.extend(await sample_chunks_n_axis(o, path_samples, layers))
    chunks_to_mesh(chunks, o)
