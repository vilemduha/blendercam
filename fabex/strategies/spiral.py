from math import (
    pi,
)


from mathutils import (
    Euler,
    Vector,
)

from ..chunk_builder import CamPathChunkBuilder

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    connect_chunks_low,
    sample_chunks,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import (
    get_layers,
    get_move_and_spin,
)


async def spiral(o):
    log.info("~ Strategy: Spiral ~")

    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pathSamples = []
    zlevel = 1
    chunk = CamPathChunkBuilder([])
    pathd = o.distance_between_paths
    pathstep = o.distance_along_paths
    midx = (o.max.x + o.min.x) / 2
    midy = (o.max.y + o.min.y) / 2
    x = pathd / 4
    y = pathd / 4
    v = Vector((pathd / 4, 0, 0))
    e = Euler((0, 0, 0))
    chunk.points.append((midx + v.x, midy + v.y, zlevel))

    while midx + v.x > o.min.x or midy + v.y > o.min.y:
        offset = 2 * v.length * pi
        e.z = 2 * pi * (pathstep / offset)
        v.rotate(e)
        v.length = v.length + pathd / (offset / pathstep)

        if o.max.x > midx + v.x > o.min.x and o.max.y > midy + v.y > o.min.y:
            chunk.points.append((midx + v.x, midy + v.y, zlevel))
        else:
            pathSamples.append(chunk.to_chunk())
            chunk = CamPathChunkBuilder([])

    if len(chunk.points) > 0:
        pathSamples.append(chunk.to_chunk())

    if o.movement.insideout == "OUTSIDEIN":
        pathSamples.reverse()

    for chunk in pathSamples:
        if o.movement.insideout == "OUTSIDEIN":
            chunk.reverse()

        if conventional_CW or climb_CCW:
            # TODO
            chunk.flip_x(o.max.x + o.min.x)

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
