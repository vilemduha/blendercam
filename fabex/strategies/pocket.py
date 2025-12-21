from math import (
    pi,
    radians,
    tan,
)

from shapely import affinity
from shapely.geometry import Polygon

import bpy
from mathutils import Euler, Vector

from ..operators.curve_create_ops import generate_crosshatch

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    limit_chunks,
    sort_chunks,
    set_chunks_z,
)
from ..utilities.geom_utils import (
    circle,
    helix,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import (
    check_min_z,
    get_layers,
    get_move_and_spin,
)
from ..utilities.parent_utils import parent_child_distance
from ..utilities.shapely_utils import (
    shapely_to_curve,
    shapely_to_chunks,
)
from ..utilities.silhouette_utils import get_object_outline
from ..utilities.simple_utils import (
    activate,
    join_multiple,
    progress,
    remove_multiple,
)


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
    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)

    if climb_CW or conventional_CCW:
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
