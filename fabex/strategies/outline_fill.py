from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    sort_chunks,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.silhouette_utils import get_operation_silhouette


async def outline_fill(o):
    get_operation_silhouette(o)

    pathSamples = get_path_pattern(o)
    pathSamples = await sort_chunks(pathSamples, o)

    chunks = []
    layers = get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    log.info("Sorting")
    chunks = await sort_chunks(chunks, o)
    chunks = await connect_chunks_low(chunks, o)

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    if o.use_bridges:
        log.info(chunks)
    for bridge_chunk in chunks:
        use_bridges(bridge_chunk, o)

    chunks_to_mesh(chunks, o)
