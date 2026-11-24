from ..bridges import use_bridges
from ..utilities.chunk_utils import (
    chunks_coherency,
    chunks_to_mesh,
    connect_chunks_low,
    limit_chunks,
    sample_chunks,
    sort_chunks,
)
from ..utilities.image_utils import (
    get_offset_image_cavities,
    prepare_area,
)
from ..utilities.logging_utils import heading, log
from ..utilities.operation_utils import (
    get_ambient,
    get_layers,
)


async def pencil(o):
    log.info(heading("Strategy: Pencil"))

    await prepare_area(o)
    get_ambient(o)

    pathSamples = get_offset_image_cavities(o, o.offset_image)
    pathSamples = limit_chunks(pathSamples, o)
    # sort before sampling to keep pencil path chunks in a coherent spatial order
    pathSamples = await sort_chunks(pathSamples, o)

    chunks = []
    layers = get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling: Finished Successfully")

    log.info("Coherency Check")
    chunks = chunks_coherency(chunks)

    log.info("Status: Connecting Low Paths")
    chunks = await connect_chunks_low(chunks, o)

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    if o.use_bridges:
        log.info(f"Chunks: {chunks}")
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    chunks_to_mesh(chunks, o)
