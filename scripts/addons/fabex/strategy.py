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

import shapely
from shapely.geometry import polygon as spolygon
from shapely.geometry import Point
from shapely import geometry as sgeometry
from shapely import affinity

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
def add_pocket(maxdepth, sname, new_cutter_diameter):
    """Add a pocket operation for the medial axis and profile cut.

    This function first deselects all objects in the scene and then checks
    for any existing medial pocket objects, deleting them if found. It
    verifies whether a medial pocket operation already exists in the CAM
    operations. If it does not exist, it creates a new pocket operation with
    the specified parameters. The function also modifies the selected
    object's silhouette offset based on the new cutter diameter.

    Args:
        maxdepth (float): The maximum depth of the pocket to be created.
        sname (str): The name of the object to which the pocket will be added.
        new_cutter_diameter (float): The diameter of the new cutter to be used.
    """

    bpy.ops.object.select_all(action="DESELECT")
    s = bpy.context.scene
    mpocket_exists = False

    # OBJECT name
    mp_ob_name = f"{sname}_medial_pocket"

    # Delete old Medial Pocket object, if one exists
    for ob in s.objects:
        if ob.name.startswith(mp_ob_name):
            ob.select_set(True)
            bpy.ops.object.delete()

    # OPERATION name
    mp_op_name = f"{sname}_MedialPocket"

    # Verify Medial Pocket Operation exists
    for op in s.cam_operations:
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
    m_ob.location.z = maxdepth

    # Create a Pocket Operation if it does not exist already
    if not mpocket_exists:
        s.cam_operations.add()
        o = s.cam_operations[-1]
        o.object_name = mp_ob_name
        s.cam_active_operation = len(s.cam_operations) - 1
        o.name = mp_op_name
        o.filename = o.name
        o.strategy = "POCKET"
        o.use_layers = False
        o.material.estimate_from_model = False
        o.material.size[2] = -maxdepth


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

    log.info("Operation: Cutout")

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
    cutter_offset = r if cutter_offset > r else cutter_offset
    # Add Skin for Profile
    cutter_offset += o.skin

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
        chunksFromCurve = []

        for ob in o.objects:
            chunksFromCurve.extend(curve_to_chunks(ob, o.use_modifiers))
    else:
        chunksFromCurve = []

        if o.cut_type == "ONLINE":
            p = get_object_outline(0, o, True)
        else:
            offset = True

            if o.cut_type == "INSIDE":
                offset = False

            p = get_object_outline(cutter_offset, o, offset)

            if o.outlines_count > 1:
                for i in range(1, o.outlines_count):
                    chunksFromCurve.extend(shapely_to_chunks(p, -1))
                    path_distance = o.distance_between_paths

                    if o.cut_type == "INSIDE":
                        path_distance *= -1
                    p = p.buffer(
                        distance=path_distance,
                        resolution=o.optimisation.circle_detail,
                        join_style=join,
                        mitre_limit=2,
                    )

        chunksFromCurve.extend(shapely_to_chunks(p, -1))

        if o.outlines_count > 1 and o.movement.insideout == "OUTSIDEIN":
            chunksFromCurve.reverse()

    chunksFromCurve = limit_chunks(chunksFromCurve, o)

    if not o.dont_merge:
        parent_child_poly(chunksFromCurve, chunksFromCurve, o)

    if o.outlines_count == 1:
        chunksFromCurve = await sort_chunks(chunksFromCurve, o)

    move_type = o.movement.type
    spin = o.movement.spindle_rotation
    climb_ccw = move_type == "CLIMB" and spin == "CCW"
    conventional_cw = move_type == "CONVENTIONAL" and spin == "CW"

    if climb_ccw or conventional_cw:
        for ch in chunksFromCurve:
            ch.reverse()

    # For simplicity, reverse once again when Inside cutting
    if o.cut_type == "INSIDE":
        for ch in chunksFromCurve:
            ch.reverse()

    layers = get_layers(
        o,
        o.max_z,
        check_min_z(o),
    )
    extendorder = []

    # If First Down is true, cut each shape from top to bottom,
    # if not, split shapes into layers by height, creating copies as
    # the same chunks will be on multiple layers
    if o.first_down:
        for chunk in chunksFromCurve:
            # A direction switch boolean check is needed to avoid cutter
            # lifting with open Chunks and "MEANDER" movement
            dir_switch = False

            for layer in layers:
                chunk_copy = chunk.copy()

                if dir_switch:
                    chunk_copy.reverse()
                extendorder.append([chunk_copy, layer])

                if (not chunk.closed) and o.movement.type == "MEANDER":
                    dir_switch = not dir_switch
    else:
        for layer in layers:
            for chunk in chunksFromCurve:
                extendorder.append([chunk.copy(), layer])

    # Set Z for all Chunks
    for chl in extendorder:
        chunk = chl[0]
        layer = chl[1]
        log.info(layer[1])
        chunk.set_z(layer[1])

    chunks = []

    # Add Bridges to Chunks
    if o.use_bridges:
        log.info("Using Bridges")
        remove_multiple(o.name + "_cut_bridges")
        log.info("Old Briddge Cut Removed")
        bridgeheight = min(o.max.z, o.min.z + abs(o.bridges_height))

        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]

            if layer[1] < bridgeheight:
                use_bridges(chunk, o)

    if o.profile_start > 0:
        log.info("Cutout Change Profile Start")
        for chl in extendorder:
            chunk = chl[0]

            if chunk.closed:
                chunk.change_path_start(o)

    # Lead in
    if o.lead_in > 0.0 or o.lead_out > 0:
        log.info("Cutout Lead-in")
        for chl in extendorder:
            chunk = chl[0]

            if chunk.closed:
                chunk.break_path_for_leadin_leadout(o)
                chunk.lead_contour(o)

    # Add Ramps or just Chunks
    if o.movement.ramp:
        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]

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
        for chl in extendorder:
            chunks.append(chl[0])

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

    log.info("Operation: Curve to Path")

    pathSamples = []
    get_operation_sources(o)

    if not o.onlycurves:
        raise CamException("All Objects Must Be Curves for This Operation.")

    for ob in o.objects:
        # Ensure Polylines are at least three points long
        subdivide_short_lines(ob)
        # Make the Chunks from the Curve
        pathSamples.extend(curve_to_chunks(ob))

    # Sort Chunks before sampling Path
    pathSamples = await sort_chunks(pathSamples, o)
    # Simplify Path Chunks
    pathSamples = chunks_refine(pathSamples, o)

    # Layers
    if o.use_layers:
        # layers is a list of lists [[0.00,l1],[l1,l2],[l2,l3]]
        # containing the start and end of each layer
        layers = get_layers(
            o,
            o.max_z,
            round(check_min_z(o), 6),
        )
        extendorder = []
        chunks = []

        # Include Layer information in Chunk list
        for layer in layers:
            for ch in pathSamples:
                extendorder.append([ch.copy(), layer])

        # Set offset Z for all chunks according to the layer information,
        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]
            log.info(f"Layer: {layer[1]}")
            chunk.offset_z(o.max_z * 2 - o.min_z + layer[1])
            # Limit Cut Depth to Operation Z Minimum
            chunk.clamp_z(o.min_z)
            # Limit Cut Height to Operation Safe Height
            chunk.clamp_max_z(o.movement.free_height)

        # Strip Layer information from extendorder and transfer them to Chunks
        for chl in extendorder:
            chunks.append(chl[0])

        chunks_to_mesh(chunks, o)  # finish by converting to mesh

    # No Layers, old Curve
    else:
        for ch in pathSamples:
            # Limit Cut Depth to Operation Z Minimum
            ch.clamp_z(o.min_z)
            # Limit Cut Height to Operation Safe Height
            ch.clamp_max_z(o.movement.free_height)
        chunks_to_mesh(pathSamples, o)


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

    log.info("Operation: Projected Curve")

    pathSamples = []
    chunks = []
    ob = bpy.data.objects[o.curve_source]
    pathSamples.extend(curve_to_chunks(ob))
    targetCurve = s.objects[o.curve_target]

    if targetCurve.type != "CURVE":
        raise CamException("Projection Target and Source Have to Be Curve Objects!")

    if 1:
        extend_up = 0.1
        extend_down = 0.04
        tsamples = curve_to_chunks(targetCurve)

        for chi, ch in enumerate(pathSamples):
            cht = tsamples[chi].get_points()
            ch.depth = 0
            ch_points = ch.get_points()

            for i, s in enumerate(ch_points):
                # move the points a bit
                ep = Vector(cht[i])
                sp = Vector(ch_points[i])
                # extend startpoint
                vecs = sp - ep
                vecs.normalize()
                vecs *= extend_up
                sp += vecs
                ch.startpoints.append(sp)
                # extend endpoint
                vece = sp - ep
                vece.normalize()
                vece *= extend_down
                ep -= vece
                ch.endpoints.append(ep)
                ch.rotations.append((0, 0, 0))
                vec = sp - ep
                ch.depth = min(ch.depth, -vec.length)
                ch_points[i] = sp.copy()

    ch.set_points(ch_points)
    layers = get_layers(o, 0, ch.depth)
    chunks.extend(sample_chunks_n_axis(o, pathSamples, layers))
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

    log.info("Operation: Pocket")

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

    chunksFromCurve = []
    angle = radians(o.parallel_pocket_angle)
    distance = o.distance_between_paths
    offset = -cutter_offset
    pocket_shape = ""
    n_angle = angle - pi / 2
    pr = get_object_outline(0, o, False)
    if o.pocket_type == "PARALLEL":
        if o.parallel_pocket_contour:
            offset = -(cutter_offset + distance / 2)
            p = pr.buffer(
                -cutter_offset,
                resolution=o.optimisation.circle_detail,
                join_style=join,
                mitre_limit=2,
            )
            nchunks = shapely_to_chunks(p, o.min.z)
            chunksFromCurve.extend(nchunks)

        crosshatch_result = generate_crosshatch(
            bpy.context,
            angle,
            distance,
            offset,
            pocket_shape,
            join,
            c_ob,
        )
        nchunks = shapely_to_chunks(crosshatch_result, o.min.z)
        chunksFromCurve.extend(nchunks)

        if o.parallel_pocket_crosshatch:
            crosshatch_result = generate_crosshatch(
                bpy.context,
                n_angle,
                distance,
                offset,
                pocket_shape,
                join,
                c_ob,
            )
            nchunks = shapely_to_chunks(crosshatch_result, o.min.z)
            chunksFromCurve.extend(nchunks)

    else:
        p = pr.buffer(
            -cutter_offset,
            resolution=o.optimisation.circle_detail,
            join_style=join,
            mitre_limit=2,
        )
        approxn = (min(o.max.x - o.min.x, o.max.y - o.min.y) / o.distance_between_paths) / 2
        log.info(f"Approximative: {approxn}")
        log.info(o.name)

        i = 0
        chunks = []
        lastchunks = []
        centers = None
        firstoutline = p  # for testing in the end.
        prest = p.buffer(-cutter_offset, o.optimisation.circle_detail)

        while not p.is_empty:
            if o.pocket_to_curve:
                # make a curve starting with _3dpocket
                shapely_to_curve("3dpocket", p, 0.0)

            nchunks = shapely_to_chunks(p, o.min.z)
            pnew = p.buffer(
                -o.distance_between_paths,
                o.optimisation.circle_detail,
                join_style=join,
                mitre_limit=2,
            )

            if pnew.is_empty:
                # test if the last curve will leave material
                pt = p.buffer(
                    -cutter_offset,
                    o.optimisation.circle_detail,
                    join_style=join,
                    mitre_limit=2,
                )

                if not pt.is_empty:
                    pnew = pt

            nchunks = limit_chunks(nchunks, o)
            chunksFromCurve.extend(nchunks)
            parent_child_distance(lastchunks, nchunks, o)
            lastchunks = nchunks
            percent = int(i / approxn * 100)
            progress("Outlining Polygons ", percent)
            p = pnew
            i += 1

    # TODO inside outside!

    move_type = o.movement.type
    spin = o.movement.spindle_rotation
    climb_cw = move_type == "CLIMB" and spin == "CW"
    climb_ccw = move_type == "CLIMB" and spin == "CCW"
    conventional_cw = move_type == "CONVENTIONAL" and spin == "CW"
    conventional_ccw = move_type == "CONVENTIONAL" and spin == "CCW"

    if climb_cw or conventional_ccw:
        for ch in chunksFromCurve:
            ch.reverse()

    chunksFromCurve = await sort_chunks(chunksFromCurve, o)
    chunks = []
    layers = get_layers(
        o,
        o.max_z,
        check_min_z(o),
    )

    for l in layers:
        lchunks = set_chunks_z(chunksFromCurve, l[1])

        if o.movement.ramp:
            for ch in lchunks:
                ch.zstart = l[0]
                ch.zend = l[1]

        # helix_enter first try here TODO: check if helix radius is not out of operation area.
        if o.movement.helix_enter:
            helix_radius = cutter_offset * o.movement.helix_diameter * 0.01
            # 90 percent of cutter radius
            helix_circumference = helix_radius * pi * 2
            revheight = helix_circumference * tan(o.movement.ramp_in_angle)

            for chi, ch in enumerate(lchunks):
                if not chunksFromCurve[chi].children:
                    # TODO:intercept closest next point when it should stay low
                    p = ch.get_point(0)
                    # first thing to do is to check if helix enter can really enter.
                    checkc = circle(helix_radius + cutter_offset, o.optimisation.circle_detail)
                    checkc = affinity.translate(checkc, p[0], p[1])
                    covers = False

                    for poly in o.silhouette.geoms:
                        if poly.contains(checkc):
                            covers = True
                            break

                    if covers:
                        revolutions = (l[0] - p[2]) / revheight
                        # log.debug(revolutions)
                        h = helix(helix_radius, o.optimisation.circle_detail, l[0], p, revolutions)
                        # invert helix if not the typical direction
                        if conventional_cw or climb_ccw:
                            nhelix = []
                            for v in h:
                                nhelix.append(
                                    (
                                        2 * p[0] - v[0],
                                        v[1],
                                        v[2],
                                    )
                                )
                            h = nhelix
                        ch.extend(h, at_index=0)

                    else:
                        o.info.warnings += "Helix entry did not fit! \n "
                        ch.closed = True
                        ch.ramp_zig_zag(l[0], l[1], o)

        # Arc retract here first try:
        # TODO: check for entry and exit point before actual computing... will be much better.
        if o.movement.retract_tangential:
            # TODO: fix this for CW and CCW!
            for chi, ch in enumerate(lchunks):
                if chunksFromCurve[chi].parents == [] or len(chunksFromCurve[chi].parents) == 1:
                    revolutions = 0.25
                    v1 = Vector(ch.get_point(-1))
                    i = -2
                    v2 = Vector(ch.get_point(i))
                    v = v1 - v2

                    while v.length == 0:
                        i = i - 1
                        v2 = Vector(ch.get_point(i))
                        v = v1 - v2

                    v.normalize()
                    rotangle = Vector((v.x, v.y)).angle_signed(Vector((1, 0)))
                    e = Euler((0, 0, pi / 2.0))  # TODO:#CW CLIMB!
                    v.rotate(e)
                    p = v1 + v * o.movement.retract_radius
                    center = p
                    p = (p.x, p.y, p.z)
                    # progress(str((v1,v,p)))
                    h = helix(
                        o.movement.retract_radius,
                        o.optimisation.circle_detail,
                        p[2] + o.movement.retract_height,
                        p,
                        revolutions,
                    )
                    # angle to rotate whole retract move
                    e = Euler((0, 0, rotangle + pi))
                    rothelix = []
                    c = []  # polygon for outlining and checking collisions.

                    for p in h:  # rotate helix to go from tangent of vector
                        v1 = Vector(p)
                        v = v1 - center
                        v.x = -v.x  # flip it here first...
                        v.rotate(e)
                        p = center + v
                        rothelix.append(p)
                        c.append((p[0], p[1]))

                    c = sgeometry.Polygon(c)
                    coutline = c.buffer(cutter_offset, o.optimisation.circle_detail)
                    # log.debug(h)
                    # log.debug(c)
                    # log.debug(coutline)
                    # polyToMesh(coutline,0)
                    rothelix.reverse()
                    covers = False

                    for poly in o.silhouette.geoms:
                        if poly.contains(coutline):
                            covers = True
                            break

                    if covers:
                        ch.extend(rothelix)

        chunks.extend(lchunks)

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(
                ch.zstart,
                ch.get_point(0)[2],
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

    log.info("Operation: Drill")

    chunks = []

    for ob in o.objects:
        activate(ob)
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
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

        l = ob.location

        if ob.type == "CURVE":
            for c in ob.data.splines:
                maxx, minx, maxy, miny, maxz, minz = -10000, 10000, -10000, 10000, -10000, 10000
                points = c.points if len(c.points) > 0 else c.bezier_points

                for p in points:
                    if o.drill_type == "ALL_POINTS":
                        chunks.append(
                            CamPathChunk(
                                [
                                    (
                                        p.co.x + l.x,
                                        p.co.y + l.y,
                                        p.co.z + l.z,
                                    )
                                ]
                            )
                        )
                    minx = min(p.co.x, minx)
                    maxx = max(p.co.x, maxx)
                    miny = min(p.co.y, miny)
                    maxy = max(p.co.y, maxy)
                    minz = min(p.co.z, minz)
                    maxz = max(p.co.z, maxz)

                cx = (maxx + minx) / 2
                cy = (maxy + miny) / 2
                cz = (maxz + minz) / 2
                center = (cx, cy)
                aspect = (maxx - minx) / (maxy - miny)

                if (
                    1.3 > aspect > 0.7 and o.drill_type == "MIDDLE_SYMETRIC"
                ) or o.drill_type == "MIDDLE_ALL":
                    chunks.append(
                        CamPathChunk(
                            [
                                (
                                    center[0] + l.x,
                                    center[1] + l.y,
                                    cz + l.z,
                                )
                            ]
                        )
                    )

        elif ob.type == "MESH":
            for v in ob.data.vertices:
                chunks.append(
                    CamPathChunk(
                        [
                            (
                                v.co.x + l.x,
                                v.co.y + l.y,
                                v.co.z + l.z,
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

    chunklayers = []
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
                newchunk = chunk.copy()
                newchunk.set_z(z)
                chunklayers.append(newchunk)
                # retract tool to maxz (operation depth start in ui)
                newchunk = chunk.copy()
                newchunk.set_z(o.max_z)
                chunklayers.append(newchunk)

    chunklayers = await sort_chunks(chunklayers, o)
    chunks_to_mesh(chunklayers, o)


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

    log.info("Operation: Medial Axis")

    remove_multiple("medialMesh")

    chunks = []

    gpoly = spolygon.Polygon()
    angle = o.cutter_tip_angle
    # Angle in Degrees
    slope = tan(pi * (90 - angle / 2) / 180)
    new_cutter_diameter = o.cutter_diameter
    m_o_ob = o.object_name

    if o.cutter_type == "VCARVE":
        angle = o.cutter_tip_angle
        # start the max depth calc from the "start depth" of the operation.
        maxdepth = o.max_z - slope * o.cutter_diameter / 2 - o.skin
        # don't cut any deeper than the "end depth" of the operation.
        if maxdepth < o.min_z:
            maxdepth = o.min_z
            # the effective cutter diameter can be reduced from it's max
            # since we will be cutting shallower than the original maxdepth
            # without this, the curve is calculated as if the diameter was at the original maxdepth and we get the bit
            # pulling away from the desired cut surface
            new_cutter_diameter = (maxdepth - o.max_z) / (-slope) * 2
    elif o.cutter_type == "BALLNOSE":
        maxdepth = -new_cutter_diameter / 2 - o.skin
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
        if ob.type == "CURVE" or ob.type == "FONT":
            resolutions_before.append(ob.data.resolution_u)
            if ob.data.resolution_u < 64:
                ob.data.resolution_u = 64

    polys = get_operation_silhouette(o)
    if isinstance(polys, list):
        if len(polys) == 1 and isinstance(polys[0], shapely.MultiPolygon):
            mpoly = polys[0]
        else:
            mpoly = sgeometry.MultiPolygon(polys)
    elif isinstance(polys, shapely.MultiPolygon):
        # just a multipolygon
        mpoly = polys
    else:
        raise CamException("Failed Getting Object Silhouette. Is Input Curve Closed?")

    mpoly_boundary = mpoly.boundary
    ipol = 0
    for poly in mpoly.geoms:
        ipol = ipol + 1

        schunks = shapely_to_chunks(poly, -1)

        schunks = chunks_refine_threshold(
            schunks,
            o.medial_axis_subdivision,
            o.medial_axis_threshold,
        )
        # chunks_refine(schunks,o)

        verts = []
        for ch in schunks:
            verts.extend(ch.get_points())

        nDupli, nZcolinear = unique(verts)
        nVerts = len(verts)
        log.info(f"{nDupli} Duplicate Points Ignored")
        log.info(f"{nZcolinear} Z Colinear Points Excluded")
        if nVerts < 3:
            log.info("Not Enough Points")
            return {"FINISHED"}

        # Check colinear
        xValues = [pt[0] for pt in verts]
        yValues = [pt[1] for pt in verts]
        if check_equal(xValues) or check_equal(yValues):
            log.info("Points Are Colinear")
            return {"FINISHED"}

        # Create diagram
        log.info(f"Tesselation... ({nVerts})Points)")
        xbuff, ybuff = 5, 5  # %
        zPosition = 0
        vertsPts = [Point(vert[0], vert[1], vert[2]) for vert in verts]

        pts, edgesIdx = compute_voronoi_diagram(
            vertsPts,
            xbuff,
            ybuff,
            polygonsOutput=False,
            formatOutput=True,
        )

        newIdx = 0
        vertr = []
        filteredPts = []
        log.info("Filter Points")
        ipts = 0

        for p in pts:
            ipts = ipts + 1

            if ipts % 500 == 0:
                sys.stdout.write("\r")
                # the exact output you're looking for:
                prog_message = f"Points: {ipts} / {len(pts)} {round(100 * ipts / len(pts))}%\n"
                sys.stdout.write(prog_message)
                sys.stdout.flush()

            if not poly.contains(sgeometry.Point(p)):
                vertr.append((True, -1))
            else:
                vertr.append((False, newIdx))

                if o.cutter_type == "VCARVE":
                    # start the z depth calc from the "start depth" of the operation.
                    z = o.max_z - mpoly.boundary.distance(sgeometry.Point(p)) * slope

                    if z < maxdepth:
                        z = maxdepth

                elif o.cutter_type == "BALL" or o.cutter_type == "BALLNOSE":
                    d = mpoly_boundary.distance(sgeometry.Point(p))
                    r = new_cutter_diameter / 2.0

                    if d >= r:
                        z = -r
                    else:
                        z = -r + sqrt(r * r - d * d)
                else:
                    z = 0  #

                filteredPts.append((p[0], p[1], z))
                newIdx += 1

        log.info("Filter Edges")
        filteredEdgs = []
        ledges = []

        for e in edgesIdx:
            do = True

            # Exclude Edges with already excluded Points
            if vertr[e[0]][0]:
                do = False
            elif vertr[e[1]][0]:
                do = False
            if do:
                filteredEdgs.append(
                    (
                        vertr[e[0]][1],
                        vertr[e[1]][1],
                    )
                )
                ledges.append(
                    sgeometry.LineString(
                        (
                            filteredPts[vertr[e[0]][1]],
                            filteredPts[vertr[e[1]][1]],
                        )
                    )
                )

        bufpoly = poly.buffer(-new_cutter_diameter / 2, resolution=64)
        lines = shapely.ops.linemerge(ledges)

        if bufpoly.geom_type == "Polygon" or bufpoly.geom_type == "MultiPolygon":
            lines = lines.difference(bufpoly)
            chunks.extend(shapely_to_chunks(bufpoly, maxdepth))

        chunks.extend(shapely_to_chunks(lines, 0))

        # Generate a Mesh from the Medial calculations
        if o.add_mesh_for_medial:
            shapely_to_curve("medialMesh", lines, 0.0)
            bpy.ops.object.convert(target="MESH")

    oi = 0
    for ob in o.objects:
        if ob.type == "CURVE" or ob.type == "FONT":
            ob.data.resolution_u = resolutions_before[oi]
            oi += 1

    # bpy.ops.object.join()
    chunks = await sort_chunks(chunks, o)
    layers = get_layers(
        o,
        o.max_z,
        o.min.z,
    )
    chunklayers = []

    for layer in layers:
        for chunk in chunks:
            if chunk.is_below_z(layer[0]):
                newchunk = chunk.copy()
                newchunk.clamp_z(layer[1])
                chunklayers.append(newchunk)

    if o.first_down:
        chunklayers = await sort_chunks(chunklayers, o)

    if o.add_mesh_for_medial:  # make curve instead of a path
        join_multiple("medialMesh")

    chunks_to_mesh(chunklayers, o)
    # add pocket operation for medial if add pocket checked
    if o.add_pocket_for_medial:
        # export medial axis parameter to pocket op
        add_pocket(maxdepth, m_o_ob, new_cutter_diameter)


def get_layers(operation, startdepth, enddepth):
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
        startdepth (float): The starting depth for layer calculation.
        enddepth (float): The ending depth for layer calculation.

    Returns:
        list: A list of layers, where each layer is represented as a list
            containing the start and end depths of that layer.

    Raises:
        CamException: If the start depth is lower than the end depth.
    """

    if startdepth < enddepth:
        string = (
            "Start Depth Is Lower than End Depth.\n"
            "if You Have Set a Custom Depth End, It Must Be Lower than Depth Start,\n"
            "and Should Usually Be Negative.\nSet This in the CAM Operation Area Panel."
        )
        log.error("Start Depth Is Lower than End Depth.")
        raise CamException(string)

    if operation.use_layers:
        layers = []
        n = ceil((startdepth - enddepth) / operation.stepdown)

        log.info(f"Start Depth: {startdepth}")
        log.info(f"End Depth: {enddepth}")
        log.info(f"Layers: {n}")

        layerstart = operation.max_z

        for x in range(0, n):
            layerend = round(
                max(startdepth - ((x + 1) * operation.stepdown), enddepth),
                6,
            )
            if int(layerstart * 10**8) != int(layerend * 10**8):
                # it was possible that with precise same end of operation,
                # last layer was done 2x on exactly same level...
                layers.append([layerstart, layerend])
            layerstart = layerend
    else:
        layers = [[round(startdepth, 6), round(enddepth, 6)]]

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
    s = bpy.context.scene
    m = s.cam_machine
    verts = []

    free_height = o.movement.free_height

    three_axis = o.machine_axes == "3"
    four_axis = o.machine_axes == "4"
    five_axis = o.machine_axes == "5"

    indexed_four_axis = four_axis and o.strategy_4_axis == "INDEXED"
    indexed_five_axis = five_axis and o.strategy_5_axis == "INDEXED"

    if three_axis:
        if m.use_position_definitions:
            origin = (
                m.starting_position.x,
                m.starting_position.y,
                m.starting_position.z,
            )
        else:
            origin = (
                0,
                0,
                free_height,
            )
        verts = [origin]

    if not three_axis:
        verts_rotations = []

    if indexed_five_axis or indexed_four_axis:
        extend_chunks_5_axis(chunks, o)

    if o.array:
        nchunks = []
        for x in range(0, o.array_x_count):
            for y in range(0, o.array_y_count):
                log.info(f"{x}, {y}")
                for ch in chunks:
                    ch = ch.copy()
                    ch.shift(
                        x * o.array_x_distance,
                        y * o.array_y_distance,
                        0,
                    )
                    nchunks.append(ch)
        chunks = nchunks

    progress("Building Paths from Chunks")
    e = 0.0001
    lifted = True

    for chi in range(0, len(chunks)):
        ch = chunks[chi]
        # TODO: there is a case where parallel+layers+zigzag ramps send empty chunks here...
        if ch.count() > 0:
            # log.debug(len(ch.points))
            nverts = []
            if o.optimisation.optimize:
                ch = optimize_chunk(ch, o)

            # lift and drop
            if lifted:
                # did the cutter lift before? if yes, put a new position above of the first point of next chunk.
                if three_axis or indexed_five_axis or indexed_four_axis:
                    v = (ch.get_point(0)[0], ch.get_point(0)[1], free_height)
                else:  # otherwise, continue with the next chunk without lifting/dropping
                    v = ch.startpoints[0]  # startpoints=retract points
                    verts_rotations.append(ch.rotations[0])
                verts.append(v)

            # add whole chunk
            verts.extend(ch.get_points())

            # add rotations for n-axis
            if not three_axis:
                verts_rotations.extend(ch.rotations)

            lift = True
            # check if lifting should happen
            if chi < len(chunks) - 1 and chunks[chi + 1].count() > 0:
                # TODO: remake this for n axis, and this check should be somewhere else...
                last = Vector(ch.get_point(-1))
                first = Vector(chunks[chi + 1].get_point(0))
                vect = first - last
                vector_length = vect.length < o.distance_between_paths * 2.5
                vector_check = vect.z == 0 and vector_length
                parallel_cross = o.strategy in ["PARALLEL", "CROSS"]

                if (three_axis and parallel_cross and vector_check) or (
                    four_axis and vector_length
                ):
                    # case of neighbouring paths
                    lift = False
                # case of stepdown by cutting.
                if abs(vect.x) < e and abs(vect.y) < e:
                    lift = False

            if lift:
                if three_axis or indexed_five_axis or indexed_four_axis:
                    v = (ch.get_point(-1)[0], ch.get_point(-1)[1], free_height)
                else:
                    v = ch.startpoints[-1]
                    verts_rotations.append(ch.rotations[-1])
                verts.append(v)
            lifted = lift

    if o.optimisation.use_exact and not o.optimisation.use_opencamlib:
        cleanup_bullet_collision(o)

    log.info(f"{time.time() - t}")
    t = time.time()

    # Blender Object generation starts here:
    edges = []
    for a in range(0, len(verts) - 1):
        edges.append((a, a + 1))

    oname = s.cam_names.path_name_full
    mesh = bpy.data.meshes.new(oname)
    mesh.name = oname
    mesh.from_pydata(verts, edges, [])

    if oname in s.objects:
        s.objects[oname].data = mesh
        ob = s.objects[oname]
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
        log.info(len(verts_rotations))

        # TODO: optimize this. this is just rewritten too many times...
        for i, co in enumerate(verts_rotations):
            shapek.data[i].co = co

    log.info(f"{time.time() - t}")

    ob.location = (0, 0, 0)
    ob.color = s.cam_machine.path_color
    o.path_object_name = oname

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
