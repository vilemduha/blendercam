from math import (
    ceil,
    floor,
)

from shapely.geometry import Polygon

from ..utilities.chunk_utils import (
    chunks_to_mesh,
    chunks_refine,
    limit_chunks,
    sample_chunks,
    sort_chunks,
)
from ..utilities.image_shapely_utils import image_to_shapely
from ..utilities.image_utils import prepare_area
from ..utilities.logging_utils import log
from ..utilities.waterline_utils import oclGetWaterline
from ..utilities.operation_utils import (
    get_ambient,
    get_move_and_spin,
)
from ..utilities.parent_utils import parent_child_distance
from ..utilities.shapely_utils import shapely_to_chunks
from ..utilities.async_utils import progress_async


async def waterline(o):
    log.info("~ Strategy: Waterline ~")

    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)

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
        layerstep = 1000000000

        if o.use_layers:
            layerstep = floor(o.stepdown / o.slice_detail)
            if layerstep == 0:
                layerstep = 1

        # for projection of filled areas
        layerstart = o.max.z  #
        layerend = o.min.z  #
        layers = [[layerstart, layerend]]
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
                    ):  # first slice fill
                        restpoly = lastslice

                    restpoly = restpoly.buffer(
                        -o.distance_between_paths,
                        resolution=o.optimisation.circle_detail,
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
                        # slicechunks.extend(polyToChunks(restpoly,z))
                        restpoly = restpoly.buffer(
                            -o.distance_between_paths,
                            resolution=o.optimisation.circle_detail,
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
                        -o.distance_between_paths,
                        resolution=o.optimisation.circle_detail,
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
