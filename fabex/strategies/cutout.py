from math import (
    radians,
    sqrt,
    tan,
)

import bpy

from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    limit_chunks,
    sort_chunks,
)
from ..utilities.curve_utils import curve_to_chunks
from ..utilities.logging_utils import log
from ..utilities.operation_utils import (
    check_min_z,
    get_layers,
)
from ..utilities.parent_utils import parent_child_poly
from ..utilities.shapely_utils import shapely_to_chunks
from ..utilities.silhouette_utils import get_object_outline
from ..utilities.simple_utils import (
    activate,
    remove_multiple,
    subdivide_short_lines,
)


# cutout strategy is completely here:
async def cutout(o):
    """Perform a cutout operation based on the provided parameters.

    This function calculates the necessary cutter offset based on the cutter
    type and its parameters. It processes a list of objects to determine how
    to cut them based on their geometry and the specified cutting type. The
    function handles different cutter types such as 'VCARVE', 'CYLCONE',
    'BALLCONE', and 'BALLNOSE', applying specific calculations for each. It
    also manages the layering and movement strategies for the cutting
    operation, including options for lead-ins, ramps, and bridges.

    Args:
        o (object): An object containing parameters for the cutout operation,
            including cutter type, diameter, depth, and other settings.

    Returns:
        None: This function does not return a value but performs operations
            on the provided object.
    """

    log.info("Strategy: Cutout")

    max_depth = check_min_z(o)
    cutter_angle = radians(o.cutter_tip_angle / 2)

    # Cutter Offset
    r = o.cutter_diameter / 2
    cutter_offset = r

    log.info(f"Cutter Type: {o.cutter_type}")
    log.info(f"Max Depth: {max_depth}")
    log.info(f"Cutter Radius: {r}")
    log.info(f"Skin: {o.skin}")

    offset_by_type = {
        "VCARVE": -max_depth * tan(cutter_angle),
        "CYLCONE": -max_depth * tan(cutter_angle) + o.cylcone_diameter / 2,
        "BALLCONE": -max_depth * tan(cutter_angle) + o.ball_radius,
        "BALLNOSE": sqrt(r**2 - (r + max_depth) ** 2) if -max_depth < r else r,
    }

    try:
        cutter_offset = offset_by_type[o.cutter_type]
    except:
        pass

    # Add Skin for Profile
    cutter_offset = (r if cutter_offset > r else cutter_offset) + o.skin

    log.info(f"Offset: {cutter_offset}")

    join = 2 if o.straight else 1
    offset = True

    for ob in o.objects:
        if ob.type == "CURVE":
            activate(ob)
            if ob.data.splines and ob.data.splines[0].type == "BEZIER":
                bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
            else:
                bpy.ops.object.curve_remove_doubles()
            # Ensure polylines are at least three points long
            subdivide_short_lines(ob)

    # Separate to allow open Curves :)
    if o.cut_type == "ONLINE" and o.onlycurves:
        log.info("Separate")
        chunks_from_curve = []

        for ob in o.objects:
            chunks_from_curve.extend(curve_to_chunks(ob, o.use_modifiers))
    else:
        chunks_from_curve = []

        if o.cut_type == "ONLINE":
            path = get_object_outline(0, o, True)
        else:
            offset = True

            if o.cut_type == "INSIDE":
                offset = False

            path = get_object_outline(cutter_offset, o, offset)

            if o.outlines_count > 1:
                for i in range(1, o.outlines_count):
                    chunks_from_curve.extend(shapely_to_chunks(path, -1))
                    path_distance = o.distance_between_paths

                    if o.cut_type == "INSIDE":
                        path_distance *= -1

                    path = path.buffer(
                        distance=path_distance,
                        resolution=o.optimisation.circle_detail,
                        join_style=join,
                        mitre_limit=2,
                    )

        chunks_from_curve.extend(shapely_to_chunks(path, -1))

        if o.outlines_count > 1 and o.movement.insideout == "OUTSIDEIN":
            chunks_from_curve.reverse()

    chunks_from_curve = limit_chunks(chunks_from_curve, o)

    if not o.dont_merge:
        parent_child_poly(chunks_from_curve, chunks_from_curve, o)

    if o.outlines_count == 1:
        chunks_from_curve = await sort_chunks(chunks_from_curve, o)

    move_type = o.movement.type
    spin = o.movement.spindle_rotation
    climb_ccw = move_type == "CLIMB" and spin == "CCW"
    conventional_cw = move_type == "CONVENTIONAL" and spin == "CW"

    if climb_ccw or conventional_cw:
        [chunk.reverse() for chunk in chunks_from_curve]

    # For simplicity, reverse once again when Inside cutting
    if o.cut_type == "INSIDE":
        [chunk.reverse() for chunk in chunks_from_curve]

    layers = get_layers(
        o,
        o.max_z,
        check_min_z(o),
    )
    chunk_copies = []

    # If First Down is true, cut each shape from top to bottom,
    # if not, split shapes into layers by height, creating copies as
    # the same chunks will be on multiple layers
    if o.first_down:
        for chunk in chunks_from_curve:
            # A direction switch boolean check is needed to avoid cutter
            # lifting with open Chunks and "MEANDER" movement
            dir_switch = False

            for layer in layers:
                chunk_copy = chunk.copy()

                if dir_switch:
                    chunk_copy.reverse()
                chunk_copies.append([chunk_copy, layer])

                if (not chunk.closed) and o.movement.type == "MEANDER":
                    dir_switch = not dir_switch
    else:
        for layer in layers:
            for chunk in chunks_from_curve:
                chunk_copies.append([chunk.copy(), layer])

    # Set Z for all Chunks
    for i, chunk_layer in enumerate(chunk_copies):
        chunk = chunk_layer[0]
        layer = chunk_layer[1]
        chunk.set_z(layer[1])

        log.info(f"Layer {i} Depth: {layer[1]}")

    chunks = []

    # Add Bridges to Chunks
    if o.use_bridges:
        remove_multiple(o.name + "_cut_bridges")
        bridge_height = min(o.max.z, o.min.z + abs(o.bridges_height))

        log.info("-")
        log.info("Using Bridges")
        log.info("Old Briddge Cut Removed")

        for chunk_layer in chunk_copies:
            chunk = chunk_layer[0]
            layer = chunk_layer[1]

            if layer[1] < bridge_height:
                use_bridges(chunk, o)

    if o.profile_start > 0:
        log.info("Cutout Change Profile Start")
        for chunk_layer in chunk_copies:
            chunk = chunk_layer[0]

            if chunk.closed:
                chunk.change_path_start(o)

    # Lead in
    if o.lead_in > 0.0 or o.lead_out > 0:
        log.info("Cutout Lead-in")
        for chunk_layer in chunk_copies:
            chunk = chunk_layer[0]

            if chunk.closed:
                chunk.break_path_for_leadin_leadout(o)
                chunk.lead_contour(o)

    # Add Ramps or just Chunks
    if o.movement.ramp:
        for chunk_layer in chunk_copies:
            chunk = chunk_layer[0]
            layer = chunk_layer[1]

            if o.movement.zig_zag_ramp:
                chunk.ramp_zig_zag(
                    layer[0],
                    layer[1],
                    o,
                )
                chunks.append(chunk)
            else:
                if chunk.closed:
                    chunk.ramp_contour(
                        layer[0],
                        layer[1],
                        o,
                    )
                    chunks.append(chunk)
                else:
                    chunk.ramp_zig_zag(
                        layer[0],
                        layer[1],
                        o,
                    )
                    chunks.append(chunk)
    else:
        for chunk_layer in chunk_copies:
            chunks.append(chunk_layer[0])

    chunks_to_mesh(chunks, o)
