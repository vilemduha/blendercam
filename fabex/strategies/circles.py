from math import (
    pi,
    sqrt,
)

from mathutils import Euler, Vector

from ..bridges import use_bridges

from ..chunk_builder import CamPathChunkBuilder
from ..utilities.chunk_utils import (
    chunks_to_mesh,
    connect_chunks_low,
    sample_chunks,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.parent_utils import parent_child_distance
from ..utilities.simple_utils import progress


async def circles(o):
    progress("~ Building Path Pattern ~")
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    pathSamples = []

    zlevel = 1  # minz#this should do layers...

    pathd = o.distance_between_paths
    pathstep = o.distance_along_paths
    midx = (o.max.x + o.min.x) / 2
    midy = (o.max.y + o.min.y) / 2
    rx = o.max.x - o.min.x
    ry = o.max.y - o.min.y
    maxr = sqrt(rx * rx + ry * ry)
    e = Euler((0, 0, 0))
    chunk = CamPathChunkBuilder([])
    chunk.points.append((midx, midy, zlevel))
    pathSamples.append(chunk.to_chunk())
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
                    pathSamples.append(chunk)
                    currentstepchunks.append(chunk)
                    chunk = CamPathChunkBuilder([])

            v.rotate(e)

        if len(chunk.points) > 0:
            chunk.points.append(firstchunk.points[0])

            if chunk == firstchunk:
                chunk.closed = True

            chunk = chunk.to_chunk()
            pathSamples.append(chunk)
            currentstepchunks.append(chunk)
            chunk = CamPathChunkBuilder([])

        for ch in laststepchunks:
            for p in currentstepchunks:
                parent_child_distance(p, ch, o)

    if o.movement.insideout == "OUTSIDEIN":
        pathSamples.reverse()

    for chunk in pathSamples:
        if o.movement.insideout == "OUTSIDEIN":
            chunk.reverse()
        if (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CW") or (
            o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CCW"
        ):
            chunk.reverse()

    pathSamples = await connect_chunks_low(pathSamples, o)
    chunks = []
    layers = get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    if o.use_bridges:
        log.info(chunks)
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    chunks_to_mesh(chunks, o)
