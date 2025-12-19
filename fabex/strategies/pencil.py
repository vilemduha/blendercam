from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_coherency,
    chunks_to_mesh,
    limit_chunks,
    sample_chunks,
    sort_chunks,
)
from ..utilities.image_utils import prepare_area, get_offset_image_cavities
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers, get_ambient


async def pencil(o):
    await prepare_area(o)
    get_ambient(o)
    pathSamples = get_offset_image_cavities(o, o.offset_image)
    pathSamples = limit_chunks(pathSamples, o)
    # sort before sampling
    pathSamples = await sort_chunks(pathSamples, o)

    chunks = []
    layers = get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    chunks = chunks_coherency(chunks)
    log.info("Coherency Check")

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
