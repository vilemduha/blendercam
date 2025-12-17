"""Fabex 'toolpath.py' © 2012 Vilem Novak

Generate toolpaths from path chunks.
"""

# G-code Generaton
from math import (
    ceil,
    floor,
)
import time

from shapely.geometry import Polygon

import bpy

from . import strategy
from .bridges import use_bridges
from .cam_chunk import (
    curve_to_chunks,
    limit_chunks,
    chunks_coherency,
    shapely_to_chunks,
    sample_chunks,
    sample_chunks_n_axis,
    get_operation_silhouette,
    get_ambient,
    connect_chunks_low,
    sort_chunks,
    oclGetWaterline,
    image_to_shapely,
    crazy_stroke_image_binary,
    get_offset_image_cavities,
)
from .exception import CamException
from .constants import (
    USE_PROFILER,
)
from .exception import CamException
from .pattern import get_path_pattern, get_path_pattern_4_axis

from .utilities.async_utils import progress_async
from .utilities.bounds_utils import get_bounds
from .utilities.chunk_utils import (
    chunks_refine,
    parent_child_distance,
)
from .utilities.image_utils import (
    prepare_area,
)
from .utilities.index_utils import (
    cleanup_indexed,
    prepare_indexed,
)
from .utilities.logging_utils import log
from .utilities.operation_utils import (
    get_operation_sources,
    get_change_data,
)
from .utilities.simple_utils import (
    progress,
)


async def get_path(context, operation):
    """Calculate the path for a given operation in a specified context.

    This function performs various calculations to determine the path based
    on the operation's parameters and context. It checks for changes in the
    operation's data and updates relevant tags accordingly. Depending on the
    number of machine axes specified in the operation, it calls different
    functions to handle 3-axis, 4-axis, or 5-axis operations. Additionally,
    if automatic export is enabled, it exports the generated G-code path.

    Args:
        context: The context in which the operation is being performed.
        operation: An object representing the operation with various
            attributes such as machine_axes, strategy, and
            auto_export.
    """
    # should do all path calculations.
    t = time.process_time()

    if operation.feedrate > context.scene.cam_machine.feedrate_max:
        raise CamException("Operation Feedrate is greater than Machine Maximum!")

    # these tags are for caching of some of the results. Not working well still
    # - although it can save a lot of time during calculation...

    chd = get_change_data(operation)

    if operation.change_data != chd:  # or 1:
        operation.update_offset_image_tag = True
        operation.update_z_buffer_image_tag = True
        operation.change_data = chd

    operation.update_silhouette_tag = True
    operation.update_ambient_tag = True
    operation.update_bullet_collision_tag = True

    get_operation_sources(operation)

    operation.info.warnings = ""
    check_memory_limit(operation)

    log.info(f"Operation Axes: {operation.machine_axes}")

    if operation.machine_axes == "3":
        if USE_PROFILER == True:  # profiler
            import cProfile

            pr = cProfile.Profile()
            pr.enable()
            await get_path_3_axis(context, operation)
            pr.disable()
            pr.dump_stats(time.strftime("Fabex_%Y%m%d_%H%M.prof"))
        else:
            await get_path_3_axis(context, operation)

    elif (operation.machine_axes == "5" and operation.strategy_5_axis == "INDEXED") or (
        operation.machine_axes == "4" and operation.strategy_4_axis == "INDEXED"
    ):
        # 5 axis operations are now only 3 axis operations that get rotated...
        operation.orientation = prepare_indexed(operation)  # TODO RENAME THIS

        await get_path_3_axis(context, operation)  # TODO RENAME THIS

        cleanup_indexed(operation)  # TODO RENAME THIS
    # transform5axisIndexed
    elif operation.machine_axes == "4":
        await get_path_4_axis(context, operation)

    # export gcode if automatic.
    if operation.auto_export:
        path_name = context.scene.cam_names.path_name_full
        if bpy.data.objects.get(path_name) is None:
            return
        p = bpy.data.objects[path_name]
        name = operation.name if operation.link_operation_file_names else operation.filename
        export_gcode_path(name, [p.data], [operation])

    operation.changed = False
    t1 = time.process_time() - t
    progress("Total Time: ", t1)


# this is the main function.
# FIXME: split strategies into separate file!
async def get_path_3_axis(context, operation):
    """Generate a machining path based on the specified operation strategy.

    This function evaluates the provided operation's strategy and generates
    the corresponding machining path. It supports various strategies such as
    'CUTOUT', 'CURVE', 'PROJECTED_CURVE', 'POCKET', and others. Depending on
    the strategy, it performs specific calculations and manipulations on the
    input data to create a path that can be used for machining operations.
    The function handles different strategies by calling appropriate methods
    from the `strategy` module and processes the path samples accordingly.
    It also manages the generation of chunks, which represent segments of
    the machining path, and applies any necessary transformations based on
    the operation's parameters.

    Args:
        context (bpy.context): The Blender context containing scene information.
        operation (Operation): An object representing the machining operation,
            which includes strategy and other relevant parameters.

    Returns:
        None: This function does not return a value but modifies the state of
        the operation and context directly.
    """

    s = bpy.context.scene
    o = operation
    get_bounds(o)
    tw = time.time()

    if o.strategy == "CUTOUT":
        await strategy.cutout(o)

    elif o.strategy == "CURVE":
        await strategy.curve(o)

    elif o.strategy == "PROJECTED_CURVE":
        await strategy.project_curve(s, o)

    elif o.strategy == "POCKET":
        await strategy.pocket(o)

    elif o.strategy in [
        "PARALLEL",
        "CROSS",
        "BLOCK",
        "SPIRAL",
        "CIRCLES",
        "OUTLINEFILL",
        "CARVE",
        "PENCIL",
        "CRAZY",
    ]:
        if o.strategy == "CARVE":
            pathSamples = []
            ob = bpy.data.objects[o.curve_source]
            pathSamples.extend(curve_to_chunks(ob))
            # sort before sampling
            pathSamples = await sort_chunks(pathSamples, o)
            pathSamples = chunks_refine(pathSamples, o)
        elif o.strategy == "PENCIL":
            await prepare_area(o)
            get_ambient(o)
            pathSamples = get_offset_image_cavities(o, o.offset_image)
            pathSamples = limit_chunks(pathSamples, o)
            # sort before sampling
            pathSamples = await sort_chunks(pathSamples, o)
        elif o.strategy == "CRAZY":
            await prepare_area(o)
            # pathSamples = crazyStrokeImage(o)
            # this kind of worked and should work:
            millarea = o.zbuffer_image < o.min_z + 0.000001
            avoidarea = o.offset_image > o.min_z + 0.000001

            pathSamples = crazy_stroke_image_binary(o, millarea, avoidarea)
            #####
            pathSamples = await sort_chunks(pathSamples, o)
            pathSamples = chunks_refine(pathSamples, o)

        else:
            if o.strategy == "OUTLINEFILL":
                get_operation_silhouette(o)

            pathSamples = get_path_pattern(o)

            if o.strategy == "OUTLINEFILL":
                pathSamples = await sort_chunks(pathSamples, o)
                # have to be sorted once before, because of the parenting inside of samplechunks

            if o.strategy in ["BLOCK", "SPIRAL", "CIRCLES"]:
                pathSamples = await connect_chunks_low(pathSamples, o)

        chunks = []
        layers = strategy.get_layers(o, o.max_z, o.min.z)

        log.info(f"Sampling Object: {o.name}")
        chunks.extend(await sample_chunks(o, pathSamples, layers))
        log.info("Sampling Finished Successfully")

        if o.strategy == "PENCIL":
            chunks = chunks_coherency(chunks)
            log.info("Coherency Check")

        if o.strategy in ["PARALLEL", "CROSS", "PENCIL", "OUTLINEFILL"]:
            log.info("Sorting")
            chunks = await sort_chunks(chunks, o)
            if o.strategy == "OUTLINEFILL":
                chunks = await connect_chunks_low(chunks, o)
        if o.movement.ramp:
            for ch in chunks:
                ch.ramp_zig_zag(ch.zstart, None, o)

        if o.strategy == "CARVE":
            for ch in chunks:
                ch.offset_z(-o.carve_depth)

        if o.use_bridges:
            log.info(chunks)
            for bridge_chunk in chunks:
                use_bridges(bridge_chunk, o)

        strategy.chunks_to_mesh(chunks, o)

    elif o.strategy == "WATERLINE" and o.optimisation.use_opencamlib:
        get_ambient(o)
        chunks = []
        await oclGetWaterline(o, chunks)
        chunks = limit_chunks(chunks, o)
        if (o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW") or (
            o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW"
        ):
            for ch in chunks:
                ch.reverse()

        strategy.chunks_to_mesh(chunks, o)

    elif o.strategy == "WATERLINE" and not o.optimisation.use_opencamlib:
        topdown = True
        chunks = []
        await progress_async("Retrieving Object Slices")
        await prepare_area(o)
        layerstep = 1000000000
        if o.use_layers:
            layerstep = floor(o.stepdown / o.slice_detail)
            if layerstep == 0:
                layerstep = 1

        # for projection of filled areas
        layerstart = o.max.z  #
        layerend = o.min.z  #
        layers = [[layerstart, layerend]]
        #######################
        nslices = ceil(abs((o.min_z - o.max_z) / o.slice_detail))
        lastslice = Polygon()  # polyversion
        layerstepinc = 0

        slicesfilled = 0
        get_ambient(o)

        for h in range(0, nslices):
            layerstepinc += 1
            slicechunks = []
            # lower the layer by the skin value so the slice gets done at the tip of the tool
            z = o.min_z + h * o.slice_detail - o.skin
            if h == 0:
                z += 0.0000001
                # if people do mill flat areas, this helps to reach those...
                # otherwise first layer would actually be one slicelevel above min z.

            islice = o.offset_image > z
            slicepolys = image_to_shapely(o, islice, with_border=True)

            poly = Polygon()  # polygversion
            lastchunks = []

            for p in slicepolys.geoms:
                poly = poly.union(p)  # polygversion TODO: why is this added?
                nchunks = shapely_to_chunks(p, z + o.skin)
                nchunks = limit_chunks(nchunks, o, force=True)
                lastchunks.extend(nchunks)
                slicechunks.extend(nchunks)
            if len(slicepolys.geoms) > 0:
                slicesfilled += 1

            #
            if o.waterline_fill:
                layerstart = min(o.max_z, z + o.slice_detail)  #
                layerend = max(o.min.z, z - o.slice_detail)  #
                layers = [[layerstart, layerend]]
                #####################################
                # fill top slice for normal and first for inverse, fill between polys
                if not lastslice.is_empty or (
                    o.inverse and not poly.is_empty and slicesfilled == 1
                ):
                    restpoly = None
                    if not lastslice.is_empty:  # between polys
                        if o.inverse:
                            restpoly = poly.difference(lastslice)
                        else:
                            restpoly = lastslice.difference(poly)

                    if (not o.inverse and poly.is_empty and slicesfilled > 0) or (
                        o.inverse and not poly.is_empty and slicesfilled == 1
                    ):
                        # first slice fill
                        restpoly = lastslice

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths, resolution=o.optimisation.circle_detail
                    )

                    fillz = z
                    i = 0
                    while not restpoly.is_empty:
                        nchunks = shapely_to_chunks(restpoly, fillz + o.skin)
                        # project paths TODO: path projection during waterline is not working
                        if o.waterline_project:
                            nchunks = chunks_refine(nchunks, o)
                            nchunks = await sample_chunks(o, nchunks, layers)

                        nchunks = limit_chunks(nchunks, o, force=True)
                        #########################
                        slicechunks.extend(nchunks)
                        parent_child_distance(lastchunks, nchunks, o)
                        lastchunks = nchunks
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths, resolution=o.optimisation.circle_detail
                        )

                        i += 1

                i = 0
                #  fill layers and last slice, last slice with inverse is not working yet
                #  - inverse millings end now always on 0 so filling ambient does have no sense.
                if (
                    (slicesfilled > 0 and layerstepinc == layerstep)
                    or (not o.inverse and not poly.is_empty and slicesfilled == 1)
                    or (o.inverse and poly.is_empty and slicesfilled > 0)
                ):
                    fillz = z
                    layerstepinc = 0

                    bound_rectangle = o.ambient
                    restpoly = bound_rectangle.difference(poly)
                    if o.inverse and poly.is_empty and slicesfilled > 0:
                        restpoly = bound_rectangle.difference(lastslice)

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths, resolution=o.optimisation.circle_detail
                    )

                    i = 0

                    while not restpoly.is_empty:
                        nchunks = shapely_to_chunks(restpoly, fillz + o.skin)
                        #########################
                        nchunks = limit_chunks(nchunks, o, force=True)
                        slicechunks.extend(nchunks)
                        parent_child_distance(lastchunks, nchunks, o)
                        lastchunks = nchunks
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths, resolution=o.optimisation.circle_detail
                        )
                        i += 1

                percent = int(h / nslices * 100)
                await progress_async("Waterline Layers", percent)
                lastslice = poly

            if (o.movement.type == "CONVENTIONAL" and o.movement.spindle_rotation == "CCW") or (
                o.movement.type == "CLIMB" and o.movement.spindle_rotation == "CW"
            ):
                for chunk in slicechunks:
                    chunk.reverse()
            slicechunks = await sort_chunks(slicechunks, o)
            if topdown:
                slicechunks.reverse()
            # project chunks in between

            chunks.extend(slicechunks)
        if topdown:
            chunks.reverse()
        strategy.chunks_to_mesh(chunks, o)

    elif o.strategy == "DRILL":
        await strategy.drill(o)

    elif o.strategy == "MEDIAL_AXIS":
        await strategy.medial_axis(o)

    await progress_async(f"Done", time.time() - tw, "s")


async def get_path_4_axis(context, operation):
    """Generate a path for a specified axis based on the given operation.

    This function retrieves the bounds of the operation and checks the
    strategy associated with the axis. If the strategy is one of the
    specified types ('PARALLELR', 'PARALLEL', 'HELIX', 'CROSS'), it
    generates path samples and processes them into chunks for meshing. The
    function utilizes various helper functions to achieve this, including
    obtaining layers and sampling chunks.

    Args:
        context: The context in which the operation is executed.
        operation: An object that contains the strategy and other
            necessary parameters for generating the path.

    Returns:
        None: This function does not return a value but modifies
            the state of the operation by processing chunks for meshing.
    """

    o = operation
    get_bounds(o)
    if o.strategy_4_axis in ["PARALLELR", "PARALLEL", "HELIX", "CROSS"]:
        path_samples = get_path_pattern_4_axis(o)

        depth = path_samples[0].depth
        chunks = []

        layers = strategy.get_layers(o, 0, depth)

        chunks.extend(await sample_chunks_n_axis(o, path_samples, layers))
        strategy.chunks_to_mesh(chunks, o)
