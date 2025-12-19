from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_refine,
    sample_chunks,
    sort_chunks,
)
from ..utilities.image_utils import prepare_area
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.stroke_utils import crazy_stroke_image_binary


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
