"""Fabex 'pattern.py' © 2012 Vilem Novak

Functions to read CAM path patterns and return CAM path chunks.
"""

from math import (
    floor,
    pi,
)


from ..utilities.chunk_builder import CamPathChunkBuilder
from ..utilities.chunk_utils import chunks_to_mesh, sample_chunks_n_axis
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers


async def helix_four_axis(o):
    """Generate path patterns for a specified operation along a rotary axis.

    This function constructs a series of path chunks based on the provided
    operation's parameters, including the rotary axis, strategy, and
    dimensions. It calculates the necessary angles and positions for the
    cutter based on the specified strategy (PARALLELR, PARALLEL, or HELIX)
    and generates the corresponding path chunks for machining operations.

    Args:
        operation (object): An object containing parameters for the machining operation,
            including min and max coordinates, rotary axis configuration,
            distance settings, and movement strategy.

    Returns:
        list: A list of path chunks generated for the specified operation.
    """

    if o.strategy_4_axis == "HELIX":
        log.info("Helix")
        a1step = o.distance_between_paths / circlesteps
        # only one chunk, init here
        chunk = CamPathChunkBuilder([])

        for a in range(0, floor(steps) + 1):
            cutterstart[a1] = o.min[a1] + a * o.distance_between_paths
            cutterend[a1] = cutterstart[a1]
            cutterstart[a2] = 0
            cutterstart[a3] = radius
            cutterend[a3] = radiusend

            for b in range(0, floor(circlesteps) + 1):
                cutterstart[a1] += a1step
                cutterend[a1] += a1step
                chunk.startpoints.append(cutterstart.to_tuple())
                chunk.endpoints.append(cutterend.to_tuple())
                rot = [0, 0, 0]
                rot[a1] = a * 2 * pi + b * anglestep
                chunk.rotations.append(rot)
                cutterstart.rotate(e)
                cutterend.rotate(e)

            chunk = chunk.to_chunk()
            chunk.depth = radiusend - radius

        pathchunks.append(chunk)

    path_samples = pathchunks

    depth = path_samples[0].depth
    chunks = []

    layers = get_layers(o, 0, depth)

    chunks.extend(await sample_chunks_n_axis(o, path_samples, layers))
    chunks_to_mesh(chunks, o)
