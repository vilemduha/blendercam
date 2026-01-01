from math import (
    ceil,
    pi,
)
import random

import numpy as np
import numpy as np

from mathutils import Vector, Euler


from ..chunk_builder import (
    CamPathChunk,
    CamPathChunkBuilder,
)
from .geom_utils import get_circle_binary
from .image_utils import (
    prepare_area,
)
from .logging_utils import log
from .operation_utils import get_move_and_spin
from .parent_utils import (
    parent_child_distance,
)


def crazy_stroke_image(o):
    """Generate a toolpath for a milling operation using a crazy stroke
    strategy.

    This function computes a path for a milling cutter based on the provided
    parameters and the offset image. It utilizes a circular cutter
    representation and evaluates potential cutting positions based on
    various thresholds. The algorithm iteratively tests different angles and
    lengths for the cutter's movement until the desired cutting area is
    achieved or the maximum number of tests is reached.

    Args:
        o (object): An object containing parameters such as cutter diameter,
            optimization settings, movement type, and thresholds for
            determining cutting effectiveness.

    Returns:
        list: A list of chunks representing the computed toolpath for the milling
            operation.
    """

    # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)

    r = int((o.cutter_diameter / 2.0) / o.optimisation.pixsize)
    d = 2 * r
    coef = 0.75
    ar = o.offset_image.copy()
    maxarx = ar.shape[0]
    maxary = ar.shape[1]
    cutterArray = get_circle_binary(r)
    cutterArrayNegative = -cutterArray
    cutterimagepix = cutterArray.sum()
    # a threshold which says if it is valuable to cut in a direction
    satisfypix = cutterimagepix * o.crazy_threshold_1
    toomuchpix = cutterimagepix * o.crazy_threshold_2
    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()  #
    totpix = startpix
    chunk_builders = []
    xs = indices[0][0] - r

    if xs < r:
        xs = r
    ys = indices[1][0] - r

    if ys < r:
        ys = r

    nchunk = CamPathChunkBuilder([(xs, ys)])  # startposition
    log.info(indices)
    log.info(f"{indices[0][0]}, {indices[1][0]}")
    # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    lastvect = Vector((r, 0, 0))
    # multiply *2 not to get values <1 pixel
    testvect = lastvect.normalized() * r / 2.0
    rot = Euler((0, 0, 1))
    i = 0
    perc = 0
    itests = 0
    totaltests = 0
    maxtests = 500
    maxtotaltests = 1000000

    log.info(f"{xs}, {ys}, {indices[0][0]}, {indices[1][0]}, {r}")
    ar[xs - r : xs - r + d, ys - r : ys - r + d] = (
        ar[xs - r : xs - r + d, ys - r : ys - r + d] * cutterArrayNegative
    )
    # range for angle of toolpath vector versus material vector
    anglerange = [-pi, pi]
    testangleinit = 0
    angleincrement = 0.05

    if climb_CCW or conventional_CW:
        anglerange = [-pi, 0]
        testangleinit = 1
        angleincrement = -angleincrement
    elif conventional_CCW or climb_CW:
        anglerange = [0, pi]
        testangleinit = -1
        angleincrement = angleincrement

    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end
        success = False
        # define a vector which gets varied throughout the testing, growing and growing angle to sides.
        testangle = testangleinit
        testleftright = False
        testlength = r

        while not success:
            xs = nchunk.points[-1][0] + int(testvect.x)
            ys = nchunk.points[-1][1] + int(testvect.y)

            if xs > r + 1 and xs < ar.shape[0] - r - 1 and ys > r + 1 and ys < ar.shape[1] - r - 1:
                testar = ar[xs - r : xs - r + d, ys - r : ys - r + d] * cutterArray
                if 0:
                    log.info("Test")
                    log.info(f"{testar.sum()}, {satisfypix}")
                    log.info(f"{xs}, {ys}, {testlength}, {testangle}")
                    log.info(lastvect)
                    log.info(testvect)
                    log.info(totpix)

                eatpix = testar.sum()
                cindices = testar.nonzero()
                cx = cindices[0].sum() / eatpix
                cy = cindices[1].sum() / eatpix
                v = Vector((cx - r, cy - r))
                angle = testvect.to_2d().angle_signed(v)
                # this could be righthanded milling? lets see :)

                if anglerange[0] < angle < anglerange[1]:
                    if toomuchpix > eatpix > satisfypix:
                        success = True

            if success:
                nchunk.points.append([xs, ys])
                lastvect = testvect
                ar[xs - r : xs - r + d, ys - r : ys - r + d] = ar[
                    xs - r : xs - r + d, ys - r : ys - r + d
                ] * (-cutterArray)
                totpix -= eatpix
                itests = 0

                if 0:
                    log.info("Success")
                    log.info(f"{xs}, {ys}, {testlength}, {testangle}")
                    log.info(lastvect)
                    log.info(testvect)
                    log.info(itests)
            else:
                # TODO: after all angles were tested into material higher than toomuchpix, it should cancel,
                #  otherwise there is no problem with long travel in free space.....
                # TODO:the testing should start not from the same angle as lastvector, but more towards material.
                #  So values closer to toomuchpix are obtained rather than satisfypix
                testvect = lastvect.normalized() * testlength
                right = True

                if testangleinit == 0:  # meander
                    if testleftright:
                        testangle = -testangle
                        testleftright = False
                    else:
                        testangle = abs(testangle) + angleincrement  # increment angle
                        testleftright = True
                else:  # climb/conv.
                    testangle += angleincrement

                if abs(testangle) > o.crazy_threshold_3:  # /testlength
                    testangle = testangleinit
                    testlength += r / 4.0
                if nchunk.points[-1][0] + testvect.x < r:
                    testvect.x = r
                if nchunk.points[-1][1] + testvect.y < r:
                    testvect.y = r
                if nchunk.points[-1][0] + testvect.x > maxarx - r:
                    testvect.x = maxarx - r
                if nchunk.points[-1][1] + testvect.y > maxary - r:
                    testvect.y = maxary - r

                rot.z = testangle
                testvect.rotate(rot)

            itests += 1
            totaltests += 1

            if itests > maxtests or testlength > r * 1.5:
                indices = ar.nonzero()
                chunk_builders.append(nchunk)

                if len(indices[0]) > 0:
                    xs = indices[0][0] - r

                    if xs < r:
                        xs = r
                    ys = indices[1][0] - r

                    if ys < r:
                        ys = r
                    nchunk = CamPathChunkBuilder([(xs, ys)])  # startposition
                    ar[xs - r : xs - r + d, ys - r : ys - r + d] = (
                        ar[xs - r : xs - r + d, ys - r : ys - r + d] * cutterArrayNegative
                    )
                    r = random.random() * 2 * pi
                    e = Euler((0, 0, r))
                    testvect = lastvect.normalized() * 4  # multiply *2 not to get values <1 pixel
                    testvect.rotate(e)
                    lastvect = testvect.copy()
                success = True
                itests = 0
        i += 1

        if i % 100 == 0:
            log.info("100 Succesfull Tests Done")
            totpix = ar.sum()
            log.info(totpix)
            log.info(totaltests)
            i = 0

    chunk_builders.append(nchunk)

    for ch in chunk_builders:
        ch = ch.points

        for i in range(0, len(ch)):
            ch[i] = (
                (ch[i][0] + coef - o.borderwidth) * o.optimisation.pixsize + minx,
                (ch[i][1] + coef - o.borderwidth) * o.optimisation.pixsize + miny,
                0,
            )

    return [c.to_chunk() for c in chunk_builders]


def crazy_stroke_image_binary(o, ar, avoidar):
    """Perform a milling operation using a binary image representation.

    This function implements a strategy for milling by navigating through a
    binary image. It starts from a defined point and attempts to move in
    various directions, evaluating the cutter load to determine the
    appropriate path. The algorithm continues until it either exhausts the
    available pixels to cut or reaches a predefined limit on the number of
    tests. The function modifies the input array to represent the areas that
    have been milled and returns the generated path as a list of chunks.

    Args:
        o (object): An object containing parameters for the milling operation, including
            cutter diameter, thresholds, and movement type.
        ar (np.ndarray): A 2D binary array representing the image to be milled.
        avoidar (np.ndarray): A 2D binary array indicating areas to avoid during milling.

    Returns:
        list: A list of chunks representing the path taken during the milling
            operation.
    """

    # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    # works like this:
    # start 'somewhere'
    # try to go in various directions.
    # if somewhere the cutter load is appropriate - it is correct magnitude and side, continue in that directon
    # try to continue straight or around that, looking
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    climb_CW, climb_CCW, conventional_CW, conventional_CCW = get_move_and_spin(o)
    # TODO this should be somewhere else, but here it is now to get at least some ambient for start of the operation.
    ar[: o.borderwidth, :] = 0
    ar[-o.borderwidth :, :] = 0
    ar[:, : o.borderwidth] = 0
    ar[:, -o.borderwidth :] = 0

    # ceil((o.cutter_diameter/12)/o.optimisation.pixsize)
    r = int((o.cutter_diameter / 2.0) / o.optimisation.pixsize)
    d = 2 * r
    coef = 0.75
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = get_circle_binary(r)
    cutterArrayNegative = -cutterArray

    cutterimagepix = cutterArray.sum()

    anglelimit = o.crazy_threshold_3
    # a threshold which says if it is valuable to cut in a direction
    satisfypix = cutterimagepix * o.crazy_threshold_1
    toomuchpix = cutterimagepix * o.crazy_threshold_2  # same, but upper limit
    # (satisfypix+toomuchpix)/2.0# the ideal eating ratio
    optimalpix = cutterimagepix * o.crazy_threshold_5
    indices = ar.nonzero()  # first get white pixels

    startpix = ar.sum()  #
    totpix = startpix

    chunk_builders = []
    # try to find starting point here

    xs = indices[0][0] - r / 2
    if xs < r:
        xs = r
    ys = indices[1][0] - r
    if ys < r:
        ys = r

    nchunk = CamPathChunkBuilder([(xs, ys)])  # startposition
    log.info(indices)
    log.info(f"{indices[0][0]}, {indices[1][0]}")
    # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    lastvect = Vector((r, 0, 0))
    # multiply *2 not to get values <1 pixel
    testvect = lastvect.normalized() * r / 4.0
    rot = Euler((0, 0, 1))
    i = 0
    itests = 0
    totaltests = 0
    maxtests = 2000
    maxtotaltests = 20000  # 1000000

    margin = 0

    # print(xs,ys,indices[0][0],indices[1][0],r)
    ar[xs - r : xs + r, ys - r : ys + r] = (
        ar[xs - r : xs + r, ys - r : ys + r] * cutterArrayNegative
    )
    anglerange = [-pi, pi]
    # range for angle of toolpath vector versus material vector -
    # probably direction negative to the force applied on cutter by material.
    testangleinit = 0
    angleincrement = o.crazy_threshold_4

    if climb_CCW or conventional_CW:
        anglerange = [-pi, 0]
        testangleinit = anglelimit
        angleincrement = -angleincrement
    elif conventional_CCW or climb_CW:
        anglerange = [0, pi]
        testangleinit = -anglelimit
        angleincrement = angleincrement

    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end
        success = False
        # define a vector which gets varied throughout the testing, growing and growing angle to sides.
        testangle = testangleinit
        testleftright = False
        testlength = r
        foundsolutions = []

        while not success:
            xs = int(nchunk.points[-1][0] + testvect.x)
            ys = int(nchunk.points[-1][1] + testvect.y)

            if (
                xs > r + margin
                and xs < ar.shape[0] - r - margin
                and ys > r + margin
                and ys < ar.shape[1] - r - margin
            ):
                # avoidtest=avoidar[xs-r:xs+r,ys-r:ys+r]*cutterArray
                if not avoidar[xs, ys]:
                    testar = ar[xs - r : xs + r, ys - r : ys + r] * cutterArray
                    eatpix = testar.sum()
                    cindices = testar.nonzero()
                    cx = cindices[0].sum() / eatpix
                    cy = cindices[1].sum() / eatpix
                    v = Vector((cx - r, cy - r))

                    if v.length != 0:
                        angle = testvect.to_2d().angle_signed(v)
                        if (
                            anglerange[0] < angle < anglerange[1]
                            and toomuchpix > eatpix > satisfypix
                        ) or (eatpix > 0 and totpix < startpix * 0.025):
                            # this could be righthanded milling?
                            # lets see :)
                            foundsolutions.append([testvect.copy(), eatpix])
                            # or totpix < startpix*0.025:
                            if len(foundsolutions) >= 10:
                                success = True
            itests += 1
            totaltests += 1

            if success:
                # fist, try to inter/extrapolate the recieved results.
                closest = 100000000

                for s in foundsolutions:
                    if abs(s[1] - optimalpix) < closest:
                        bestsolution = s
                        closest = abs(s[1] - optimalpix)

                # v1#+(v2-v1)*ratio#rewriting with interpolated vect.
                testvect = bestsolution[0]
                xs = int(nchunk.points[-1][0] + testvect.x)
                ys = int(nchunk.points[-1][1] + testvect.y)
                nchunk.points.append([xs, ys])
                lastvect = testvect

                ar[xs - r : xs + r, ys - r : ys + r] = (
                    ar[xs - r : xs + r, ys - r : ys + r] * cutterArrayNegative
                )
                totpix -= bestsolution[1]
                itests = 0
                totaltests = 0
            else:
                # TODO: after all angles were tested into material higher than toomuchpix,
                #  it should cancel, otherwise there is no problem with long travel in free space.....
                # TODO:the testing should start not from the same angle as lastvector, but more towards material.
                #  So values closer to toomuchpix are obtained rather than satisfypix
                testvect = lastvect.normalized() * testlength

                if testangleinit == 0:  # meander
                    if testleftright:
                        testangle = -testangle - angleincrement
                        testleftright = False
                    else:
                        testangle = -testangle + angleincrement  # increment angle
                        testleftright = True
                else:  # climb/conv.
                    testangle += angleincrement

                if (abs(testangle) > o.crazy_threshold_3 and len(nchunk.points) > 1) or (
                    abs(testangle) > 2 * pi
                ):
                    testangle = testangleinit
                    testlength += r / 4.0

                if nchunk.points[-1][0] + testvect.x < r:
                    testvect.x = r
                if nchunk.points[-1][1] + testvect.y < r:
                    testvect.y = r
                if nchunk.points[-1][0] + testvect.x > maxarx - r:
                    testvect.x = maxarx - r
                if nchunk.points[-1][1] + testvect.y > maxary - r:
                    testvect.y = maxary - r

                rot.z = testangle
                testvect.rotate(rot)

                if itests > maxtests or testlength > r * 1.5:
                    andar = np.logical_and(ar, np.logical_not(avoidar))
                    indices = andar.nonzero()

                    if len(nchunk.points) > 1:
                        parent_child_distance([nchunk], chunks, o, distance=r)
                        chunk_builders.append(nchunk)

                    if totpix > startpix * 0.001:
                        found = False
                        ftests = 0

                        while not found:
                            # look for next start point:
                            index = random.randint(0, len(indices[0]) - 1)
                            xs = indices[0][index]
                            ys = indices[1][index]
                            v = Vector((r - 1, 0, 0))
                            randomrot = random.random() * 2 * pi
                            e = Euler((0, 0, randomrot))
                            v.rotate(e)
                            xs += int(v.x)
                            ys += int(v.y)

                            if xs < r:
                                xs = r
                            if ys < r:
                                ys = r
                            if avoidar[xs, ys] == 0:
                                testarsum = (
                                    ar[xs - r : xs - r + d, ys - r : ys - r + d].sum() * pi / 4
                                )

                                if toomuchpix > testarsum > 0 or (totpix < startpix * 0.025):
                                    # 0 now instead of satisfypix
                                    found = True
                                    nchunk = CamPathChunk([(xs, ys)])  # startposition
                                    ar[xs - r : xs + r, ys - r : ys + r] = (
                                        ar[xs - r : xs + r, ys - r : ys + r] * cutterArrayNegative
                                    )
                                    # lastvect=Vector((r,0,0))#vector is 3d,
                                    # blender somehow doesn't rotate 2d vectors with angles.
                                    randomrot = random.random() * 2 * pi
                                    e = Euler((0, 0, randomrot))
                                    testvect = lastvect.normalized() * 2
                                    # multiply *2 not to get values <1 pixel
                                    testvect.rotate(e)
                                    lastvect = testvect.copy()
                            if ftests > 2000:
                                totpix = 0  # this quits the process now.
                            ftests += 1

                    success = True
                    itests = 0
        i += 1

        if i % 100 == 0:
            log.info("100 Succesfull Tests Done")
            totpix = ar.sum()
            log.info(totpix)
            log.info(totaltests)
            i = 0

    if len(nchunk.points) > 1:
        parent_child_distance([nchunk], chunks, o, distance=r)
        chunk_builders.append(nchunk)

    for ch in chunk_builders:
        ch = ch.points

        for i in range(0, len(ch)):
            ch[i] = (
                (ch[i][0] + coef - o.borderwidth) * o.optimisation.pixsize + minx,
                (ch[i][1] + coef - o.borderwidth) * o.optimisation.pixsize + miny,
                o.min_z,
            )

    return [c.to_chunk for c in chunk_builders]


async def crazy_path(o):
    """Execute a greedy adaptive algorithm for path planning.

    This function prepares an area based on the provided object `o`,
    calculates the dimensions of the area, and initializes a mill image and
    cutter array. The dimensions are determined by the maximum and minimum
    coordinates of the object, adjusted by the simulation detail and border
    width. The function is currently a stub and requires further
    implementation.

    Args:
        o (object): An object containing properties such as max, min, optimisation, and
            borderwidth.

    Returns:
        None: This function does not return a value.
    """

    # TODO: try to do something with this  stuff, it's just a stub. It should be a greedy adaptive algorithm.
    #  started another thing below.
    await prepare_area(o)
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.optimisation.simulation_detail) + 2 * o.borderwidth
    resy = ceil(sy / o.optimisation.simulation_detail) + 2 * o.borderwidth

    o.millimage = np.full(shape=(resx, resy), fill_value=0.0, dtype=np.float)
    # getting inverted cutter
    o.cutterArray = -get_cutter_array(o, o.optimisation.simulation_detail)


def build_stroke(start, end, cutterArray):
    """Build a stroke array based on start and end points.

    This function generates a 2D stroke array that represents a stroke from
    a starting point to an ending point. It calculates the length of the
    stroke and creates a grid that is filled based on the positions defined
    by the start and end coordinates. The function uses a cutter array to
    determine how the stroke interacts with the grid.

    Args:
        start (tuple): A tuple representing the starting coordinates (x, y, z).
        end (tuple): A tuple representing the ending coordinates (x, y, z).
        cutterArray: An object that contains size information used to modify
            the stroke array.

    Returns:
        numpy.ndarray: A 2D array representing the stroke, filled with
            calculated values based on the input parameters.
    """

    strokelength = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
    size_x = abs(end[0] - start[0]) + cutterArray.size[0]
    size_y = abs(end[1] - start[1]) + cutterArray.size[0]
    r = cutterArray.size[0] / 2

    strokeArray = np.full(shape=(size_x, size_y), fill_value=-10.0, dtype=np.float)
    samplesx = np.round(np.linspace(start[0], end[0], strokelength))
    samplesy = np.round(np.linspace(start[1], end[1], strokelength))
    samplesz = np.round(np.linspace(start[2], end[2], strokelength))

    for i in range(0, len(strokelength)):
        strokeArray[
            samplesx[i] - r : samplesx[i] + r, samplesy[i] - r : samplesy[i] + r
        ] = np.maximum(
            strokeArray[samplesx[i] - r : samplesx[i] + r, samplesy[i] - r : samplesy[i] + r],
            cutterArray + samplesz[i],
        )
    return strokeArray


def test_stroke():
    pass


def apply_stroke():
    pass


def test_stroke_binary(img, stroke):
    pass  # buildstroke()
