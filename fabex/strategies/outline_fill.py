from ..bridges import use_bridges

from ..utilities.chunk_utils import (
    chunks_refine,
    chunks_to_mesh,
    connect_chunks_low,
    sample_chunks,
    sort_chunks,
)
from ..utilities.logging_utils import log
from ..utilities.operation_utils import (
    get_layers,
    get_move_and_spin,
)
from ..utilities.parent_utils import parent_child_distance
from ..utilities.shapely_utils import shapely_to_chunks
from ..utilities.silhouette_utils import get_operation_silhouette
from ..utilities.simple_utils import progress


async def outline_fill(o):
    log.info("~ Strategy: Outline Fill ~")

    get_operation_silhouette(o)

    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)

    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pathchunks = []
    zlevel = 1
    polys = o.silhouette.geoms
    chunks = []

    for p in polys:
        p = p.buffer(-o.distance_between_paths / 10, o.optimisation.circle_detail)
        # first, move a bit inside, because otherwise the border samples go crazy very often changin between
        # hit/non hit and making too many jumps in the path.
        chunks.extend(shapely_to_chunks(p, 0))

    pathchunks.extend(chunks)
    lastchunks = chunks
    firstchunks = chunks
    approxn = (min(maxx - minx, maxy - miny) / o.distance_between_paths) / 2
    i = 0

    for porig in polys:
        p = porig

        while not p.is_empty:
            p = p.buffer(-o.distance_between_paths, o.optimisation.circle_detail)

            if not p.is_empty:
                nchunks = shapely_to_chunks(p, zlevel)

                if o.movement.insideout == "INSIDEOUT":
                    parent_child_distance(lastchunks, nchunks, o)
                else:
                    parent_child_distance(nchunks, lastchunks, o)

                pathchunks.extend(nchunks)
                lastchunks = nchunks

            percent = int(i / approxn * 100)
            progress("Outlining Polygons ", percent)
            i += 1

    pathchunks.reverse()

    if not o.inverse:  # dont do ambient for inverse milling
        lastchunks = firstchunks

        for p in polys:
            d = o.distance_between_paths
            steps = o.ambient_radius / o.distance_between_paths

            for a in range(0, int(steps)):
                dist = d

                if a == int(o.cutter_diameter / 2 / o.distance_between_paths):
                    if o.optimisation.use_exact:
                        dist += o.optimisation.pixsize * 0.85
                        # this is here only because silhouette is still done with zbuffer method,
                        # even if we use bullet collisions.
                    else:
                        dist += o.optimisation.pixsize * 2.5

                p = p.buffer(dist, o.optimisation.circle_detail)

                if not p.is_empty:
                    nchunks = shapely_to_chunks(p, zlevel)

                    if o.movement.insideout == "INSIDEOUT":
                        parent_child_distance(nchunks, lastchunks, o)
                    else:
                        parent_child_distance(lastchunks, nchunks, o)

                    pathchunks.extend(nchunks)
                    lastchunks = nchunks

    if o.movement.insideout == "OUTSIDEIN":
        pathchunks.reverse()

    for chunk in pathchunks:
        if o.movement.insideout == "OUTSIDEIN":
            chunk.reverse()
        if climb_CW or conventional_CCW:
            chunk.reverse()

    pathSamples = chunks_refine(pathchunks, o)
    pathSamples = await sort_chunks(pathSamples, o)
    chunks = []
    layers = get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    log.info("Sorting")
    chunks = await sort_chunks(chunks, o)
    chunks = await connect_chunks_low(chunks, o)

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    if o.use_bridges:
        log.info(chunks)
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    chunks_to_mesh(chunks, o)
