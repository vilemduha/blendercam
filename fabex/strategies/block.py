from math import ceil, floor

from ..bridges import use_bridges

from ..chunk_builder import CamPathChunkBuilder
from ..utilities.chunk_utils import (
    chunks_to_mesh,
    connect_chunks_low,
    sample_chunks,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.simple_utils import progress


async def block(o):
    progress("~ Building Path Pattern ~")
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    # pathchunks = []

    zlevel = 1  # minz#this should do layers...

    # from Pattern
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
    pathSamples = [chunk.to_chunk()]

    # from Toolpath
    # if o.strategy in ["BLOCK", "SPIRAL", "CIRCLES"]:
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
