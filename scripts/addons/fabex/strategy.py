"""Fabex 'strategy.py' © 2012 Vilem Novak

Strategy functionality of Fabex - e.g. Cutout, Parallel, Spiral, Waterline
The functions here are called with operators defined in 'ops.py'
"""

from math import (
    ceil,
    pi,
    radians,
    sqrt,
    tan,
)
import sys
import time

from shapely import affinity
from shapely.geometry import (
    LineString,
    MultiPolygon,
    Point,
    Polygon,
)
from shapely.ops import linemerge

import bpy
from bpy_extras import object_utils
from mathutils import Euler, Vector

from .bridges import use_bridges
from .cam_chunk import (
    CamPathChunk,
    curve_to_chunks,
    limit_chunks,
    shapely_to_chunks,
    sample_chunks_n_axis,
    silhouette_offset,
    get_object_silhouette,
    get_object_outline,
    get_operation_silhouette,
    sort_chunks,
)
from .collision import cleanup_bullet_collision
from .constants import SHAPELY
from .exception import CamException

from .operators.curve_create_ops import generate_crosshatch

from .utilities.chunk_utils import (
    chunks_refine,
    optimize_chunk,
    chunks_refine_threshold,
    parent_child_distance,
    parent_child_poly,
    set_chunks_z,
    extend_chunks_5_axis,
)
from .utilities.compare_utils import check_equal, unique
from .utilities.geom_utils import circle, helix
from .utilities.logging_utils import log
from .utilities.operation_utils import get_operation_sources
from .utilities.shapely_utils import shapely_to_curve
from .utilities.simple_utils import (
    activate,
    delete_object,
    join_multiple,
    progress,
    remove_multiple,
    subdivide_short_lines,
)
from .voronoi import compute_voronoi_diagram


# add pocket op for medial axis and profile cut inside to clean unremoved material
def add_pocket(max_depth, sname, new_cutter_diameter):
    """Add a pocket operation for the medial axis and profile cut.

    This function first deselects all objects in the scene and then checks
    for any existing medial pocket objects, deleting them if found. It
    verifies whether a medial pocket operation already exists in the CAM
    operations. If it does not exist, it creates a new pocket operation with
    the specified parameters. The function also modifies the selected
    object's silhouette offset based on the new cutter diameter.

    Args:
        max_depth (float): The maximum depth of the pocket to be created.
        sname (str): The name of the object to which the pocket will be added.
        new_cutter_diameter (float): The diameter of the new cutter to be used.
    """

    bpy.ops.object.select_all(action="DESELECT")
    scene = bpy.context.scene
    mpocket_exists = False

    # OBJECT name
    mp_ob_name = f"{sname}_medial_pocket"

    # Delete old Medial Pocket object, if one exists
    # [ob.select_set(True) for ob in scene.objects if ob.name.startswith(mp_ob_name)]
    for ob in scene.objects:
        if ob.name.startswith(mp_ob_name):
            ob.select_set(True)
            bpy.ops.object.delete()

    # OPERATION name
    mp_op_name = f"{sname}_MedialPocket"

    # Verify Medial Pocket Operation exists
    for op in scene.cam_operations:
        if op.name == mp_op_name:
            mpocket_exists = True

    # Modify Silhouette with Cutter Radius
    ob = bpy.data.objects[sname]
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    silhouette_offset(
        ob,
        -new_cutter_diameter / 2,
        1,
        2,
    )
    bpy.context.active_object.name = mp_ob_name
    m_ob = bpy.context.view_layer.objects.active
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    m_ob.location.z = max_depth

    # Create a Pocket Operation if it does not exist already
    if not mpocket_exists:
        scene.cam_operations.add()
        o = scene.cam_operations[-1]
        o.object_name = mp_ob_name
        scene.cam_active_operation = len(scene.cam_operations) - 1
        o.name = mp_op_name
        o.filename = o.name
        o.strategy = "POCKET"
        o.use_layers = False
        o.material.estimate_from_model = False
        o.material.size[2] = -max_depth


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
            layer = chunk_layer[1]
            chunk.offset_z(o.max_z * 2 - o.min_z + layer[1])
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


async def project_curve(s, o):
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


async def pocket(o):
    """Perform pocketing operation based on the provided parameters.

    This function executes a pocketing operation using the specified
    parameters from the object `o`. It calculates the cutter offset based on
    the cutter type and depth, processes curves, and generates the necessary
    chunks for the pocketing operation. The function also handles various
    movement types and optimizations, including helix entry and retract
    movements.

    Args:
        o (object): An object containing parameters for the pocketing

    Returns:
        None: The function modifies the scene and generates geometry
        based on the pocketing operation.
    """

    log.info("Strategy: Pocket")

    join = 2 if o.straight else 1

    scene = bpy.context.scene
    remove_multiple("3D_poc")
    max_depth = check_min_z(o) + o.skin
    cutter_angle = radians(o.cutter_tip_angle / 2)

    cutter_offset = o.cutter_diameter / 2
    if o.cutter_type == "VCARVE":
        cutter_offset = -max_depth * tan(cutter_angle)
    elif o.cutter_type == "CYLCONE":
        cutter_offset = -max_depth * tan(cutter_angle) + o.cylcone_diameter / 2
    elif o.cutter_type == "BALLCONE":
        cutter_offset = -max_depth * tan(cutter_angle) + o.ball_radius

    if cutter_offset > o.cutter_diameter / 2:
        cutter_offset = o.cutter_diameter / 2

    cutter_offset += o.skin  # add skin
    log.info(f"Cutter Offset: {cutter_offset}")
    obname = o.object_name
    c_ob = bpy.data.objects[obname]

    for ob in o.objects:
        if ob.type == "CURVE":
            if ob.data.splines and ob.data.splines[0].type == "BEZIER":
                activate(ob)
                bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
            else:
                bpy.ops.object.curve_remove_doubles()

    circle_detail = o.optimisation.circle_detail

    chunks_from_curve = []
    angle = radians(o.parallel_pocket_angle)
    stepover = o.distance_between_paths
    offset = -cutter_offset
    pocket_shape = ""
    n_angle = angle - pi / 2
    pr = get_object_outline(0, o, False)

    if o.pocket_type == "PARALLEL":
        if o.parallel_pocket_contour:
            offset = -(cutter_offset + stepover / 2)
            point = pr.buffer(
                -cutter_offset,
                resolution=circle_detail,
                join_style=join,
                mitre_limit=2,
            )
            nchunks = shapely_to_chunks(point, o.min.z)
            chunks_from_curve.extend(nchunks)

        crosshatch_result = generate_crosshatch(
            bpy.context,
            angle,
            stepover,
            offset,
            pocket_shape,
            join,
            c_ob,
        )
        nchunks = shapely_to_chunks(crosshatch_result, o.min.z)
        chunks_from_curve.extend(nchunks)

        if o.parallel_pocket_crosshatch:
            crosshatch_result = generate_crosshatch(
                bpy.context,
                n_angle,
                stepover,
                offset,
                pocket_shape,
                join,
                c_ob,
            )
            nchunks = shapely_to_chunks(crosshatch_result, o.min.z)
            chunks_from_curve.extend(nchunks)

    else:
        point = pr.buffer(
            -cutter_offset,
            resolution=circle_detail,
            join_style=join,
            mitre_limit=2,
        )
        size_x = o.max.x - o.min.x
        size_y = o.max.y - o.min.y
        approximate_area = (min(size_x, size_y) / stepover) / 2

        log.info(f"Approximative: {approximate_area}")
        log.info(o.name)

        i = 0
        chunks = []
        last_chunks = []
        centers = None
        first_outline = point  # for testing in the end.
        prest = point.buffer(-cutter_offset, circle_detail)

        while not point.is_empty:
            if o.pocket_to_curve:
                # make a curve starting with _3dpocket
                shapely_to_curve("3dpocket", point, 0.0)

            nchunks = shapely_to_chunks(point, o.min.z)
            pnew = point.buffer(
                -stepover,
                circle_detail,
                join_style=join,
                mitre_limit=2,
            )

            if pnew.is_empty:
                # test if the last curve will leave material
                pt = point.buffer(
                    -cutter_offset,
                    circle_detail,
                    join_style=join,
                    mitre_limit=2,
                )

                if not pt.is_empty:
                    pnew = pt

            nchunks = limit_chunks(nchunks, o)
            chunks_from_curve.extend(nchunks)
            parent_child_distance(last_chunks, nchunks, o)
            last_chunks = nchunks
            percent = int(i / approximate_area * 100)
            progress("Outlining Polygons ", percent)
            point = pnew
            i += 1

    # TODO inside outside!

    move_type = o.movement.type
    spin = o.movement.spindle_rotation
    climb_cw = move_type == "CLIMB" and spin == "CW"
    climb_ccw = move_type == "CLIMB" and spin == "CCW"
    conventional_cw = move_type == "CONVENTIONAL" and spin == "CW"
    conventional_ccw = move_type == "CONVENTIONAL" and spin == "CCW"

    if climb_cw or conventional_ccw:
        for chunk in chunks_from_curve:
            chunk.reverse()

    chunks_from_curve = await sort_chunks(chunks_from_curve, o)
    chunks = []
    layers = get_layers(
        o,
        o.max_z,
        check_min_z(o),
    )

    for layer in layers:
        layer_chunks = set_chunks_z(chunks_from_curve, layer[1])

        if o.movement.ramp:
            for chunk in layer_chunks:
                chunk.zstart = layer[0]
                chunk.zend = layer[1]

        # helix_enter first try here TODO: check if helix radius is not out of operation area.
        if o.movement.helix_enter:
            helix_radius = cutter_offset * o.movement.helix_diameter * 0.01
            # 90 percent of cutter radius
            helix_circumference = helix_radius * pi * 2
            revolution_height = helix_circumference * tan(o.movement.ramp_in_angle)

            for chunk_index, chunk in enumerate(layer_chunks):
                if not chunks_from_curve[chunk_index].children:
                    # TODO:intercept closest next point when it should stay low
                    point = chunk.get_point(0)
                    # first thing to do is to check if helix enter can really enter.
                    check_circle = circle(
                        helix_radius + cutter_offset,
                        circle_detail,
                    )
                    check_circle = affinity.translate(
                        check_circle,
                        point[0],
                        point[1],
                    )
                    covers = False
                    silhouette_geometry = o.silhouette.geoms

                    for polygon in silhouette_geometry:
                        if polygon.contains(check_circle):
                            covers = True
                            break

                    if covers:
                        revolutions = (layer[0] - point[2]) / revolution_height
                        entry_helix = helix(
                            helix_radius,
                            circle_detail,
                            layer[0],
                            point,
                            revolutions,
                        )
                        # invert helix if not the typical direction
                        if conventional_cw or climb_ccw:
                            inverse_helix = []
                            for vector in entry_helix:
                                inverse_helix.append(
                                    (
                                        2 * point[0] - vector[0],
                                        vector[1],
                                        vector[2],
                                    )
                                )
                            entry_helix = inverse_helix
                        chunk.extend(entry_helix, at_index=0)

                    else:
                        o.info.warnings += "Helix entry did not fit! \n "
                        chunk.closed = True
                        chunk.ramp_zig_zag(layer[0], layer[1], o)

        # Arc retract here first try:
        # TODO: check for entry and exit point before actual computing... will be much better.
        if o.movement.retract_tangential:
            # TODO: fix this for CW and CCW!
            for chunk_index, chunk in enumerate(layer_chunks):
                if (
                    chunks_from_curve[chunk_index].parents == []
                    or len(chunks_from_curve[chunk_index].parents) == 1
                ):
                    revolutions = 0.25
                    vector_1 = Vector(chunk.get_point(-1))
                    i = -2
                    vector_2 = Vector(chunk.get_point(i))
                    vector = vector_1 - vector_2

                    while vector.length == 0:
                        i = i - 1
                        vector_2 = Vector(chunk.get_point(i))
                        vector = vector_1 - vector_2

                    vector.normalize()
                    rotate_angle = Vector((vector.x, vector.y)).angle_signed(Vector((1, 0)))
                    e = Euler((0, 0, pi / 2.0))  # TODO:#CW CLIMB!
                    vector.rotate(e)
                    point = vector_1 + vector * o.movement.retract_radius
                    center = point
                    point = (point.x, point.y, point.z)
                    entry_helix = helix(
                        o.movement.retract_radius,
                        circle_detail,
                        point[2] + o.movement.retract_height,
                        point,
                        revolutions,
                    )
                    # angle to rotate whole retract move
                    e = Euler((0, 0, rotate_angle + pi))
                    rotate_helix = []
                    check_polygon = []  # polygon for outlining and checking collisions.

                    for point in entry_helix:  # rotate helix to go from tangent of vector
                        vector_1 = Vector(point)
                        vector = vector_1 - center
                        vector.x = -vector.x  # flip it here first...
                        vector.rotate(e)
                        point = center + vector
                        rotate_helix.append(point)
                        check_polygon.append((point[0], point[1]))

                    check_polygon = Polygon(check_polygon)
                    check_outline = check_polygon.buffer(cutter_offset, circle_detail)
                    rotate_helix.reverse()
                    covers = False
                    silhouette_geometry = o.silhouette.geoms

                    for polygon in silhouette_geometry:
                        if polygon.contains(check_outline):
                            covers = True
                            break

                    if covers:
                        chunk.extend(rotate_helix)

        chunks.extend(layer_chunks)

    if o.movement.ramp:
        for chunk in chunks:
            chunk.ramp_zig_zag(
                chunk.zstart,
                chunk.get_point(0)[2],
                o,
            )

    if o.first_down:
        if o.pocket_option == "OUTSIDE":
            chunks.reverse()
        chunks = await sort_chunks(chunks, o)

    if o.pocket_to_curve:  # make curve instead of a path
        join_multiple("3dpocket")
    else:
        chunks_to_mesh(chunks, o)  # make normal pocket path


async def drill(o):
    """Perform a drilling operation on the specified objects.

    This function iterates through the objects in the provided context,
    activating each object and applying transformations. It duplicates the
    objects and processes them based on their type (CURVE or MESH). For
    CURVE objects, it calculates the bounding box and center points of the
    splines and bezier points, and generates chunks based on the specified
    drill type. For MESH objects, it generates chunks from the vertices. The
    function also manages layers and chunk depths for the drilling
    operation.

    Args:
        o (object): An object containing properties and methods required
            for the drilling operation, including a list of
            objects to drill, drill type, and depth parameters.

    Returns:
        None: This function does not return a value but performs operations
            that modify the state of the Blender context.
    """

    log.info("Strategy: Drill")

    chunks = []

    for ob in o.objects:
        activate(ob)
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={
                "linked": False,
                "mode": "TRANSLATION",
            },
            TRANSFORM_OT_translate={
                "value": (0, 0, 0),
                "constraint_axis": (False, False, False),
                "orient_type": "GLOBAL",
                "mirror": False,
                "use_proportional_edit": False,
                "proportional_edit_falloff": "SMOOTH",
                "proportional_size": 1,
                "snap": False,
                "snap_target": "CLOSEST",
                "snap_point": (0, 0, 0),
                "snap_align": False,
                "snap_normal": (0, 0, 0),
                "texture_space": False,
                "release_confirm": False,
            },
        )
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
        ob = bpy.context.active_object

        if ob.type == "CURVE":
            ob.data.dimensions = "3D"

        try:
            bpy.ops.object.transform_apply(
                location=True,
                rotation=False,
                scale=False,
            )
            bpy.ops.object.transform_apply(
                location=False,
                rotation=True,
                scale=False,
            )
            bpy.ops.object.transform_apply(
                location=False,
                rotation=False,
                scale=True,
            )
        except:
            pass

        object_location = ob.location

        if ob.type == "CURVE":
            for curve in ob.data.splines:
                max_x, min_x, max_y, min_y, max_z, min_z = (
                    -10000,
                    10000,
                    -10000,
                    10000,
                    -10000,
                    10000,
                )
                # If Curve Points has points use them, otherwise use Bezier Points
                points = curve.points if len(curve.points) > 0 else curve.bezier_points

                for point in points:
                    if o.drill_type == "ALL_POINTS":
                        chunks.append(
                            CamPathChunk(
                                [
                                    (
                                        point.co.x + object_location.x,
                                        point.co.y + object_location.y,
                                        point.co.z + object_location.z,
                                    )
                                ]
                            )
                        )
                    min_x = min(point.co.x, min_x)
                    max_x = max(point.co.x, max_x)
                    min_y = min(point.co.y, min_y)
                    max_y = max(point.co.y, max_y)
                    min_z = min(point.co.z, min_z)
                    max_z = max(point.co.z, max_z)

                center_x = (max_x + min_x) / 2
                center_y = (max_y + min_y) / 2
                center_z = (max_z + min_z) / 2
                center = (center_x, center_y)
                aspect = (max_x - min_x) / (max_y - min_y)

                aspect_check = 1.3 > aspect > 0.7
                mid_sym = o.drill_type == "MIDDLE_SYMETRIC"
                mid_all = o.drill_type == "MIDDLE_ALL"

                if (aspect_check and mid_sym) or mid_all:
                    chunks.append(
                        CamPathChunk(
                            [
                                (
                                    center[0] + object_location.x,
                                    center[1] + object_location.y,
                                    center_z + object_location.z,
                                )
                            ]
                        )
                    )

        elif ob.type == "MESH":
            for vertex in ob.data.vertices:
                chunks.append(
                    CamPathChunk(
                        [
                            (
                                vertex.co.x + object_location.x,
                                vertex.co.y + object_location.y,
                                vertex.co.z + object_location.z,
                            )
                        ]
                    )
                )
        # Delete temporary Object with applied transforms
        delete_object(ob)

    layers = get_layers(
        o,
        o.max_z,
        check_min_z(o),
    )

    chunk_layers = []
    for layer in layers:
        for chunk in chunks:
            # If using Object for minz then use Z from Points in Object
            if o.min_z_from == "OBJECT":
                z = chunk.get_point(0)[2]
            else:  # using operation minz
                z = o.min_z
            # only add a chunk layer if the chunk z point is in or lower than the layer
            if z <= layer[0]:
                if z <= layer[1]:
                    z = layer[1]
                # perform peck drill
                new_chunk = chunk.copy()
                new_chunk.set_z(z)
                chunk_layers.append(new_chunk)
                # retract tool to maxz (operation depth start in ui)
                new_chunk = chunk.copy()
                new_chunk.set_z(o.max_z)
                chunk_layers.append(new_chunk)

    chunk_layers = await sort_chunks(chunk_layers, o)
    chunks_to_mesh(chunk_layers, o)


async def medial_axis(o):
    """Generate the medial axis for a given operation.

    This function computes the medial axis of the specified operation, which
    involves processing various cutter types and their parameters. It starts
    by removing any existing medial mesh, then calculates the maximum depth
    based on the cutter type and its properties. The function refines curves
    and computes the Voronoi diagram for the points derived from the
    operation's silhouette. It filters points and edges based on their
    positions relative to the computed shapes, and generates a mesh
    representation of the medial axis. Finally, it handles layers and
    optionally adds a pocket operation if specified.

    Args:
        o (Operation): An object containing parameters for the operation, including
            cutter type, dimensions, and other relevant properties.

    Returns:
        dict: A dictionary indicating the completion status of the operation.

    Raises:
        CamException: If an unsupported cutter type is provided or if the input curve
            is not closed.
    """

    log.info("Strategy: Medial Axis")

    remove_multiple("medialMesh")

    chunks = []

    angle = o.cutter_tip_angle
    # Angle in Degrees
    slope = tan(pi * (90 - angle / 2) / 180)
    new_cutter_diameter = o.cutter_diameter
    m_o_ob = o.object_name

    if o.cutter_type == "VCARVE":
        # start the max depth calc from the "start depth" of the operation.
        max_depth = o.max_z - slope * o.cutter_diameter / 2 - o.skin
        # don't cut any deeper than the "end depth" of the operation.
        if max_depth < o.min_z:
            max_depth = o.min_z
            # the effective cutter diameter can be reduced from it's max
            # since we will be cutting shallower than the original max_depth
            # without this, the curve is calculated as if the diameter was at the original max_depth and we get the bit
            # pulling away from the desired cut surface
            new_cutter_diameter = (max_depth - o.max_z) / (-slope) * 2
    elif o.cutter_type == "BALLNOSE":
        max_depth = -new_cutter_diameter / 2 - o.skin
    else:
        raise CamException("Only Ballnose and V-carve Cutters Are Supported for Medial Axis.")

    # remember resolutions of curves, to refine them,
    # otherwise medial axis computation yields too many branches in curved parts
    resolutions_before = []

    for ob in o.objects:
        if ob.type == "CURVE":
            if ob.data.splines and ob.data.splines[0].type == "BEZIER":
                activate(ob)
                bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
            else:
                bpy.ops.object.curve_remove_doubles()

    for ob in o.objects:
        if ob.type in ["CURVE", "FONT"]:
            resolutions_before.append(ob.data.resolution_u)
            if ob.data.resolution_u < 64:
                ob.data.resolution_u = 64

    silhouette_polygon = get_operation_silhouette(o)
    silhouette_is_list = isinstance(silhouette_polygon, list)
    silhouette_is_multipolygon = isinstance(silhouette_polygon, MultiPolygon)

    if silhouette_is_list:
        if len(silhouette_polygon) == 1 and isinstance(silhouette_polygon[0], MultiPolygon):
            multipolygon = silhouette_polygon[0]
        else:
            multipolygon = MultiPolygon(silhouette_polygon)
    elif silhouette_is_multipolygon:
        # just a multipolygon
        multipolygon = silhouette_polygon
    else:
        raise CamException("Failed Getting Object Silhouette. Is Input Curve Closed?")

    multipolygon_boundary = multipolygon.boundary
    multipolygon_geometry = multipolygon.geoms

    for polygon_index, polygon in enumerate(multipolygon_geometry):
        polygon_index += 1

        silhouette_chunks = shapely_to_chunks(polygon, -1)
        silhouette_chunks = chunks_refine_threshold(
            silhouette_chunks,
            o.medial_axis_subdivision,
            o.medial_axis_threshold,
        )

        vertices = []

        for chunk in silhouette_chunks:
            vertices.extend(chunk.get_points())

        duplicate_point_count, z_colinear_point_count = unique(vertices)
        vertex_count = len(vertices)

        log.info(f"Duplicate Points Ignored: {duplicate_point_count}")
        log.info(f"Z Colinear Points Excluded: {z_colinear_point_count}")

        if vertex_count < 3:
            log.info("Not Enough Points")
            return {"FINISHED"}

        # Check colinear
        x_values = [vertex[0] for vertex in vertices]
        y_values = [vertex[1] for vertex in vertices]

        if check_equal(x_values) or check_equal(y_values):
            log.info("Points Are Colinear")
            return {"FINISHED"}

        # Create diagram
        log.info(f"Tesselation... ({vertex_count} Points)")

        x_buffer, y_buffer = 5, 5
        z_position = 0
        verts_as_points = [Point(vertex[0], vertex[1], vertex[2]) for vertex in vertices]
        points, edges = compute_voronoi_diagram(
            verts_as_points,
            x_buffer,
            y_buffer,
            polygonsOutput=False,
            formatOutput=True,
        )

        vertr = []
        filtered_points = []

        log.info("Filter Points")

        newIdx = 0
        point_count = len(points)

        for point_index, point in enumerate(points):
            point_index += 1

            if point_index % 500 == 0:
                sys.stdout.write("\r")
                # the exact output you're looking for:
                prog_message = f"Points: {point_index}/{point_count} - {round(100 * point_index / point_count)}%"
                sys.stdout.write(prog_message)
                sys.stdout.flush()

            if not polygon.contains(Point(point)):
                vertr.append((True, -1))
            else:
                vertr.append((False, newIdx))

                if o.cutter_type == "VCARVE":
                    # start the z depth calc from the "start depth" of the operation.
                    z = o.max_z - multipolygon.boundary.distance(Point(point)) * slope
                    z = max_depth if z < max_depth else z

                elif o.cutter_type == "BALL" or o.cutter_type == "BALLNOSE":
                    d = multipolygon_boundary.distance(Point(point))
                    r = new_cutter_diameter / 2.0

                    if d >= r:
                        z = -r
                    else:
                        z = -r + sqrt(r * r - d * d)
                else:
                    z = 0  #

                filtered_points.append((point[0], point[1], z))
                newIdx += 1

        log.info("Filter Edges")
        log.info("-")

        filtered_edges = []
        line_edges = []

        for edge in edges:
            # Exclude Edges with already excluded Points
            do = False if vertr[edge[0]][0] or vertr[edge[1]][0] else True

            if do:
                filtered_edges.append(
                    (
                        vertr[edge[0]][1],
                        vertr[edge[1]][1],
                    )
                )
                line_edges.append(
                    LineString(
                        (
                            filtered_points[vertr[edge[0]][1]],
                            filtered_points[vertr[edge[1]][1]],
                        )
                    )
                )

        polygon_buffer = polygon.buffer(-new_cutter_diameter / 2, resolution=64)
        lines = linemerge(line_edges)

        if polygon_buffer.geom_type in ["Polygon", "MultiPolygon"]:
            lines = lines.difference(polygon_buffer)
            chunks.extend(shapely_to_chunks(polygon_buffer, max_depth))

        chunks.extend(shapely_to_chunks(lines, 0))

        # Generate a Mesh from the Medial calculations
        if o.add_mesh_for_medial:
            shapely_to_curve("medialMesh", lines, 0.0)
            bpy.ops.object.convert(target="MESH")

    oi = 0
    for ob in o.objects:
        if ob.type in ["CURVE", "FONT"]:
            ob.data.resolution_u = resolutions_before[oi]
            oi += 1

    chunks = await sort_chunks(chunks, o)
    layers = get_layers(
        o,
        o.max_z,
        o.min.z,
    )
    chunk_layers = []

    for layer in layers:
        for chunk in chunks:
            if chunk.is_below_z(layer[0]):
                new_chunk = chunk.copy()
                new_chunk.clamp_z(layer[1])
                chunk_layers.append(new_chunk)

    if o.first_down:
        chunk_layers = await sort_chunks(chunk_layers, o)

    if o.add_mesh_for_medial:  # make curve instead of a path
        join_multiple("medialMesh")

    chunks_to_mesh(chunk_layers, o)
    # add pocket operation for medial if add pocket checked
    if o.add_pocket_for_medial:
        # export medial axis parameter to pocket op
        add_pocket(max_depth, m_o_ob, new_cutter_diameter)


def get_layers(operation, start_depth, end_depth):
    """Returns a list of layers bounded by start depth and end depth.

    This function calculates the layers between the specified start and end
    depths based on the step down value defined in the operation. If the
    operation is set to use layers, it computes the number of layers by
    dividing the difference between start and end depths by the step down
    value. The function raises an exception if the start depth is lower than
    the end depth.

    Args:
        operation (object): An object that contains the properties `use_layers`,
            `stepdown`, and `maxz` which are used to determine
            how layers are generated.
        start_depth (float): The starting depth for layer calculation.
        end_depth (float): The ending depth for layer calculation.

    Returns:
        list: A list of layers, where each layer is represented as a list
            containing the start and end depths of that layer.

    Raises:
        CamException: If the start depth is lower than the end depth.
    """

    if start_depth < end_depth:
        string = (
            "Start Depth Is Lower than End Depth.\n"
            "if You Have Set a Custom Depth End, It Must Be Lower than Depth Start,\n"
            "and Should Usually Be Negative.\nSet This in the CAM Operation Area Panel."
        )
        log.error("Start Depth Is Lower than End Depth.")
        raise CamException(string)

    if operation.use_layers:
        layers = []
        layer_count = ceil((start_depth - end_depth) / operation.stepdown)

        log.info("-")
        log.info("~ Getting Layer Data ~")
        log.info(f"Start Depth: {start_depth}")
        log.info(f"End Depth: {end_depth}")
        log.info(f"Layers: {layer_count}")
        log.info("-")

        layer_start = operation.max_z

        for x in range(0, layer_count):
            layer_end = round(
                max(start_depth - ((x + 1) * operation.stepdown), end_depth),
                6,
            )
            if int(layer_start * 10**8) != int(layer_end * 10**8):
                # it was possible that with precise same end of operation,
                # last layer was done 2x on exactly same level...
                layers.append([layer_start, layer_end])
            layer_start = layer_end
    else:
        layers = [[round(start_depth, 6), round(end_depth, 6)]]

    return layers


def chunks_to_mesh(chunks, o):
    """Convert sampled chunks into a mesh path for a given optimization object.

    This function takes a list of sampled chunks and converts them into a
    mesh path based on the specified optimization parameters. It handles
    different machine axes configurations and applies optimizations as
    needed. The resulting mesh is created in the Blender context, and the
    function also manages the lifting and dropping of the cutter based on
    the chunk positions.

    Args:
        chunks (list): A list of chunk objects to be converted into a mesh.
        o (object): An object containing optimization parameters and settings.

    Returns:
        None: The function creates a mesh in the Blender context but does not return a
            value.
    """

    t = time.time()
    scene = bpy.context.scene
    machine = scene.cam_machine
    vertices = []

    free_height = o.movement.free_height

    three_axis = o.machine_axes == "3"
    four_axis = o.machine_axes == "4"
    five_axis = o.machine_axes == "5"

    indexed_four_axis = four_axis and o.strategy_4_axis == "INDEXED"
    indexed_five_axis = five_axis and o.strategy_5_axis == "INDEXED"

    user_origin = (
        machine.starting_position.x,
        machine.starting_position.y,
        machine.starting_position.z,
    )

    default_origin = (
        0,
        0,
        free_height,
    )

    if three_axis:
        origin = user_origin if machine.use_position_definitions else default_origin
        vertices = [origin]

    if not three_axis:
        vertices_rotations = []

    if indexed_five_axis or indexed_four_axis:
        extend_chunks_5_axis(chunks, o)

    if o.array:
        array_chunks = []
        for x in range(0, o.array_x_count):
            for y in range(0, o.array_y_count):
                log.info(f"{x}, {y}")

                for chunk in chunks:
                    chunk = chunk.copy()
                    chunk.shift(
                        x * o.array_x_distance,
                        y * o.array_y_distance,
                        0,
                    )
                    array_chunks.append(chunk)
        chunks = array_chunks

    log.info("-")
    progress("Building Paths from Chunks")
    e = 0.0001
    lifted = True

    for chunk_index in range(0, len(chunks)):
        chunk = chunks[chunk_index]
        # TODO: there is a case where parallel+layers+zigzag ramps send empty chunks here...
        if chunk.count() > 0:
            if o.optimisation.optimize:
                chunk = optimize_chunk(chunk, o)

            # lift and drop
            if lifted:
                # did the cutter lift before? if yes, put a new position above of the first point of next chunk.
                if three_axis or indexed_five_axis or indexed_four_axis:
                    vertex = (
                        chunk.get_point(0)[0],
                        chunk.get_point(0)[1],
                        free_height,
                    )
                # otherwise, continue with the next chunk without lifting/dropping
                else:
                    vertex = chunk.startpoints[0]
                    vertices_rotations.append(chunk.rotations[0])
                vertices.append(vertex)

            # add whole chunk
            vertices.extend(chunk.get_points())

            # add rotations for n-axis
            if not three_axis:
                vertices_rotations.extend(chunk.rotations)

            lift = True
            # check if lifting should happen
            if chunk_index < len(chunks) - 1 and chunks[chunk_index + 1].count() > 0:
                # TODO: remake this for n axis, and this check should be somewhere else...
                last = Vector(chunk.get_point(-1))
                first = Vector(chunks[chunk_index + 1].get_point(0))
                vector = first - last

                vector_length = vector.length < o.distance_between_paths * 2.5
                vector_check = vector.z == 0 and vector_length
                parallel_cross = o.strategy in ["PARALLEL", "CROSS"]
                neighbouring_paths = (three_axis and parallel_cross and vector_check) or (
                    four_axis and vector_length
                )
                stepdown_by_cutting = abs(vector.x) < e and abs(vector.y) < e

                if neighbouring_paths or stepdown_by_cutting:
                    lift = False

            if lift:
                if three_axis or indexed_five_axis or indexed_four_axis:
                    vertex = (chunk.get_point(-1)[0], chunk.get_point(-1)[1], free_height)
                else:
                    vertex = chunk.startpoints[-1]
                    vertices_rotations.append(chunk.rotations[-1])
                vertices.append(vertex)
            lifted = lift

    if o.optimisation.use_exact and not o.optimisation.use_opencamlib:
        cleanup_bullet_collision(o)

    log.info(f"Path Calculation Time: {time.time() - t}")
    t = time.time()

    # Blender Object generation starts here:
    edges = []
    for a in range(0, len(vertices) - 1):
        edges.append((a, a + 1))

    path_name = scene.cam_names.path_name_full
    mesh = bpy.data.meshes.new(path_name)
    mesh.name = path_name
    mesh.from_pydata(vertices, edges, [])

    if path_name in scene.objects:
        scene.objects[path_name].data = mesh
        ob = scene.objects[path_name]
    else:
        ob = object_utils.object_data_add(bpy.context, mesh, operator=None)

    if not three_axis:
        # store rotations into shape keys, only way to store large arrays with correct floating point precision
        # - object/mesh attributes can only store array up to 32000 intems.
        ob.shape_key_add()
        ob.shape_key_add()
        shapek = mesh.shape_keys.key_blocks[1]
        shapek.name = "rotations"

        log.info(len(shapek.data))
        log.info(len(vertices_rotations))

        # TODO: optimize this. this is just rewritten too many times...
        for i, co in enumerate(vertices_rotations):
            shapek.data[i].co = co

    log.info(f"Path Object Generation Time: {time.time() - t}")
    log.info("-")

    ob.location = (0, 0, 0)
    ob.color = scene.cam_machine.path_color
    o.path_object_name = path_name

    bpy.context.collection.objects.unlink(ob)
    bpy.data.collections["Paths"].objects.link(ob)

    # parent the path object to source object if object mode
    if (o.geometry_source == "OBJECT") and o.parent_path_to_object:
        activate(o.objects[0])
        ob.select_set(state=True, view_layer=None)
        bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)
    else:
        ob.select_set(state=True, view_layer=None)


def check_min_z(o):
    """Check the minimum value based on the specified condition.

    This function evaluates the 'minz_from' attribute of the input object
    'o'. If 'minz_from' is set to 'MATERIAL', it returns the value of
    'min.z'. Otherwise, it returns the value of 'minz'.

    Args:
        o (object): An object that has attributes 'minz_from', 'min', and 'minz'.

    Returns:
        The minimum value, which can be either 'o.min.z' or 'o.min_z' depending
            on the condition.
    """
    if o.min_z_from == "MATERIAL":
        return o.min.z
    else:
        return o.min_z
