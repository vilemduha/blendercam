from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_refine,
    sort_chunks,
)
from ..utilities.logging_utils import log


async def crazy(o):
    await prepare_area(o)
    # pathSamples = crazyStrokeImage(o)
    # this kind of worked and should work:
    millarea = o.zbuffer_image < o.min_z + 0.000001
    avoidarea = o.offset_image > o.min_z + 0.000001

    pathSamples = crazy_stroke_image_binary(o, millarea, avoidarea)
    pathSamples = await sort_chunks(pathSamples, o)
    pathSamples = chunks_refine(pathSamples, o)

    chunks = []
    layers = strategy.get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    if o.use_bridges:
        log.info(chunks)
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    strategy.chunks_to_mesh(chunks, o)
