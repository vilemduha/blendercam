"""Fabex 'chunk_utils.py' © 2012 Vilem Novak"""

from math import (
    ceil,
    cos,
    pi,
    sin,
)
import sys
import time

import numpy as np
from shapely import contains, points
from shapely.geometry import (
    Point,
    Polygon,
)

import bpy
from bpy_extras import object_utils
from mathutils import Vector

try:
    import bl_ext.blender_org.simplify_curves_plus as curve_simplify
except ImportError:
    pass


from .async_utils import progress_async
from .chunk_builder import (
    CamPathChunk,
    CamPathChunkBuilder,
)
from .collision_utils import (
    cleanup_bullet_collision,
    get_sample_bullet,
    get_sample_bullet_n_axis,
    prepare_bullet_collision,
)
from .image_utils import (
    get_sample_image,
    prepare_area,
)
from .internal_utils import _optimize_internal
from .logging_utils import log
from .ocl_utils import (
    oclSample,
    oclResampleChunks,
)

from .operation_utils import get_ambient
from .parent_utils import (
    parent_child,
    parent_child_distance,
)
from .simple_utils import (
    activate,
    progress,
    timing_add,
    timing_init,
    timing_start,
    tuple_add,
    tuple_multiply,
    tuple_subtract,
    is_vertical_limit,
)

from ..exception import CamException


def chunks_refine(chunks, o):
    """Add Extra Points in Between for Chunks"""
    for ch in chunks:
        # print('before',len(ch))
        newchunk = []
        v2 = Vector(ch.points[0])
        # print(ch.points)
        for s in ch.points:
            v1 = Vector(s)
            v = v1 - v2

            if v.length > o.distance_along_paths:
                d = v.length
                v.normalize()
                i = 0
                vref = Vector((0, 0, 0))

                while vref.length < d:
                    i += 1
                    vref = v * o.distance_along_paths * i
                    if vref.length < d:
                        p = v2 + vref

                        newchunk.append((p.x, p.y, p.z))

            newchunk.append(s)
            v2 = v1
        ch.points = np.array(newchunk)

    return chunks


def chunks_refine_threshold(chunks, distance, limitdistance):
    """Add Extra Points in Between for Chunks. for Medial Axis Strategy only!"""
    for ch in chunks:
        newchunk = []
        v2 = Vector(ch.points[0])

        for s in ch.points:
            v1 = Vector(s)
            v = v1 - v2

            if v.length > limitdistance:
                d = v.length
                v.normalize()
                i = 1
                vref = Vector((0, 0, 0))
                while vref.length < d / 2:
                    vref = v * distance * i
                    if vref.length < d:
                        p = v2 + vref

                        newchunk.append((p.x, p.y, p.z))
                    i += 1
                    # because of the condition, so it doesn't run again.
                    vref = v * distance * i
                while i > 0:
                    vref = v * distance * i
                    if vref.length < d:
                        p = v1 - vref

                        newchunk.append((p.x, p.y, p.z))
                    i -= 1

            newchunk.append(s)
            v2 = v1
        ch.points = np.array(newchunk)

    return chunks


def chunk_to_shapely(chunk):
    p = Polygon(chunk.points)
    return p


def set_chunks_z(chunks, z):
    newchunks = []
    for ch in chunks:
        chunk = ch.copy()
        chunk.set_z(z)
        newchunks.append(chunk)
    return newchunks


def optimize_chunk(chunk, operation):
    if len(chunk.points) > 2:
        points = chunk.points
        naxispoints = False
        if len(chunk.startpoints) > 0:
            startpoints = chunk.startpoints
            endpoints = chunk.endpoints
            naxispoints = True

        protect_vertical = operation.movement.protect_vertical and operation.machine_axes == "3"
        keep_points = np.full(points.shape[0], True)
        # shape points need to be on line,
        # but we need to protect vertical - which
        # means changing point values
        # bits of this are moved from simple.py so that
        # numba can optimize as a whole
        _optimize_internal(
            points,
            keep_points,
            operation.optimisation.optimize_threshold * 0.000001,
            protect_vertical,
            operation.movement.protect_vertical_limit,
        )

        # now do numpy select by boolean array
        chunk.points = points[keep_points]
        if naxispoints:
            # list comprehension so we don't have to do tons of appends
            chunk.startpoints = [
                chunk.startpoints[i] for i, b in enumerate(keep_points) if b == True
            ]
            chunk.endpoints = [chunk.endpoints[i] for i, b in enumerate(keep_points) if b == True]
            chunk.rotations = [chunk.rotations[i] for i, b in enumerate(keep_points) if b == True]
    return chunk


def extend_chunks_5_axis(chunks, o):
    """Extend chunks with 5-axis cutter start and end points.

    This function modifies the provided chunks by appending calculated start
    and end points for a cutter based on the specified orientation and
    movement parameters. It determines the starting position of the cutter
    based on the machine's settings and the object's movement constraints.
    The function iterates through each point in the chunks and updates their
    start and end points accordingly.

    Args:
        chunks (list): A list of chunk objects that will be modified.
        o (object): An object containing movement and orientation data.
    """

    s = bpy.context.scene
    m = s.cam_machine
    s = bpy.context.scene
    free_height = o.movement.free_height  # o.max.z +
    if m.use_position_definitions:  # dhull
        cutterstart = Vector(
            (m.starting_position.x, m.starting_position.y, max(o.max.z, m.starting_position.z))
        )  # start point for casting
    else:
        # start point for casting
        cutterstart = Vector((0, 0, max(o.max.z, free_height)))
    cutterend = Vector((0, 0, o.min.z))
    oriname = o.name + " orientation"
    ori = s.objects[oriname]
    # rotationaxes = rotTo2axes(ori.rotation_euler,'CA')#warning-here it allready is reset to 0!!
    log.info(f"rot {o.rotationaxes}")
    a, b = o.rotationaxes  # this is all nonsense by now.
    for chunk in chunks:
        for v in chunk.points:
            cutterstart.x = v[0]
            cutterstart.y = v[1]
            cutterend.x = v[0]
            cutterend.y = v[1]
            chunk.startpoints.append(cutterstart.to_tuple())
            chunk.endpoints.append(cutterend.to_tuple())
            chunk.rotations.append(
                (a, b, 0)
            )  # TODO: this is a placeholder. It does 99.9% probably write total nonsense.


def get_closest_chunk(o, pos, chunks):
    """Find the closest chunk to a given position.

    This function iterates through a list of chunks and determines which
    chunk is closest to the specified position. It checks if each chunk's
    children are sorted before calculating the distance. The chunk with the
    minimum distance to the given position is returned.

    Args:
        o: An object representing the origin point.
        pos: A position to which the closest chunk is calculated.
        chunks (list): A list of chunk objects to evaluate.

    Returns:
        Chunk: The closest chunk object to the specified position, or None if no valid
            chunk is found.
    """

    # ch=-1
    mind = 2000
    d = 100000000000
    ch = None
    for chtest in chunks:
        cango = True
        # here was chtest.getNext==chtest, was doing recursion error and slowing down.
        for child in chtest.children:
            if not child.sorted:
                cango = False
                break
        if cango:
            d = chtest.distance(pos, o)
            if d < mind:
                ch = chtest
                mind = d
    return ch


def chunks_coherency(chunks):
    # checks chunks for their stability, for pencil path.
    # it checks if the vectors direction doesn't jump too much too quickly,
    # if this happens it splits the chunk on such places,
    # too much jumps = deletion of the chunk. this is because otherwise the router has to slow down too often,
    # but also means that some parts detected by cavity algorithm won't be milled
    nchunks = []

    for chunk in chunks:
        if len(chunk.points) > 2:
            nchunk = CamPathChunkBuilder()
            # doesn't check for 1 point chunks here, they shouldn't get here at all.
            lastvec = Vector(chunk.points[1]) - Vector(chunk.points[0])

            for i in range(0, len(chunk.points) - 1):
                nchunk.points.append(chunk.points[i])
                vec = Vector(chunk.points[i + 1]) - Vector(chunk.points[i])
                angle = vec.angle(lastvec, vec)

                if angle > 1.07:  # 60 degrees is maximum toleration for pencil paths.
                    if len(nchunk.points) > 4:  # this is a testing threshold
                        nchunks.append(nchunk.to_chunk())
                    nchunk = CamPathChunkBuilder()
                lastvec = vec

            if len(nchunk.points) > 4:  # this is a testing threshold
                nchunk.points = np.array(nchunk.points)
                nchunks.append(nchunk)

    return nchunks


def limit_chunks(chunks, o, force=False):  # TODO: this should at least add point on area border...
    # but shouldn't be needed at all at the first place...
    if o.use_limit_curve or force:
        nchunks = []

        for ch in chunks:
            prevsampled = True
            nch = CamPathChunkBuilder()
            nch1 = None
            closed = True

            for s in ch.points:
                sampled = o.ambient.contains(Point(s[0], s[1]))

                if not sampled and len(nch.points) > 0:
                    nch.closed = False
                    closed = False
                    nchunks.append(nch.to_chunk())

                    if nch1 is None:
                        nch1 = nchunks[-1]
                    nch = CamPathChunkBuilder()
                elif sampled:
                    nch.points.append(s)
                prevsampled = sampled

            if (
                len(nch.points) > 2
                and closed
                and ch.closed
                and np.array_equal(ch.points[0], ch.points[-1])
            ):
                nch.closed = True
            elif (
                ch.closed
                and nch1 is not None
                and len(nch.points) > 1
                and np.array_equal(nch.points[-1], nch1.points[0])
            ):
                # here adds beginning of closed chunk to the end, if the chunks were split during limiting
                nch.points.extend(nch1.points.tolist())
                nchunks.remove(nch1)
                log.info("Joining")

            if len(nch.points) > 0:
                nchunks.append(nch.to_chunk())
        return nchunks
    else:
        return chunks


async def sample_chunks_n_axis(o, pathSamples, layers):
    """Sample chunks along a specified axis based on provided paths and layers.

    This function processes a set of path samples and organizes them into
    chunks according to specified layers. It prepares the collision world if
    necessary, updates the cutter's rotation based on the path samples, and
    handles the sampling of points along the paths. The function also
    manages the relationships between the sampled points and their
    respective layers, ensuring that the correct points are added to each
    chunk. The resulting chunks can be used for further processing in a 3D
    environment.

    Args:
        o (object): An object containing properties such as min/max coordinates,
            cutter shape, and other relevant parameters.
        pathSamples (list): A list of path samples, each containing start points,
            end points, and rotations.
        layers (list): A list of layer definitions that specify the boundaries
            for sampling.

    Returns:
        list: A list of sampled chunks organized by layers.
    """

    #
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    # prepare collision world
    if o.update_bullet_collision_tag:
        prepare_bullet_collision(o)
        get_ambient(o)
        o.update_bullet_collision_tag = False

    cutter = o.cutter_shape
    cutterdepth = cutter.dimensions.z / 2
    t = time.time()
    totlen = 0  # total length of all chunks, to estimate sampling time.

    log.info("~ Sampling Paths ~")

    for chs in pathSamples:
        totlen += len(chs.startpoints)

    layerchunks = []
    minz = o.min_z
    layeractivechunks = []
    lastrunchunks = []

    for l in layers:
        layerchunks.append([])
        layeractivechunks.append(CamPathChunkBuilder([]))
        lastrunchunks.append([])

    n = 0
    last_percent = -1
    lastz = minz

    for patternchunk in pathSamples:
        thisrunchunks = []

        for l in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None
        lastrotation = (0, 0, 0)
        spl = len(patternchunk.startpoints)

        for si in range(0, spl):
            # #TODO: seems we are writing into the source chunk ,
            #  and that is why we need to write endpoints everywhere too?
            percent = int(100 * n / totlen)

            if percent != last_percent:
                await progress_async("Sampling Paths", percent)
                last_percent = percent

            n += 1
            sampled = False

            # get the vector to sample
            startp = Vector(patternchunk.startpoints[si])
            endp = Vector(patternchunk.endpoints[si])
            rotation = patternchunk.rotations[si]
            sweepvect = endp - startp
            sweepvect.normalize()

            # sampling
            if rotation != lastrotation:
                cutter.rotation_euler = rotation

                if o.cutter_type == "VCARVE":  # Bullet cone is always pointing Up Z in the object
                    cutter.rotation_euler.x += pi

                cutter.update_tag()
                # this has to be :( it resets the rigidbody world.
                bpy.context.scene.frame_set(1)
                # No other way to update it probably now :(
                # actually 2 frame jumps are needed.
                bpy.context.scene.frame_set(2)
                bpy.context.scene.frame_set(0)

            newsample = get_sample_bullet_n_axis(cutter, startp, endp, rotation, cutterdepth)

            ################################
            # handling samples
            ############################################
            # this is weird, but will leave it this way now.. just prototyping here.
            if newsample is not None:
                sampled = True
            else:  # TODO: why was this here?
                newsample = startp
                sampled = True

            if sampled:
                for i, l in enumerate(layers):
                    terminatechunk = False
                    ch = layeractivechunks[i]
                    v = startp - newsample
                    distance = -v.length

                    if l[1] <= distance <= l[0]:
                        lastlayer = currentlayer
                        currentlayer = i

                        if (
                            lastsample is not None
                            and lastlayer is not None
                            and currentlayer is not None
                            and lastlayer != currentlayer
                        ):  # sampling for sorted paths in layers-
                            # to go to the border of the sampled layer at least...
                            # there was a bug here, but should be fixed.
                            if currentlayer < lastlayer:
                                growing = True
                                r = range(currentlayer, lastlayer)
                                spliti = 1
                            else:
                                r = range(lastlayer, currentlayer)
                                growing = False
                                spliti = 0

                            li = 0

                            for ls in r:
                                splitdistance = layers[ls][1]

                                ratio = (splitdistance - lastdistance) / (distance - lastdistance)
                                betweensample = lastsample + (newsample - lastsample) * ratio
                                # this probably doesn't work at all!!!! check this algoritm>
                                betweenrotation = tuple_add(
                                    lastrotation,
                                    tuple_multiply(tuple_subtract(rotation, lastrotation), ratio),
                                )
                                # startpoint = retract point, it has to be always available...
                                betweenstartpoint = (
                                    laststartpoint + (startp - laststartpoint) * ratio
                                )
                                # here, we need to have also possible endpoints always..
                                betweenendpoint = lastendpoint + (endp - lastendpoint) * ratio
                                if growing:
                                    if li > 0:
                                        layeractivechunks[ls].points.insert(-1, betweensample)
                                        layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                        layeractivechunks[ls].startpoints.insert(
                                            -1, betweenstartpoint
                                        )
                                        layeractivechunks[ls].endpoints.insert(-1, betweenendpoint)
                                    else:
                                        layeractivechunks[ls].points.append(betweensample)
                                        layeractivechunks[ls].rotations.append(betweenrotation)
                                        layeractivechunks[ls].startpoints.append(betweenstartpoint)
                                        layeractivechunks[ls].endpoints.append(betweenendpoint)

                                    layeractivechunks[ls + 1].points.append(betweensample)
                                    layeractivechunks[ls + 1].rotations.append(betweenrotation)
                                    layeractivechunks[ls + 1].startpoints.append(betweenstartpoint)
                                    layeractivechunks[ls + 1].endpoints.append(betweenendpoint)
                                else:
                                    layeractivechunks[ls].points.insert(-1, betweensample)
                                    layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                    layeractivechunks[ls].startpoints.insert(-1, betweenstartpoint)
                                    layeractivechunks[ls].endpoints.insert(-1, betweenendpoint)

                                    layeractivechunks[ls + 1].points.append(betweensample)
                                    layeractivechunks[ls + 1].rotations.append(betweenrotation)
                                    layeractivechunks[ls + 1].startpoints.append(betweenstartpoint)
                                    layeractivechunks[ls + 1].endpoints.append(betweenendpoint)

                                li += 1
                        # this chunk is terminated, and allready in layerchunks /
                        ch.points.append(newsample)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)
                        lastdistance = distance

                    elif l[1] > distance:
                        v = sweepvect * l[1]
                        p = startp - v
                        ch.points.append(p)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)

                    elif l[0] < distance:  # retract to original track
                        ch.points.append(startp)
                        ch.rotations.append(rotation)
                        ch.startpoints.append(startp)
                        ch.endpoints.append(endp)

            lastsample = newsample
            lastrotation = rotation
            laststartpoint = startp
            lastendpoint = endp

        # convert everything to actual chunks
        # rather than chunkBuilders
        for i, l in enumerate(layers):
            layeractivechunks[i] = (
                layeractivechunks[i].to_chunk() if layeractivechunks[i] is not None else None
            )

        for i, l in enumerate(layers):
            ch = layeractivechunks[i]
            if ch.count() > 0:
                layerchunks[i].append(ch)
                thisrunchunks[i].append(ch)
                layeractivechunks[i] = CamPathChunkBuilder([])

            if o.strategy in ["PARALLEL", "CROSS", "OUTLINEFILL"]:
                parent_child_distance(thisrunchunks[i], lastrunchunks[i], o)

        lastrunchunks = thisrunchunks

    progress("~ Checking Relations Between Paths ~")
    """#this algorithm should also work for n-axis, but now is "sleeping"
    if (o.strategy=='PARALLEL' or o.strategy=='CROSS'):
        if len(layers)>1:# sorting help so that upper layers go first always
            for i in range(0,len(layers)-1):
                #print('layerstuff parenting')
                parentChild(layerchunks[i+1],layerchunks[i],o)
    """
    chunks = []
    for i, l in enumerate(layers):
        chunks.extend(layerchunks[i])

    return chunks


def sample_path_low(o, ch1, ch2, dosample):
    """Generate a sample path between two channels.

    This function computes a series of points that form a path between two
    given channels. It calculates the direction vector from the end of the
    first channel to the start of the second channel and generates points
    along this vector up to a specified distance. If sampling is enabled, it
    modifies the z-coordinate of the generated points based on the cutter
    shape or image sampling, ensuring that the path accounts for any
    obstacles or features in the environment.

    Args:
        o: An object containing optimization parameters and properties related to
            the path generation.
        ch1: The first channel object, which provides a point for the starting
            location of the path.
        ch2: The second channel object, which provides a point for the ending
            location of the path.
        dosample (bool): A flag indicating whether to perform sampling along the generated path.

    Returns:
        CamPathChunk: An object representing the generated path points.
    """

    v1 = Vector(ch1.get_point(-1))
    v2 = Vector(ch2.get_point(0))
    v = v2 - v1
    d = v.length
    v.normalize()
    vref = Vector((0, 0, 0))
    bpath_points = []
    i = 0

    while vref.length < d:
        i += 1
        vref = v * o.distance_along_paths * i

        if vref.length < d:
            p = v1 + vref
            bpath_points.append([p.x, p.y, p.z])

    pixsize = o.optimisation.pixsize

    if dosample:
        if not (o.optimisation.use_opencamlib and o.optimisation.use_exact):
            if o.optimisation.use_exact:
                if o.update_bullet_collision_tag:
                    prepare_bullet_collision(o)
                    o.update_bullet_collision_tag = False

                cutterdepth = o.cutter_shape.dimensions.z / 2

                for p in bpath_points:
                    z = get_sample_bullet(o.cutter_shape, p[0], p[1], cutterdepth, 1, o.min_z)

                    if z > p[2]:
                        p[2] = z
            else:
                for p in bpath_points:
                    xs = (p[0] - o.min.x) / pixsize + o.borderwidth + pixsize / 2
                    ys = (p[1] - o.min.y) / pixsize + o.borderwidth + pixsize / 2
                    z = get_sample_image((xs, ys), o.offset_image, o.min_z) + o.skin

                    if z > p[2]:
                        p[2] = z

    return CamPathChunk(bpath_points)


# samples in both modes now - image and bullet collision too.
async def sample_chunks(o, pathSamples, layers):
    """Sample chunks of paths based on the provided parameters.

    This function processes the given path samples and layers to generate
    chunks of points that represent the sampled paths. It takes into account
    various optimization settings and strategies to determine how the points
    are sampled and organized into layers. The function handles different
    scenarios based on the object's properties and the specified layers,
    ensuring that the resulting chunks are correctly structured for further
    processing.

    Args:
        o (object): An object containing various properties and settings
            related to the sampling process.
        pathSamples (list): A list of path samples to be processed.
        layers (list): A list of layers defining the z-coordinate ranges
            for sampling.

    Returns:
        list: A list of sampled chunks, each containing points that represent
            the sampled paths.
    """

    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    get_ambient(o)

    if o.optimisation.use_exact:  # prepare collision world
        if o.optimisation.use_opencamlib:
            await oclSample(o, pathSamples)
            cutterdepth = 0
        else:
            if o.update_bullet_collision_tag:
                prepare_bullet_collision(o)
                o.update_bullet_collision_tag = False

            cutter = o.cutter_shape
            cutterdepth = cutter.dimensions.z / 2
    else:
        # or prepare offset image, but not in some strategies.
        if o.strategy != "WATERLINE":
            await prepare_area(o)

        pixsize = o.optimisation.pixsize
        coordoffset = o.borderwidth + pixsize / 2  # -m
        res = ceil(o.cutter_diameter / o.optimisation.pixsize)
        m = res / 2

    t = time.time()

    totlen = 0  # total length of all chunks, to estimate sampling time.

    for ch in pathSamples:
        totlen += ch.count()

    layerchunks = []
    minz = o.min_z - 0.000001  # correction for image method problems
    layeractivechunks = []
    lastrunchunks = []

    for l in layers:
        layerchunks.append([])
        layeractivechunks.append(CamPathChunkBuilder([]))
        lastrunchunks.append([])

    zinvert = 0

    if o.inverse:
        ob = bpy.data.objects[o.object_name]
        zinvert = ob.location.z + maxz  # ob.bound_box[6][2]

    log.info(f"Total Sample Points: {totlen}")
    log.info("-")

    n = 0
    last_percent = -1
    # timing for optimisation
    samplingtime = timing_init()
    sortingtime = timing_init()
    totaltime = timing_init()
    timing_start(totaltime)
    lastz = minz

    for patternchunk in pathSamples:
        thisrunchunks = []

        for l in layers:
            thisrunchunks.append([])

        lastlayer = None
        currentlayer = None
        lastsample = None
        our_points = patternchunk.get_points_np()
        ambient_contains = contains(o.ambient, points(our_points[:, 0:2]))

        for s, in_ambient in zip(our_points, ambient_contains):
            if o.strategy != "WATERLINE" and int(100 * n / totlen) != last_percent:
                last_percent = int(100 * n / totlen)
                await progress_async("Sampling Paths", last_percent)

            n += 1
            x = s[0]
            y = s[1]

            if not in_ambient:
                newsample = (x, y, 1)
            else:
                if o.optimisation.use_opencamlib and o.optimisation.use_exact:
                    z = s[2]

                    if minz > z:
                        z = minz
                    newsample = (x, y, z)

                # ampling
                elif o.optimisation.use_exact and not o.optimisation.use_opencamlib:
                    if lastsample is not None:  # this is an optimalization,
                        # search only for near depths to the last sample. Saves about 30% of sampling time.
                        z = get_sample_bullet(
                            cutter, x, y, cutterdepth, 1, lastsample[2] - o.distance_along_paths
                        )  # first try to the last sample

                        if z < minz - 1:
                            z = get_sample_bullet(
                                cutter,
                                x,
                                y,
                                cutterdepth,
                                lastsample[2] - o.distance_along_paths,
                                minz,
                            )
                    else:
                        z = get_sample_bullet(cutter, x, y, cutterdepth, 1, minz)

                else:
                    timing_start(samplingtime)
                    xs = (x - minx) / pixsize + coordoffset
                    ys = (y - miny) / pixsize + coordoffset
                    timing_add(samplingtime)
                    z = get_sample_image((xs, ys), o.offset_image, minz) + o.skin

                ################################
                # handling samples
                ############################################

                if minz > z:
                    z = minz
                newsample = (x, y, z)

            for i, l in enumerate(layers):
                terminatechunk = False
                ch = layeractivechunks[i]

                if l[1] <= newsample[2] <= l[0]:
                    lastlayer = None  # rather the last sample here ? has to be set to None,
                    # since sometimes lastsample vs lastlayer didn't fit and did ugly ugly stuff....
                    if lastsample is not None:
                        for i2, l2 in enumerate(layers):
                            if l2[1] <= lastsample[2] <= l2[0]:
                                lastlayer = i2

                    currentlayer = i

                    if lastlayer is not None and lastlayer != currentlayer:
                        # #sampling for sorted paths in layers- to go to the border of the sampled layer at least...
                        # there was a bug here, but should be fixed.
                        if currentlayer < lastlayer:
                            growing = True
                            r = range(currentlayer, lastlayer)
                            spliti = 1
                        else:
                            r = range(lastlayer, currentlayer)
                            growing = False
                            spliti = 0

                        li = 0

                        for ls in r:
                            splitz = layers[ls][1]
                            v1 = lastsample
                            v2 = newsample

                            if o.movement.protect_vertical:
                                v1, v2 = is_vertical_limit(
                                    v1, v2, o.movement.protect_vertical_limit
                                )
                            v1 = Vector(v1)
                            v2 = Vector(v2)

                            # Prevent divide by zero:
                            dz = v2.z - v1.z
                            if abs(dz) < 1e-8:
                                # no vertical change – nothing to split
                                continue
                            ratio = (splitz - v1.z) / dz
                            betweensample = v1 + (v2 - v1) * ratio

                            if growing:
                                if li > 0:
                                    layeractivechunks[ls].points.insert(
                                        -1, betweensample.to_tuple()
                                    )
                                else:
                                    layeractivechunks[ls].points.append(betweensample.to_tuple())
                                layeractivechunks[ls + 1].points.append(betweensample.to_tuple())
                            else:
                                layeractivechunks[ls].points.insert(-1, betweensample.to_tuple())
                                layeractivechunks[ls + 1].points.insert(0, betweensample.to_tuple())

                            li += 1
                    # this chunk is terminated, and allready in layerchunks /

                    # ch.points.append(betweensample.to_tuple())#
                    ch.points.append(newsample)
                elif l[1] > newsample[2]:
                    ch.points.append((newsample[0], newsample[1], l[1]))
                elif l[0] < newsample[2]:  # terminate chunk
                    terminatechunk = True

                if terminatechunk:
                    if len(ch.points) > 0:
                        as_chunk = ch.to_chunk()
                        layerchunks[i].append(as_chunk)
                        thisrunchunks[i].append(as_chunk)
                        layeractivechunks[i] = CamPathChunkBuilder([])
            lastsample = newsample

        for i, l in enumerate(layers):
            ch = layeractivechunks[i]
            if len(ch.points) > 0:
                as_chunk = ch.to_chunk()
                layerchunks[i].append(as_chunk)
                thisrunchunks[i].append(as_chunk)
                layeractivechunks[i] = CamPathChunkBuilder([])

            # PARENTING
            if o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "OUTLINEFILL":
                timing_start(sortingtime)
                parent_child_distance(thisrunchunks[i], lastrunchunks[i], o)
                timing_add(sortingtime)

        lastrunchunks = thisrunchunks

    progress("~ Checking Relations Between Paths ~")
    timing_start(sortingtime)

    if o.strategy == "PARALLEL" or o.strategy == "CROSS" or o.strategy == "OUTLINEFILL":
        if len(layers) > 1:  # sorting help so that upper layers go first always
            for i in range(0, len(layers) - 1):
                parents = []
                children = []
                # only pick chunks that should have connectivity assigned - 'last' and 'first' ones of the layer.
                for ch in layerchunks[i + 1]:
                    if not ch.children:
                        parents.append(ch)
                for ch1 in layerchunks[i]:
                    if not ch1.parents:
                        children.append(ch1)

                # parent only last and first chunk, before it did this for all.
                parent_child(parents, children, o)
    timing_add(sortingtime)
    chunks = []

    for i, l in enumerate(layers):
        if o.movement.ramp:
            for ch in layerchunks[i]:
                ch.zstart = layers[i][0]
                ch.zend = layers[i][1]
        chunks.extend(layerchunks[i])
    timing_add(totaltime)

    log.info(f"Sampling Time: {samplingtime}")
    log.info(f"Sorting Time: {sortingtime}")
    log.info(f"Total Time: {totaltime}")
    log.info("-")

    return chunks


async def connect_chunks_low(chunks, o):
    """Connects chunks that are close to each other without lifting, sampling
    them 'low'.

    This function processes a list of chunks and connects those that are
    within a specified distance based on the provided options. It takes into
    account various strategies for connecting the chunks, including 'CARVE',
    'PENCIL', and 'MEDIAL_AXIS', and adjusts the merging distance
    accordingly. The function also handles specific movement settings, such
    as whether to stay low or to merge distances, and may resample chunks if
    certain optimization conditions are met.

    Args:
        chunks (list): A list of chunk objects to be connected.
        o (object): An options object containing movement and strategy parameters.

    Returns:
        list: A list of connected chunk objects.
    """
    if not o.movement.stay_low or (o.strategy == "CARVE" and o.carve_depth > 0):
        return chunks

    connectedchunks = []
    chunks_to_resample = []  # for OpenCAMLib sampling
    mergedist = 3 * o.distance_between_paths
    if o.strategy == "PENCIL":
        # this is bigger for pencil path since it goes on the surface to clean up the rests,
        # and can go to close points on the surface without fear of going deep into material.
        mergedist = 10 * o.distance_between_paths

    if o.strategy == "MEDIAL_AXIS":
        mergedist = 1 * o.medial_axis_subdivision

    if o.movement.parallel_step_back:
        mergedist *= 2

    if o.movement.merge_distance > 0:
        mergedist = o.movement.merge_distance
    # mergedist=10
    lastch = None
    i = len(chunks)
    pos = (0, 0, 0)

    for ch in chunks:
        if ch.count() > 0:
            if lastch is not None and (ch.distance_start(pos, o) < mergedist):
                # CARVE should lift allways, when it goes below surface...
                if o.strategy in ["PARALLEL", "CROSS", "PENCIL"]:
                    # for these paths sorting happens after sampling, thats why they need resample the connection
                    between = sample_path_low(o, lastch, ch, True)
                else:
                    between = sample_path_low(o, lastch, ch, False)
                # other paths either dont use sampling or are sorted before it.
                if (
                    o.optimisation.use_opencamlib
                    and o.optimisation.use_exact
                    and (o.strategy in ["PARALLEL", "CROSS", "PENCIL"])
                ):
                    chunks_to_resample.append(
                        (connectedchunks[-1], connectedchunks[-1].count(), between.count())
                    )

                connectedchunks[-1].extend(between.get_points_np())
                connectedchunks[-1].extend(ch.get_points_np())
            else:
                connectedchunks.append(ch)
            lastch = ch
            pos = lastch.get_point(-1)

    if (
        o.optimisation.use_opencamlib
        and o.optimisation.use_exact
        and o.strategy != "CUTOUT"
        and o.strategy != "POCKET"
        and o.strategy != "WATERLINE"
    ):
        await oclResampleChunks(o, chunks_to_resample, use_cached_mesh=True)

    return connectedchunks


async def sort_chunks(chunks, o, last_pos=None):
    """Sort a list of chunks based on a specified strategy.

    This function sorts a list of chunks according to the provided options
    and the current position. It utilizes a recursive approach to find the
    closest chunk to the current position and adapts its distance if it has
    not been sorted before. The function also handles progress updates
    asynchronously and adjusts the recursion limit to accommodate deep
    recursion scenarios.

    Args:
        chunks (list): A list of chunk objects to be sorted.
        o (object): An options object that contains sorting strategy and other parameters.
        last_pos (tuple?): The last known position as a tuple of coordinates.
            Defaults to None, which initializes the position to (0, 0, 0).

    Returns:
        list: A sorted list of chunk objects.
    """

    log.info("-")

    if o.strategy != "WATERLINE":
        await progress_async("Sorting Paths")
    # the getNext() function of CamPathChunk was running out of recursion limits.
    sys.setrecursionlimit(100000)
    sortedchunks = []
    chunks_to_resample = []

    lastch = None
    last_progress_time = time.time()
    total = len(chunks)
    i = len(chunks)
    pos = (0, 0, 0) if last_pos is None else last_pos

    while len(chunks) > 0:
        if o.strategy != "WATERLINE" and time.time() - last_progress_time > 0.1:
            await progress_async("Sorting Paths", 100.0 * (total - len(chunks)) / total)
            last_progress_time = time.time()
        ch = None
        if len(sortedchunks) == 0 or len(lastch.parents) == 0:
            # first chunk or when there are no parents -> parents come after children here...
            ch = get_closest_chunk(o, pos, chunks)
        elif len(lastch.parents) > 0:  # looks in parents for next candidate, recursively
            for parent in lastch.parents:
                ch = parent.get_next_closest(o, pos)
                if ch is not None:
                    break
            if ch is None:
                ch = get_closest_chunk(o, pos, chunks)

        if ch is not None:  # found next chunk, append it to list
            # only adaptdist the chunk if it has not been sorted before
            if not ch.sorted:
                ch.adapt_distance(pos, o)
                ch.sorted = True

            chunks.remove(ch)
            sortedchunks.append(ch)
            lastch = ch
            pos = lastch.get_point(-1)

        i -= 1

    if o.strategy == "POCKET" and o.pocket_option == "OUTSIDE":
        sortedchunks.reverse()

    sys.setrecursionlimit(1000)

    if o.strategy != "DRILL" and o.strategy != "OUTLINEFILL":
        # THIS SHOULD AVOID ACTUALLY MOST STRATEGIES, THIS SHOULD BE DONE MANUALLY,
        # BECAUSE SOME STRATEGIES GET SORTED TWICE.
        sortedchunks = await connect_chunks_low(sortedchunks, o)

    return sortedchunks


def image_to_chunks(o, image, with_border=False):
    """Convert an image into chunks based on detected edges.

    This function processes a given image to identify edges and convert them
    into polychunks, which are essentially collections of connected edge
    segments. It utilizes the properties of the input object `o` to
    determine the boundaries and size of the chunks. The function can
    optionally include borders in the edge detection process. The output is
    a list of chunks that represent the detected polygons in the image.

    Args:
        o (object): An object containing properties such as min, max, borderwidth,
            and optimisation settings.
        image (np.ndarray): A 2D array representing the image to be processed,
            expected to be in a format compatible with uint8.
        with_border (bool?): A flag indicating whether to include borders
            in the edge detection. Defaults to False.

    Returns:
        list: A list of chunks, where each chunk is represented as a collection of
            points that outline the detected edges in the image.
    """

    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.optimisation.pixsize
    image = image.astype(np.uint8)
    edges = []
    ar = image[:, :-1] - image[:, 1:]
    indices1 = ar.nonzero()
    borderspread = 2
    # when the border was excluded precisely, sometimes it did remove some silhouette parts
    r = o.borderwidth - borderspread
    # to prevent outline of the border was 3 before and also (o.cutter_diameter/2)/pixsize+o.borderwidth
    if with_border:
        r = 0
    w = image.shape[0]
    h = image.shape[1]
    coef = 0.75  # compensates for imprecisions

    for id in range(0, len(indices1[0])):
        a = indices1[0][id]
        b = indices1[1][id]

        if r < a < w - r and r < b < h - r:
            edges.append(((a - 1, b), (a, b)))

    ar = image[:-1, :] - image[1:, :]
    indices2 = ar.nonzero()

    for id in range(0, len(indices2[0])):
        a = indices2[0][id]
        b = indices2[1][id]

        if r < a < w - r and r < b < h - r:
            edges.append(((a, b - 1), (a, b)))

    polychunks = []
    d = {}

    for e in edges:
        d[e[0]] = []
        d[e[1]] = []

    for e in edges:
        verts1 = d[e[0]]
        verts2 = d[e[1]]
        verts1.append(e[1])
        verts2.append(e[0])

    if len(edges) > 0:
        ch = [edges[0][0], edges[0][1]]  # first and his reference
        d[edges[0][0]].remove(edges[0][1])
        i = 0
        specialcase = 0

        while len(d) > 0 and i < 20000000:
            verts = d.get(ch[-1], [])
            closed = False

            if len(verts) <= 1:  # this will be good for not closed loops...some time
                closed = True
                if len(verts) == 1:
                    ch.append(verts[0])
                    verts.remove(verts[0])
            elif len(verts) >= 3:
                specialcase += 1
                v1 = ch[-1]
                v2 = ch[-2]
                white = image[v1[0], v1[1]]
                comesfromtop = v1[1] < v2[1]
                comesfrombottom = v1[1] > v2[1]
                comesfromleft = v1[0] > v2[0]
                comesfromright = v1[0] < v2[0]
                take = False

                for v in verts:
                    if v[0] == ch[-2][0] and v[1] == ch[-2][1]:
                        verts.remove(v)

                    if not take:
                        if (not white and comesfromtop) or (white and comesfrombottom):
                            # goes right
                            if v1[0] + 0.5 < v[0]:
                                take = True
                        elif (not white and comesfrombottom) or (white and comesfromtop):
                            # goes left
                            if v1[0] > v[0] + 0.5:
                                take = True
                        elif (not white and comesfromleft) or (white and comesfromright):
                            # goes down
                            if v1[1] > v[1] + 0.5:
                                take = True
                        elif (not white and comesfromright) or (white and comesfromleft):
                            # goes up
                            if v1[1] + 0.5 < v[1]:
                                take = True
                        if take:
                            ch.append(v)
                            verts.remove(v)

            else:  # here it has to be 2 always
                done = False
                for vi in range(len(verts) - 1, -1, -1):
                    if not done:
                        v = verts[vi]

                        if v[0] == ch[-2][0] and v[1] == ch[-2][1]:
                            verts.remove(v)
                        else:
                            ch.append(v)
                            done = True
                            verts.remove(v)
                            # or len(verts)<=1:
                            if v[0] == ch[0][0] and v[1] == ch[0][1]:
                                closed = True

            if closed:
                polychunks.append(ch)

                for si, s in enumerate(ch):
                    if si > 0:  # first one was popped
                        if d.get(s, None) is not None and len(d[s]) == 0:
                            # this makes the case much less probable, but i think not impossible
                            d.pop(s)
                if len(d) > 0:
                    newch = False

                    while not newch:
                        v1 = d.popitem()

                        if len(v1[1]) > 0:
                            ch = [v1[0], v1[1][0]]
                            newch = True

            i += 1

            if i % 10000 == 0:
                log.info(len(ch))
                log.info(i)

        vecchunks = []

        for ch in polychunks:
            vecchunk = []
            vecchunks.append(vecchunk)

            for i in range(0, len(ch)):
                ch[i] = (
                    (ch[i][0] + coef - o.borderwidth) * pixsize + minx,
                    (ch[i][1] + coef - o.borderwidth) * pixsize + miny,
                    0,
                )
                vecchunk.append(Vector(ch[i]))

        reduxratio = 1.25  # was 1.25
        soptions = [
            "distance",
            "distance",
            o.optimisation.pixsize * reduxratio,
            5,
            o.optimisation.pixsize * reduxratio,
        ]
        nchunks = []

        for i, ch in enumerate(vecchunks):
            s = curve_simplify.simplify_RDP(ch, soptions)
            nch = CamPathChunkBuilder([])

            for i in range(0, len(s)):
                nch.points.append((ch[s[i]].x, ch[s[i]].y))

            if len(nch.points) > 2:
                nchunks.append(nch.to_chunk())

        return nchunks
    else:
        return []


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
    progress("~ Building Paths from Chunks ~")
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

    collections = bpy.data.collections
    if "Paths" in collections:
        bpy.context.collection.objects.unlink(ob)
        collections["Paths"].objects.link(ob)
    else:
        add_collections()
        bpy.context.collection.objects.unlink(ob)
        collections["Paths"].objects.link(ob)

    # parent the path object to source object if object mode
    if (o.geometry_source == "OBJECT") and o.parent_path_to_object:
        activate(o.objects[0])
        ob.select_set(state=True, view_layer=None)
        bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)
    else:
        ob.select_set(state=True, view_layer=None)
