import bpy

from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_refine,
    sort_chunks,
)
from ..utilities.curve_utils import curve_to_chunks
from ..utilities.logging_utils import log


async def carve(o):
    pathSamples = []
    ob = bpy.data.objects[o.curve_source]
    pathSamples.extend(curve_to_chunks(ob))
    # sort before sampling
    pathSamples = await sort_chunks(pathSamples, o)
    pathSamples = chunks_refine(pathSamples, o)

    chunks = []
    layers = strategy.get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    for ch in chunks:
        ch.offset_z(-o.carve_depth)

    if o.use_bridges:
        log.info(chunks)
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    strategy.chunks_to_mesh(chunks, o)
