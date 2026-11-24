"""Fabex 'pattern.py' © 2012 Vilem Novak

Functions to read CAM path patterns and return CAM path chunks.
"""

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
from ..utilities.logging_utils import heading, log
from ..utilities.operation_utils import get_layers


async def helix_four_axis(o):
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

    log.info(heading("Strategy: Helix 4 Axis"))
    _minx, _miny, _minz, _maxx, _maxy, _maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pathchunks = []

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

    if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW") or (
        o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW"
    ):
        direction = -1
    else:
        direction = 1

    e[a1] = direction * anglestep

    # generalized length of the operation
    maxl = o.max[a1]
    minl = o.min[a1]
    steps = (maxl - minl) / o.distance_between_paths

    # set starting positions for cutter e.t.c.
    cutterstart = Vector((0, 0, 0))
    cutterend = Vector((0, 0, 0))  # end point for casting

    log.info("Helix")
    a1step = o.distance_between_paths / circlesteps
    # only one chunk, init here
    chunk = CamPathChunkBuilder([])

    for a in range(floor(steps) + 1):
        cutterstart[a1] = o.min[a1] + a * o.distance_between_paths
        cutterend[a1] = cutterstart[a1]
        cutterstart[a2] = 0
        cutterstart[a3] = radius
        cutterend[a3] = radiusend

        for b in range(floor(circlesteps) + 1):
            cutterstart[a1] += a1step
            cutterend[a1] += a1step
            chunk.startpoints.append(cutterstart.to_tuple())
            chunk.endpoints.append(cutterend.to_tuple())
            rot = [0, 0, 0]
            rot[a1] = direction * (a * 2 * pi + b * anglestep)
            chunk.rotations.append(rot)
            cutterstart.rotate(e)
            cutterend.rotate(e)

    chunk = chunk.to_chunk()
    chunk.depth = radiusend - radius

    pathchunks.append(chunk)
    path_samples = pathchunks
    depth = path_samples[0].depth
    chunks = []
    layers = get_layers(o, 0, depth)
    chunks.extend(await sample_chunks_n_axis(o, path_samples, layers))

    chunks_to_mesh(chunks, o)
