from ..exception import CamException

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    chunks_refine,
    sort_chunks,
)
from ..utilities.curve_utils import curve_to_chunks
from ..utilities.logging_utils import log
from ..utilities.operation_utils import (
    get_operation_sources,
    check_min_z,
    get_layers,
)
from ..utilities.simple_utils import subdivide_short_lines


async def curve(o):
    """Process and convert curve objects into mesh chunks.

    This function takes an operation object and processes the curves
    contained within it. It first checks if all objects are curves; if not,
    it raises an exception. The function then converts the curves into
    chunks, sorts them, and refines them. If layers are to be used, it
    applies layer information to the chunks, adjusting their Z-offsets
    accordingly. Finally, it converts the processed chunks into a mesh.

    Args:
        o (Operation): An object containing operation parameters, including a list of
            objects, flags for layer usage, and movement constraints.

    Returns:
        None: This function does not return a value; it performs operations on the
            input.

    Raises:
        CamException: If not all objects in the operation are curves.
    """

    log.info("Strategy: Curve to Path")

    path_samples = []
    get_operation_sources(o)

    if not o.onlycurves:
        raise CamException("All Objects Must Be Curves for This Operation.")

    for ob in o.objects:
        # Ensure Polylines are at least three points long
        subdivide_short_lines(ob)
        # Make the Chunks from the Curve
        path_samples.extend(curve_to_chunks(ob))

    # Sort Chunks before sampling Path
    path_samples = await sort_chunks(path_samples, o)
    # Simplify Path Chunks
    path_samples = chunks_refine(path_samples, o)

    # Layers
    if o.use_layers:
        # layers is a list of lists [[0.00,l1],[l1,l2],[l2,l3]]
        # containing the start and end of each layer
        layers = get_layers(
            o,
            o.max_z,
            round(check_min_z(o), 6),
        )
        chunk_copies = []
        chunks = []

        # Include Layer information in Chunk list
        for layer in layers:
            for chunk in path_samples:
                chunk_copies.append([chunk.copy(), layer])

        # Set offset Z for all chunks according to the layer information,
        for chunk_layer in chunk_copies:
            chunk = chunk_layer[0]
            layer = chunk_layer[1]  #
            chunk.clamp_z(layer[1])
            # Limit Cut Depth to Operation Z Minimum
            chunk.clamp_z(o.min_z)
            # Limit Cut Height to Operation Safe Height
            chunk.clamp_max_z(o.movement.free_height)

            log.info(f"Layer: {layer[1]}")

        # Strip Layer information from extendorder and transfer them to Chunks
        for chunk_layer in chunk_copies:
            chunks.append(chunk_layer[0])

        chunks_to_mesh(chunks, o)  # finish by converting to mesh

    # No Layers, old Curve
    else:
        for chunk in path_samples:
            # Limit Cut Depth to Operation Z Minimum
            chunk.clamp_z(o.min_z)
            # Limit Cut Height to Operation Safe Height
            chunk.clamp_max_z(o.movement.free_height)

        chunks_to_mesh(path_samples, o)
