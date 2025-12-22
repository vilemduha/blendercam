from math import (
    pi,
    sqrt,
    tan,
)
import sys

from shapely.geometry import (
    LineString,
    MultiPolygon,
    Point,
)
from shapely.ops import linemerge

import bpy

from ..exception import CamException

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    chunks_refine_threshold,
    sort_chunks,
)
from ..utilities.compare_utils import check_equal, unique
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_layers
from ..utilities.shapely_utils import (
    shapely_to_curve,
    shapely_to_chunks,
)
from ..utilities.silhouette_utils import get_operation_silhouette
from ..utilities.simple_utils import (
    activate,
    join_multiple,
    remove_multiple,
)
from ..utilities.strategy_utils import add_pocket
from ..utilities.voronoi_utils import compute_voronoi_diagram


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

    # Start the Max Depth calc from the "Start Depth" of the Operation.
    # Don't cut any deeper than the "End Depth" of the Operation.
    # The effective Cutter Diameter can be reduced from it's max
    # since we will be cutting shallower than the original `max_depth`
    # without this, the Curve is calculated as if the diameter was at
    # the original `max_depth` and we get the bit pulling away from the
    # desired cut surface
    max_depth = (
        -new_cutter_diameter / 2 - o.skin
        if o.cutter_type == "BALLNOSE"
        else (
            o.max_z - slope * o.cutter_diameter / 2 - o.skin
            if o.cutter_type == "VCARVE"
            else o.min_z if max_depth < o.min_z else None
        )
    )

    if max_depth is None:
        raise CamException("Only Ballnose and V-carve Cutters Are Supported for Medial Axis.")

    for ob in o.objects:
        if ob.type == "CURVE":
            if ob.data.splines and ob.data.splines[0].type == "BEZIER":
                activate(ob)
                bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
            else:
                bpy.ops.object.curve_remove_doubles()

    # remember resolutions of curves, to refine them,
    # otherwise medial axis computation yields too many branches in curved parts
    resolutions_before = [
        ob.data.resolution_u if ob.data.resolution_u < 64 else 64
        for ob in o.objects
        if ob.type in ["CURVE", "FONT"]
    ]

    silhouette_polygon = get_operation_silhouette(o)
    silhouette_is_list = isinstance(silhouette_polygon, list)
    silhouette_is_multipolygon = isinstance(silhouette_polygon, MultiPolygon)

    multipolygon = (
        silhouette_polygon
        if silhouette_is_multipolygon
        else (
            silhouette_polygon[0]
            if silhouette_is_list
            and len(silhouette_polygon) == 1
            and isinstance(silhouette_polygon[0], MultiPolygon)
            else MultiPolygon(silhouette_polygon) if silhouette_is_list else None
        )
    )

    if multipolygon is None:
        raise CamException("Failed Getting Object Silhouette. Is Input Curve Closed?")

    multipolygon_boundary = multipolygon.boundary
    multipolygon_geometry = multipolygon.geoms

    vertices = []

    for polygon_index, polygon in enumerate(multipolygon_geometry):
        polygon_index += 1

        silhouette_chunks = shapely_to_chunks(polygon, -1)
        silhouette_chunks = chunks_refine_threshold(
            silhouette_chunks,
            o.medial_axis_subdivision,
            o.medial_axis_threshold,
        )

        # chunk_points = [chunk.get_points() for chunk in silhouette_chunks]
        # vertices = [point for point in chunk_points]

        for chunk in silhouette_chunks:
            vertices.extend(chunk.get_points())

        duplicate_point_count, z_colinear_point_count = unique(vertices)
        vertex_count = len(vertices)

        log.info("~ Exclude Points ~")
        log.info(f"Duplicate: {duplicate_point_count}")
        log.info(f"Z Colinear: {z_colinear_point_count}")

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

        log.info("Filtering Points...")

        newIdx = 0
        point_count = len(points)
        vertr = [
            (True, -1) if polygon.contains(Point(point)) else (False, newIdx) for point in points
        ]
        filtered_points = []

        for point_index, point in enumerate(points):
            point_index += 1

            if point_index % 500 == 0:
                sys.stdout.write("\r")
                # the exact output you're looking for:
                prog_message = f"Points: {point_index}/{point_count} - {round(100 * point_index / point_count)}%"
                sys.stdout.write(prog_message)
                sys.stdout.flush()

            if o.cutter_type == "VCARVE":
                # start the z depth calc from the "start depth" of the operation.
                z = o.max_z - multipolygon.boundary.distance(Point(point)) * slope
                z = max_depth if z < max_depth else z

            elif o.cutter_type == "BALL" or o.cutter_type == "BALLNOSE":
                d = multipolygon_boundary.distance(Point(point))
                r = new_cutter_diameter / 2.0
                z = -r if d >= r else -r + sqrt(r * r - d * d)
            else:
                z = 0

            filtered_points.append((point[0], point[1], z))
            newIdx += 1

        log.info("-")
        log.info("Filtering Edges...")
        log.info("-")

        filtered_edges = [
            (
                vertr[edge[0]][1],
                vertr[edge[1]][1],
            )
            for edge in edges
            if not vertr[edge[0]][0] and not vertr[edge[1]][0]
        ]
        line_edges = [
            LineString(
                (
                    filtered_points[vertr[edge[0]][1]],
                    filtered_points[vertr[edge[1]][1]],
                )
            )
            for edge in edges
            if not vertr[edge[0]][0] and not vertr[edge[1]][0]
        ]

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
    chunk_layers = (
        await sort_chunks(chunk_layers, o)
        if o.first_down
        else [
            chunk.copy().clamp_z(layer[1])
            for chunk in chunks
            for layer in layers
            if chunk.is_below_z(layer[0])
        ]
    )

    # for layer in layers:
    #     for chunk in chunks:
    #         if chunk.is_below_z(layer[0]):
    #             new_chunk = chunk.copy()
    #             new_chunk.clamp_z(layer[1])
    #             chunk_layers.append(new_chunk)

    # if o.first_down:
    #     chunk_layers = await sort_chunks(chunk_layers, o)

    if o.add_mesh_for_medial:  # make curve instead of a path
        join_multiple("medialMesh")

    chunks_to_mesh(chunk_layers, o)
    # add pocket operation for medial if add pocket checked
    if o.add_pocket_for_medial:
        # export medial axis parameter to pocket op
        add_pocket(max_depth, m_o_ob, new_cutter_diameter)
