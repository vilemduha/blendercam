from ..exception import CamException


from ..utilities.chunk_utils import (
    chunks_to_mesh,
    sort_chunks,
    chunks_refine,
)
from ..utilities.curve_utils import curve_to_chunks
from ..utilities.logging_utils import log
from ..utilities.operation_utils import (
    get_operation_sources,
    check_min_z,
    get_layers,
)
from ..utilities.simple_utils import subdivide_short_lines


async def projected_curve(o):
    """Project a curve onto another curve object.

    This function takes a source object and a target object, both of which
    are expected to be curve objects. It projects the points of the source
    curve onto the target curve, adjusting the start and end points based on
    specified extensions. The resulting projected points are stored in the
    source object's path samples.

    Args:
        s (object): The source object containing the curve to be projected.
        o (object): An object containing references to the curve objects
            involved in the projection.

    Returns:
        None: This function does not return a value; it modifies the
            source object's path samples in place.

    Raises:
        CamException: If the target curve is not of type 'CURVE'.
    """

    log.info("Strategy: Projected Curve")

    path_samples = []
    chunks = []

    s = bpy.context.scene
    ob = bpy.data.objects[o.curve_source]
    path_samples.extend(curve_to_chunks(ob))
    target_curve = s.objects[o.curve_target]

    if target_curve.type != "CURVE":
        raise CamException("Projection Target and Source Have to Be Curve Objects!")

    if 1:
        extend_up = 0.1
        extend_down = 0.04
        target_samples = curve_to_chunks(target_curve)

        for chi, chunk in enumerate(path_samples):
            target_chunk = target_samples[chi].get_points()
            chunk.depth = 0
            chunk_points = chunk.get_points()

            for i, s in enumerate(chunk_points):
                # move the points a bit
                end_point = Vector(target_chunk[i])
                start_point = Vector(chunk_points[i])

                # Extend Start Point
                vector_start = start_point - end_point
                vector_start.normalize()
                vector_start *= extend_up
                start_point += vector_start
                chunk.startpoints.append(start_point)

                # Extend End Point
                vector_end = start_point - end_point
                vector_end.normalize()
                vector_end *= extend_down
                end_point -= vector_end
                chunk.endpoints.append(end_point)

                chunk.rotations.append((0, 0, 0))
                vector = start_point - end_point
                chunk.depth = min(chunk.depth, -vector.length)
                chunk_points[i] = start_point.copy()

    chunk.set_points(chunk_points)
    layers = get_layers(o, 0, chunk.depth)
    chunks.extend(sample_chunks_n_axis(o, path_samples, layers))
    chunks_to_mesh(chunks, o)
