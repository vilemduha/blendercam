from math import pi
import time

from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    sample_chunks,
    sort_chunks,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.simple_utils import progress
from ..utilities.strategy_utils import parallel_pattern


async def cross(o):
    # from pattern
    t = time.time()
    progress("~ Building Path Pattern ~")
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    pathSamples = []
    pathSamples.extend(parallel_pattern(o, o.parallel_angle))
    pathSamples.extend(parallel_pattern(o, o.parallel_angle - pi / 2.0))

    # from toolpath
    chunks = []
    layers = get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    log.info("Sorting")
    chunks = await sort_chunks(chunks, o)

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    if o.use_bridges:
        log.info(chunks)
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    chunks_to_mesh(chunks, o)
