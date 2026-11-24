from math import (
    ceil,
    sqrt,
)

from shapely.geometry import Polygon

from ..utilities.async_utils import progress_async
from ..utilities.chunk_utils import (
    chunks_refine,
    chunks_to_mesh,
    limit_chunks,
    sample_chunks,
    sort_chunks,
)
from ..utilities.image_shapely_utils import image_to_shapely
from ..utilities.image_utils import prepare_area
from ..utilities.logging_utils import heading, log
from ..utilities.operation_utils import (
    get_ambient,
    get_layers,
    get_move_and_spin,
)
from ..utilities.parent_utils import parent_child_distance
from ..utilities.shapely_utils import shapely_to_chunks
from ..utilities.waterline_utils import oclGetWaterline


async def waterline(o):
    log.info(heading("Strategy: Waterline"))

    climb_CW, _climb_CCW, _conventional_CW, conventional_CCW = get_move_and_spin(o)

    if o.optimisation.use_opencamlib:
        get_ambient(o)
        chunks = []
        await oclGetWaterline(o, chunks)
        chunks = limit_chunks(chunks, o)

        if climb_CW or conventional_CCW:
            for ch in chunks:
                ch.reverse()

        chunks_to_mesh(chunks, o)

    else:
        topdown = True
        chunks = []
        await progress_async("Retrieving Object Slices")
        await prepare_area(o)

        if o.use_layers:
            macro_layers = get_layers(o, o.max_z, o.min_z)  # top-down: [[start, end], ...]
            layer_boundaries = {round(layer_end, 6) for (_, layer_end) in macro_layers}

            z_levels = []
            for layer_start, layer_end in macro_layers:
                n = max(1, ceil(round((layer_start - layer_end) / o.slice_detail, 6)))
                for s in range(1, n + 1):
                    zz = round(layer_start - s * o.slice_detail, 6)
                    if zz <= layer_end or s == n:
                        zz = round(layer_end, 6)  # clamp the final step exactly onto the boundary
                    z_levels.append(zz)
            z_levels = sorted(set(z_levels))
        else:
            layer_boundaries = set()
            n_regular = ceil(abs((o.min_z - o.max_z) / o.slice_detail))
            z_levels = sorted({round(o.min_z + h * o.slice_detail, 6) for h in range(n_regular)})

        # for projection of filled areas
        layerstart = o.max.z
        layerend = o.min.z
        layers = [[layerstart, layerend]]
        nslices = len(z_levels)
        lastslice = Polygon()  # polyversion
        slicesfilled = 0
        get_ambient(o)

        for h, z_nominal in enumerate(z_levels):
            slicechunks = []
            # lower the layer by the skin value so the slice gets done at the tip of the tool
            z = z_nominal - o.skin

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

            if o.waterline_fill:
                layerstart = min(o.max_z, z + o.slice_detail)
                layerend = max(o.min.z, z - o.slice_detail)
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
                    ):  # first slice fill
                        restpoly = lastslice

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths,
                        resolution=o.optimisation.circle_detail,
                    )
                    fillz = z
                    i = 0
                    max_fill_iters = max(
                        100, int(sqrt(max(restpoly.area, 0)) / o.distance_between_paths) + 500
                    )

                    while not restpoly.is_empty and i < max_fill_iters:
                        if i % 50 == 0:
                            await progress_async("Waterline Fill", i)
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
                        # slicechunks.extend(polyToChunks(restpoly,z))
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths,
                            resolution=o.optimisation.circle_detail,
                        )
                        i += 1

                #  fill layers and last slice, last slice with inverse is not working yet
                #  - inverse millings end now always on 0 so filling ambient does have no sense.

                hit_boundary = z_nominal in layer_boundaries

                if (
                    (slicesfilled > 0 and hit_boundary)
                    or (not o.inverse and not poly.is_empty and slicesfilled == 1)
                    or (o.inverse and poly.is_empty and slicesfilled > 0)
                ):
                    fillz = z
                    bound_rectangle = o.ambient
                    restpoly = bound_rectangle.difference(poly)

                    if o.inverse and poly.is_empty and slicesfilled > 0:
                        restpoly = bound_rectangle.difference(lastslice)

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths,
                        resolution=o.optimisation.circle_detail,
                    )
                    i = 0
                    max_fill_iters = max(
                        100, int(sqrt(max(restpoly.area, 0)) / o.distance_between_paths) + 500
                    )

                    while not restpoly.is_empty and i < max_fill_iters:
                        if i % 50 == 0:
                            await progress_async("Waterline Fill", i)
                        nchunks = shapely_to_chunks(restpoly, fillz + o.skin)
                        #########################
                        nchunks = limit_chunks(nchunks, o, force=True)
                        slicechunks.extend(nchunks)
                        parent_child_distance(lastchunks, nchunks, o)
                        lastchunks = nchunks
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths,
                            resolution=o.optimisation.circle_detail,
                        )
                        i += 1

                percent = int(h / nslices * 100)
                await progress_async("Waterline Layers", percent)
                lastslice = poly

            if conventional_CCW or climb_CW:
                for chunk in slicechunks:
                    chunk.reverse()

            slicechunks = await sort_chunks(slicechunks, o)

            if topdown:
                slicechunks.reverse()

            # project chunks in between
            chunks.extend(slicechunks)

        if topdown:
            chunks.reverse()

        chunks_to_mesh(chunks, o)
