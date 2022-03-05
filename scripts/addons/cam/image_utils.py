# blender CAM image_utils.py (c) 2012 Vilem Novak
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import numpy
import math
import time
import random

import curve_simplify
import mathutils
from mathutils import *

from cam import simple
from cam.simple import *
from cam import chunk
from cam.chunk import *
from cam import simulation


def getCircle(r, z):
    car = numpy.array(0, dtype=float)
    res = 2 * r
    m = r
    car.resize(r * 2, r * 2)
    car.fill(-10)
    v = mathutils.Vector((0, 0, 0))
    for a in range(0, res):
        v.x = (a + 0.5 - m)
        for b in range(0, res):
            v.y = (b + 0.5 - m)
            if v.length <= r:
                car[a, b] = z
    return car


def getCircleBinary(r):
    car = numpy.array((False), dtype=bool)
    res = 2 * r
    m = r
    car.resize(r * 2, r * 2)
    car.fill(False)
    v = mathutils.Vector((0, 0, 0))
    for a in range(0, res):
        v.x = (a + 0.5 - m)
        for b in range(0, res):
            v.y = (b + 0.5 - m)
            if (v.length <= r):
                car.itemset((a, b), True)
    return car


# get cutters for the z-buffer image method


def numpysave(a, iname):
    inamebase = bpy.path.basename(iname)

    i = numpytoimage(a, inamebase)

    r = bpy.context.scene.render

    r.image_settings.file_format = 'OPEN_EXR'
    r.image_settings.color_mode = 'BW'
    r.image_settings.color_depth = '32'

    i.save_render(iname)


def numpytoimage(a, iname):
    print('numpy to image', iname)
    t = time.time()
    print(a.shape[0], a.shape[1])
    foundimage = False

    for image in bpy.data.images:

        if image.name[:len(iname)] == iname and image.size[0] == a.shape[0] and image.size[1] == a.shape[1]:
            i = image
            foundimage = True
    if not foundimage:
        bpy.ops.image.new(name=iname, width=a.shape[0], height=a.shape[1], color=(0, 0, 0, 1), alpha=True,
                          generated_type='BLANK', float=True)
        for image in bpy.data.images:
            # print(image.name[:len(iname)],iname, image.size[0],a.shape[0],image.size[1],a.shape[1])
            if image.name[:len(iname)] == iname and image.size[0] == a.shape[0] and image.size[1] == a.shape[1]:
                i = image

    d = a.shape[0] * a.shape[1]
    a = a.swapaxes(0, 1)
    a = a.reshape(d)
    a = a.repeat(4)
    a[3::4] = 1
    i.pixels[:] = a[:]  # this gives big speedup!
    print('\ntime ' + str(time.time() - t))
    return i


def imagetonumpy(i):
    t = time.time()

    width = i.size[0]
    height = i.size[1]
    na = numpy.array((0.1), dtype=float)

    size = width * height
    na.resize(size * 4)

    p = i.pixels[:]
    # these 2 lines are about 15% faster than na[:]=i.pixels[:].... whyyyyyyyy!!?!?!?!?!
    # Blender image data access is evil.
    na[:] = p
    na = na[::4]
    na = na.reshape(height, width)
    na = na.swapaxes(0, 1)

    print('\ntime of image to numpy ' + str(time.time() - t))
    return na


def offsetArea(o, samples):
    """ offsets the whole image with the cutter + skin offsets """
    if o.update_offsetimage_tag:
        minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
        o.offset_image.fill(-10)

        sourceArray = samples
        cutterArray = simulation.getCutterArray(o, o.pixsize)

        # progress('image size', sourceArray.shape)

        width = len(sourceArray)
        height = len(sourceArray[0])
        cwidth = len(cutterArray)

        t = time.time()

        m = int(cwidth / 2.0)

        if o.inverse:
            sourceArray = -sourceArray + minz
        print(o.offset_image.shape)
        comparearea = o.offset_image[m: width - cwidth + m, m:height - cwidth + m]
        # i=0
        for x in range(0, cwidth):  # cwidth):
            text = "Offsetting depth " + str(int(x * 100 / cwidth))
            # o.operator.report({"INFO"}, text)
            simple.progress('offset ', int(x * 100 / cwidth))
            for y in range(0, cwidth):
                # TODO:OPTIMIZE THIS - this can run much faster when the areas won't be created each run????
                #  tests dont work now
                if cutterArray[x, y] > -10:
                    # i+=1
                    # progress(i)
                    # winner
                    numpy.maximum(sourceArray[x: width - cwidth + x, y: height - cwidth + y] + cutterArray[x, y],
                                  comparearea, comparearea)
                    # contest of performance

        o.offset_image[m: width - cwidth + m, m:height - cwidth + m] = comparearea
        # progress('offseting done')

        simple.progress('\ntime ' + str(time.time() - t))

        o.update_offsetimage_tag = False
    # progress('doing offsetimage')
    return o.offset_image


def dilateAr(ar, cycles):
    for c in range(cycles):
        ar[1:-1, :] = numpy.logical_or(ar[1:-1, :], ar[:-2, :])
        ar[:, 1:-1] = numpy.logical_or(ar[:, 1:-1], ar[:, :-2])


def getOffsetImageCavities(o, i):  # for pencil operation mainly
    """detects areas in the offset image which are 'cavities' - the curvature changes."""
    # i=numpy.logical_xor(lastislice , islice)
    simple.progress('detect corners in the offset image')
    vertical = i[:-2, 1:-1] - i[1:-1, 1:-1] - o.pencil_threshold > i[1:-1, 1:-1] - i[2:, 1:-1]
    horizontal = i[1:-1, :-2] - i[1:-1, 1:-1] - o.pencil_threshold > i[1:-1, 1:-1] - i[1:-1, 2:]
    # if bpy.app.debug_value==2:

    ar = numpy.logical_or(vertical, horizontal)

    if 1:  # this is newer strategy, finds edges nicely, but pff.going exacty on edge,
        # it has tons of spikes and simply is not better than the old one
        iname = simple.getCachePath(o) + '_pencilthres.exr'
        # numpysave(ar,iname)#save for comparison before
        chunks = imageEdgeSearch_online(o, ar, i)
        iname = simple.getCachePath(o) + '_pencilthres_comp.exr'
        print("new pencil strategy")

    # ##crop pixels that are on outer borders
    for chi in range(len(chunks) - 1, -1, -1):
        chunk = chunks[chi]
        for si in range(len(chunk.points) - 1, -1, -1):
            if not (o.min.x < chunk.points[si][0] < o.max.x and o.min.y < chunk.points[si][1] < o.max.y):
                chunk.points.pop(si)
        if len(chunk.points) < 2:
            chunks.pop(chi)

    return chunks


def imageEdgeSearch_online(o, ar, zimage):  # search edges for pencil strategy, another try.
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    r = ceil((o.cutter_diameter/12)/o.pixsize)   # was commented
    coef = 0.75
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    directions = ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))

    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()
    totpix = startpix
    chunks = []
    xs = indices[0][0]
    ys = indices[1][0]
    nchunk = camPathChunk([(xs, ys, zimage[xs, ys])])  # startposition
    dindex = 0  # index in the directions list
    last_direction = directions[dindex]
    test_direction = directions[dindex]
    i = 0
    perc = 0
    itests = 0
    totaltests = 0
    maxtotaltests = startpix * 4

    ar[xs, ys] = False

    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end

        if perc != int(100 - 100 * totpix / startpix):
            perc = int(100 - 100 * totpix / startpix)
            simple.progress('pencil path searching', perc)
        # progress('simulation ',int(100*i/l))
        success = False
        testangulardistance = 0  # distance from initial direction in the list of direction
        testleftright = False  # test both sides from last vector
        while not success:
            xs = nchunk.points[-1][0] + test_direction[0]
            ys = nchunk.points[-1][1] + test_direction[1]

            if xs > r and xs < ar.shape[0] - r and ys > r and ys < ar.shape[1] - r:
                test = ar[xs, ys]
                # print(test)
                if test:
                    success = True
            if success:
                nchunk.points.append([xs, ys, zimage[xs, ys]])
                last_direction = test_direction
                ar[xs, ys] = False
                if 0:
                    print('success')
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(itests)
            else:
                # nchunk.append([xs,ys])#for debugging purpose
                # ar.shape[0]
                test_direction = last_direction
                if testleftright:
                    testangulardistance = -testangulardistance
                    testleftright = False
                else:
                    testangulardistance = -testangulardistance
                    testangulardistance += 1  # increment angle
                    testleftright = True

                if abs(testangulardistance) > 6:  # /testlength
                    testangulardistance = 0
                    indices = ar.nonzero()
                    totpix = len(indices[0])
                    chunks.append(nchunk)
                    if len(indices[0] > 0):
                        xs = indices[0][0]
                        ys = indices[1][0]
                        nchunk = camPathChunk([(xs, ys, zimage[xs, ys])])  # startposition

                        ar[xs, ys] = False
                    else:
                        nchunk = camPathChunk([])

                    test_direction = directions[3]
                    last_direction = directions[3]
                    success = True
                    itests = 0
                # print('reset')
                if len(nchunk.points) > 0:
                    if nchunk.points[-1][0] + test_direction[0] < r:
                        testvect.x = r
                    if nchunk.points[-1][1] + test_direction[1] < r:
                        testvect.y = r
                    if nchunk.points[-1][0] + test_direction[0] > maxarx - r:
                        testvect.x = maxarx - r
                    if nchunk.points[-1][1] + test_direction[1] > maxary - r:
                        testvect.y = maxary - r

                dindexmod = dindex + testangulardistance
                while dindexmod < 0:
                    dindexmod += len(directions)
                while dindexmod > len(directions):
                    dindexmod -= len(directions)

                test_direction = directions[dindexmod]
                if 0:
                    print(xs, ys, test_direction, last_direction, testangulardistance)
                    print(totpix)
            itests += 1
            totaltests += 1

        i += 1
        if i % 100 == 0:
            # print('100 succesfull tests done')
            totpix = ar.sum()
            # print(totpix)
            # print(totaltests)
            i = 0
    chunks.append(nchunk)
    for ch in chunks:
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = ((ch[i][0] + coef - o.borderwidth) * o.pixsize + minx,
                     (ch[i][1] + coef - o.borderwidth) * o.pixsize + miny, ch[i][2])
    return chunks


def crazyPath(o):
    # TODO: try to do something with this  stuff, it's just a stub. It should be a greedy adaptive algorithm.
    #  started another thing below.
    prepareArea(o)
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.simulation_detail) + 2 * o.borderwidth
    resy = ceil(sy / o.simulation_detail) + 2 * o.borderwidth

    o.millimage = numpy.array((0.1), dtype=float)
    o.millimage.resize(resx, resy)
    o.millimage.fill(0)
    o.cutterArray = -simulation.getCutterArray(o, o.simulation_detail)  # getting inverted cutter


def buildStroke(start, end, cutterArray):
    strokelength = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
    size_x = abs(end[0] - start[0]) + cutterArray.size[0]
    size_y = abs(end[1] - start[1]) + cutterArray.size[0]
    r = cutterArray.size[0] / 2

    strokeArray = numpy.array((0), dtype=float)
    strokeArray.resize(size_x, size_y)
    strokeArray.fill(-10)
    samplesx = numpy.round(numpy.linspace(start[0], end[0], strokelength))
    samplesy = numpy.round(numpy.linspace(start[1], end[1], strokelength))
    samplesz = numpy.round(numpy.linspace(start[2], end[2], strokelength))

    for i in range(0, len(strokelength)):
        strokeArray[samplesx[i] - r:samplesx[i] + r, samplesy[i] - r:samplesy[i] + r] = numpy.maximum(
            strokeArray[samplesx[i] - r:samplesx[i] + r, samplesy[i] - r:samplesy[i] + r], cutterArray + samplesz[i])
    return strokeArray


def testStroke():
    pass


def applyStroke():
    pass


def testStrokeBinary(img, stroke):
    pass  # buildstroke()


def crazyStrokeImage(o):
    # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    r = int((o.cutter_diameter / 2.0) / o.pixsize)  # ceil((o.cutter_diameter/12)/o.pixsize)
    d = 2 * r
    coef = 0.75

    ar = o.offset_image.copy()
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = getCircleBinary(r)
    cutterArrayNegative = -cutterArray

    cutterimagepix = cutterArray.sum()
    satisfypix = cutterimagepix * o.crazy_threshold1  # a threshold which says if it is valuable to cut in a direction
    toomuchpix = cutterimagepix * o.crazy_threshold2
    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()  #
    totpix = startpix
    chunks = []
    xs = indices[0][0] - r
    if xs < r:
        xs = r
    ys = indices[1][0] - r
    if ys < r:
        ys = r
    nchunk = camPathChunk([(xs, ys)])  # startposition
    print(indices)
    print(indices[0][0], indices[1][0])
    lastvect = Vector((r, 0, 0))  # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    testvect = lastvect.normalized() * r / 2.0  # multiply *2 not to get values <1 pixel
    rot = Euler((0, 0, 1))
    i = 0
    perc = 0
    itests = 0
    totaltests = 0
    maxtests = 500
    maxtotaltests = 1000000

    print(xs, ys, indices[0][0], indices[1][0], r)
    ar[xs - r:xs - r + d, ys - r:ys - r + d] = ar[xs - r:xs - r + d, ys - r:ys - r + d] * cutterArrayNegative
    anglerange = [-pi, pi]  # range for angle of toolpath vector versus material vector
    testangleinit = 0
    angleincrement = 0.05
    if (o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CCW') or (
            o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CW'):
        anglerange = [-pi, 0]
        testangleinit = 1
        angleincrement = -angleincrement
    elif (o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CCW') or (
            o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CW'):
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
                testar = ar[xs - r:xs - r + d, ys - r:ys - r + d] * cutterArray
                if 0:
                    print('test')
                    print(testar.sum(), satisfypix)
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(totpix)

                eatpix = testar.sum()
                cindices = testar.nonzero()
                cx = cindices[0].sum() / eatpix
                cy = cindices[1].sum() / eatpix
                v = Vector((cx - r, cy - r))
                angle = testvect.to_2d().angle_signed(v)
                if anglerange[0] < angle < anglerange[1]:  # this could be righthanded milling? lets see :)
                    if toomuchpix > eatpix > satisfypix:
                        success = True
            if success:
                nchunk.points.append([xs, ys])
                lastvect = testvect
                ar[xs - r:xs - r + d, ys - r:ys - r + d] = ar[xs - r:xs - r + d, ys - r:ys - r + d] * (-cutterArray)
                totpix -= eatpix
                itests = 0
                if 0:
                    print('success')
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(itests)
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

                if abs(testangle) > o.crazy_threshold3:  # /testlength
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
                # if 0:
                #     print(xs, ys, testlength, testangle)
                #     print(lastvect)
                #     print(testvect)
                #     print(totpix)
            itests += 1
            totaltests += 1

            if itests > maxtests or testlength > r * 1.5:
                # print('resetting location')
                indices = ar.nonzero()
                chunks.append(nchunk)
                if len(indices[0]) > 0:
                    xs = indices[0][0] - r
                    if xs < r:
                        xs = r
                    ys = indices[1][0] - r
                    if ys < r:
                        ys = r
                    nchunk = camPathChunk([(xs, ys)])  # startposition
                    ar[xs - r:xs - r + d, ys - r:ys - r + d] = ar[xs - r:xs - r + d,
                                                               ys - r:ys - r + d] * cutterArrayNegative
                    r = random.random() * 2 * pi
                    e = Euler((0, 0, r))
                    testvect = lastvect.normalized() * 4  # multiply *2 not to get values <1 pixel
                    testvect.rotate(e)
                    lastvect = testvect.copy()
                success = True
                itests = 0
        i += 1
        if i % 100 == 0:
            print('100 succesfull tests done')
            totpix = ar.sum()
            print(totpix)
            print(totaltests)
            i = 0
    chunks.append(nchunk)
    for ch in chunks:
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = ((ch[i][0] + coef - o.borderwidth) * o.pixsize + minx,
                     (ch[i][1] + coef - o.borderwidth) * o.pixsize + miny, 0)
    return chunks


def crazyStrokeImageBinary(o, ar, avoidar):
    # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    # works like this:
    # start 'somewhere'
    # try to go in various directions.
    # if somewhere the cutter load is appropriate - it is correct magnitude and side, continue in that directon
    # try to continue straight or around that, looking
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    # TODO this should be somewhere else, but here it is now to get at least some ambient for start of the operation.
    ar[:o.borderwidth, :] = 0
    ar[-o.borderwidth:, :] = 0
    ar[:, :o.borderwidth] = 0
    ar[:, -o.borderwidth:] = 0

    r = int((o.cutter_diameter / 2.0) / o.pixsize)  # ceil((o.cutter_diameter/12)/o.pixsize)
    d = 2 * r
    coef = 0.75
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = getCircleBinary(r)
    cutterArrayNegative = -cutterArray

    cutterimagepix = cutterArray.sum()

    anglelimit = o.crazy_threshold3
    satisfypix = cutterimagepix * o.crazy_threshold1  # a threshold which says if it is valuable to cut in a direction
    toomuchpix = cutterimagepix * o.crazy_threshold2  # same, but upper limit
    optimalpix = cutterimagepix * o.crazy_threshold5  # (satisfypix+toomuchpix)/2.0# the ideal eating ratio
    indices = ar.nonzero()  # first get white pixels

    startpix = ar.sum()  #
    totpix = startpix

    chunks = []
    # try to find starting point here

    xs = indices[0][0] - r / 2
    if xs < r:
        xs = r
    ys = indices[1][0] - r
    if ys < r:
        ys = r

    nchunk = camPathChunk([(xs, ys)])  # startposition
    print(indices)
    print(indices[0][0], indices[1][0])
    lastvect = Vector((r, 0, 0))  # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    testvect = lastvect.normalized() * r / 4.0  # multiply *2 not to get values <1 pixel
    rot = Euler((0, 0, 1))
    i = 0
    itests = 0
    totaltests = 0
    maxtests = 2000
    maxtotaltests = 20000  # 1000000

    margin = 0

    # print(xs,ys,indices[0][0],indices[1][0],r)
    ar[xs - r:xs + r, ys - r:ys + r] = ar[xs - r:xs + r, ys - r:ys + r] * cutterArrayNegative
    anglerange = [-pi, pi]
    # range for angle of toolpath vector versus material vector -
    # probably direction negative to the force applied on cutter by material.
    testangleinit = 0
    angleincrement = o.crazy_threshold4

    if (o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CCW') or (
            o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CW'):
        anglerange = [-pi, 0]
        testangleinit = anglelimit
        angleincrement = -angleincrement
    elif (o.movement_type == 'CONVENTIONAL' and o.spindle_rotation_direction == 'CCW') or (
            o.movement_type == 'CLIMB' and o.spindle_rotation_direction == 'CW'):
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
            # print(xs,ys,ar.shape)
            # print(d)
            if xs > r + margin and xs < ar.shape[0] - r - margin and ys > r + margin and ys < ar.shape[1] - r - margin:
                # avoidtest=avoidar[xs-r:xs+r,ys-r:ys+r]*cutterArray
                if not avoidar[xs, ys]:
                    testar = ar[xs - r:xs + r, ys - r:ys + r] * cutterArray
                    eatpix = testar.sum()
                    cindices = testar.nonzero()
                    cx = cindices[0].sum() / eatpix
                    cy = cindices[1].sum() / eatpix
                    v = Vector((cx - r, cy - r))
                    # print(testvect.length,testvect)

                    if v.length != 0:
                        angle = testvect.to_2d().angle_signed(v)
                        if (anglerange[0] < angle < anglerange[1] and toomuchpix > eatpix > satisfypix) or (
                                eatpix > 0 and totpix < startpix * 0.025):
                            # this could be righthanded milling?
                            # lets see :)
                            # print(xs,ys,angle)
                            foundsolutions.append([testvect.copy(), eatpix])
                            if len(foundsolutions) >= 10:  # or totpix < startpix*0.025:
                                success = True
            itests += 1
            totaltests += 1

            if success:
                # fist, try to inter/extrapolate the recieved results.
                closest = 100000000
                # print('evaluate')
                for s in foundsolutions:
                    # print(abs(s[1]-optimalpix),optimalpix,abs(s[1]))
                    if abs(s[1] - optimalpix) < closest:
                        bestsolution = s
                        closest = abs(s[1] - optimalpix)
                # print('closest',closest)

                testvect = bestsolution[0]  # v1#+(v2-v1)*ratio#rewriting with interpolated vect.
                xs = int(nchunk.points[-1][0] + testvect.x)
                ys = int(nchunk.points[-1][1] + testvect.y)
                nchunk.points.append([xs, ys])
                lastvect = testvect

                ar[xs - r:xs + r, ys - r:ys + r] = ar[xs - r:xs + r, ys - r:ys + r] * cutterArrayNegative
                totpix -= bestsolution[1]
                itests = 0
                # if 0:
                #     print('success')
                #     print(testar.sum(), satisfypix, toomuchpix)
                #     print(xs, ys, testlength, testangle)
                #     print(lastvect)
                #     print(testvect)
                #     print(itests)
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

                if (abs(testangle) > o.crazy_threshold3 and len(nchunk.points) > 1) or abs(
                        testangle) > 2 * pi:  # /testlength
                    testangle = testangleinit
                    testlength += r / 4.0
                # print(itests,testlength)
                if nchunk.points[-1][0] + testvect.x < r:
                    testvect.x = r
                if nchunk.points[-1][1] + testvect.y < r:
                    testvect.y = r
                if nchunk.points[-1][0] + testvect.x > maxarx - r:
                    testvect.x = maxarx - r
                if nchunk.points[-1][1] + testvect.y > maxary - r:
                    testvect.y = maxary - r

                rot.z = testangle
                # if abs(testvect.normalized().y<-0.99):
                #   print(testvect,rot.z)
                testvect.rotate(rot)

                # if 0:
                #     print(xs, ys, testlength, testangle)
                #     print(lastvect)
                #     print(testvect)
                #     print(totpix)
                if itests > maxtests or testlength > r * 1.5:
                    # if len(foundsolutions)>0:

                    # print('resetting location')
                    # print(testlength,r)
                    andar = numpy.logical_and(ar, numpy.logical_not(avoidar))
                    indices = andar.nonzero()
                    if len(nchunk.points) > 1:
                        chunk.parentChildDist([nchunk], chunks, o, distance=r)
                        chunks.append(nchunk)

                    if totpix > startpix * 0.001:
                        found = False
                        ftests = 0
                        while not found:
                            # look for next start point:
                            index = random.randint(0, len(indices[0]) - 1)
                            # print(index,len(indices[0]))
                            # print(indices[index])
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

                                # print(toomuchpix,ar[xs-r:xs-r+d,ys-r:ys-r+d].sum()*pi/4,satisfypix)
                                testarsum = ar[xs - r:xs - r + d, ys - r:ys - r + d].sum() * pi / 4
                                if toomuchpix > testarsum > 0 or (
                                        totpix < startpix * 0.025):  # 0 now instead of satisfypix
                                    found = True
                                    # print(xs,ys,indices[0][index],indices[1][index])

                                    nchunk = camPathChunk([(xs, ys)])  # startposition
                                    ar[xs - r:xs + r, ys - r:ys + r] = ar[xs - r:xs + r,
                                                                       ys - r:ys + r] * cutterArrayNegative
                                    # lastvect=Vector((r,0,0))#vector is 3d,
                                    # blender somehow doesn't rotate 2d vectors with angles.
                                    randomrot = random.random() * 2 * pi
                                    e = Euler((0, 0, randomrot))
                                    testvect = lastvect.normalized() * 2  # multiply *2 not to get values <1 pixel
                                    testvect.rotate(e)
                                    lastvect = testvect.copy()
                            if ftests > 2000:
                                totpix = 0  # this quits the process now.
                            ftests += 1

                    success = True
                    itests = 0
        i += 1
        if i % 100 == 0:
            print('100 succesfull tests done')
            totpix = ar.sum()
            print(totpix)
            print(totaltests)
            i = 0
    if len(nchunk.points) > 1:
        chunk.parentChildDist([nchunk], chunks, o, distance=r)
        chunks.append(nchunk)

    for ch in chunks:
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = ((ch[i][0] + coef - o.borderwidth) * o.pixsize + minx,
                     (ch[i][1] + coef - o.borderwidth) * o.pixsize + miny, o.minz)

    return chunks


def imageToChunks(o, image, with_border=False):
    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.pixsize

    image = image.astype(numpy.uint8)

    # progress('detecting outline')
    edges = []
    ar = image[:, :-1] - image[:, 1:]

    indices1 = ar.nonzero()
    borderspread = 2
    # o.cutter_diameter/o.pixsize#when the border was excluded precisely, sometimes it did remove some silhouette parts
    r = o.borderwidth - borderspread
    # to prevent outline of the border was 3 before and also (o.cutter_diameter/2)/pixsize+o.borderwidth
    if with_border:
        #   print('border')
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
    # progress(len(edges))

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
        # progress('condensing outline')
        while len(
                d) > 0 and i < 20000000:
            verts = d.get(ch[-1], [])
            closed = False
            # print(verts)

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
                        pass
                        verts.remove(v)

                    if not take:
                        if (not white and comesfromtop) or (white and comesfrombottom):  # goes right
                            if v1[0] + 0.5 < v[0]:
                                take = True
                        elif (not white and comesfrombottom) or (white and comesfromtop):  # goes left
                            if v1[0] > v[0] + 0.5:
                                take = True
                        elif (not white and comesfromleft) or (white and comesfromright):  # goes down
                            if v1[1] > v[1] + 0.5:
                                take = True
                        elif (not white and comesfromright) or (white and comesfromleft):  # goes up
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
                            pass
                            verts.remove(v)
                        else:

                            ch.append(v)
                            done = True
                            verts.remove(v)
                            if v[0] == ch[0][0] and v[1] == ch[0][1]:  # or len(verts)<=1:
                                closed = True

            if closed:
                polychunks.append(ch)
                for si, s in enumerate(ch):
                    # print(si)
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

            # print(' la problema grandiosa')
            i += 1
            if i % 10000 == 0:
                print(len(ch))
                # print(polychunks)
                print(i)

        vecchunks = []

        for ch in polychunks:
            vecchunk = []
            vecchunks.append(vecchunk)
            for i in range(0, len(ch)):
                ch[i] = ((ch[i][0] + coef - o.borderwidth) * pixsize + minx,
                         (ch[i][1] + coef - o.borderwidth) * pixsize + miny, 0)
                vecchunk.append(Vector(ch[i]))
        # print('optimizing outline')

        # print('directsimplify')
        reduxratio = 1.25  # was 1.25
        soptions = ['distance', 'distance', o.pixsize * reduxratio, 5, o.pixsize * reduxratio]
        nchunks = []
        for i, ch in enumerate(vecchunks):

            s = curve_simplify.simplify_RDP(ch, soptions)
            # print(s)
            nch = camPathChunk([])
            for i in range(0, len(s)):
                nch.points.append((ch[s[i]].x, ch[s[i]].y))

            if len(nch.points) > 2:
                nchunks.append(nch)

        return nchunks
    else:
        return []


def imageToShapely(o, i, with_border=False):
    polychunks = imageToChunks(o, i, with_border)
    polys = chunksToShapely(polychunks)

    return polys


def getSampleImage(s, sarray, minz):
    x = s[0]
    y = s[1]
    if (x < 0 or x > len(sarray) - 1) or (y < 0 or y > len(sarray[0]) - 1):
        return -10
    else:
        minx = floor(x)
        maxx = minx + 1
        miny = floor(y)
        maxy = miny + 1
        s1a = sarray.item(minx, miny)  # most optimal access to array so far
        s2a = sarray.item(maxx, miny)
        s1b = sarray.item(minx, maxy)
        s2b = sarray.item(maxx, maxy)

        sa = s1a * (maxx - x) + s2a * (x - minx)
        sb = s1b * (maxx - x) + s2b * (x - minx)
        z = sa * (maxy - y) + sb * (y - miny)
        return z


def getResolution(o):
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.pixsize) + 2 * o.borderwidth
    resy = ceil(sy / o.pixsize) + 2 * o.borderwidth

# this basically renders blender zbuffer and makes it accessible by saving & loading it again.
# that's because blender doesn't allow accessing pixels in render :(


def renderSampleImage(o):
    t = time.time()
    simple.progress('getting zbuffer')
    # print(o.zbuffer_image)

    if o.geometry_source == 'OBJECT' or o.geometry_source == 'COLLECTION':
        pixsize = o.pixsize

        sx = o.max.x - o.min.x
        sy = o.max.y - o.min.y

        resx = math.ceil(sx / o.pixsize) + 2 * o.borderwidth
        resy = math.ceil(sy / o.pixsize) + 2 * o.borderwidth

        if not o.update_zbufferimage_tag and len(o.zbuffer_image) == resx and len(o.zbuffer_image[0]) == resy:
            # if we call this accidentally in more functions, which currently happens...
            # print('has zbuffer')
            return o.zbuffer_image
        # ###setup image name
        iname = getCachePath(o) + '_z.exr'
        if not o.update_zbufferimage_tag:
            try:
                i = bpy.data.images.load(iname)
            except:
                o.update_zbufferimage_tag = True
        if o.update_zbufferimage_tag:
            s = bpy.context.scene

            # prepare nodes first
            s.use_nodes = True
            n = s.node_tree

            n.links.clear()
            n.nodes.clear()
            n1 = n.nodes.new('CompositorNodeRLayers')
            n2 = n.nodes.new('CompositorNodeViewer')
            n3 = n.nodes.new('CompositorNodeComposite')
            n.links.new(n1.outputs['Depth'], n2.inputs['Image'])
            n.links.new(n1.outputs['Depth'], n3.inputs['Image'])
            n.nodes.active = n2
            ###################

            r = s.render
            r.resolution_x = resx
            r.resolution_y = resy

            # resize operation image
            o.offset_image.resize((resx, resy))
            o.offset_image.fill(-10)

            # various settings for  faster render
            r.tile_x = 1024  # ceil(resx/1024)
            r.tile_y = 1024  # ceil(resy/1024)
            r.resolution_percentage = 100

            r.engine = 'BLENDER_EEVEE'
            ff = r.image_settings.file_format
            cm = r.image_settings.color_mode
            r.image_settings.file_format = 'OPEN_EXR'
            r.image_settings.color_mode = 'BW'
            r.image_settings.color_depth = '32'

            # camera settings
            camera = s.camera
            if camera is None:
                bpy.ops.object.camera_add(align='WORLD', enter_editmode=False, location=(0, 0, 0),
                                          rotation=(0, 0, 0))
                camera = bpy.context.active_object
                bpy.context.scene.camera = camera

            camera.data.type = 'ORTHO'
            camera.data.ortho_scale = max(resx * o.pixsize, resy * o.pixsize)
            camera.location = (o.min.x + sx / 2, o.min.y + sy / 2, 1)
            camera.rotation_euler = (0, 0, 0)
            # if not o.render_all:#removed in 0.3

            h = []

            # ob=bpy.data.objects[o.object_name]
            for ob in s.objects:
                h.append(ob.hide_render)
                ob.hide_render = True
            for ob in o.objects:
                ob.hide_render = False

            bpy.ops.render.render()

            # if not o.render_all:
            for id, obs in enumerate(s.objects):
                obs.hide_render = h[id]

            imgs = bpy.data.images
            for isearch in imgs:
                if len(isearch.name) >= 13:
                    if isearch.name[:13] == 'Render Result':
                        i = isearch

                        # progress(iname)
                        i.save_render(iname)

            r.image_settings.file_format = ff
            r.image_settings.color_mode = cm

            i = bpy.data.images.load(iname)
            bpy.context.scene.render.engine = 'BLENDERCAM_RENDER'
        a = imagetonumpy(i)
        a = 1.0 - a
        o.zbuffer_image = a
        o.update_zbufferimage_tag = False

    else:
        i = bpy.data.images[o.source_image_name]
        if o.source_image_crop:
            sx = int(i.size[0] * o.source_image_crop_start_x / 100.0)
            ex = int(i.size[0] * o.source_image_crop_end_x / 100.0)
            sy = int(i.size[1] * o.source_image_crop_start_y / 100.0)
            ey = int(i.size[1] * o.source_image_crop_end_y / 100.0)
        else:
            sx = 0
            ex = i.size[0]
            sy = 0
            ey = i.size[1]

        o.offset_image.resize(ex - sx + 2 * o.borderwidth, ey - sy + 2 * o.borderwidth)

        o.pixsize = o.source_image_size_x / i.size[0]
        simple.progress('pixel size in the image source', o.pixsize)

        rawimage = imagetonumpy(i)
        maxa = numpy.max(rawimage)
        mina = numpy.min(rawimage)
        a = numpy.array((1.0, 1.0))
        a.resize(2 * o.borderwidth + i.size[0], 2 * o.borderwidth + i.size[1])
        neg = o.source_image_scale_z < 0
        if o.strategy == 'WATERLINE':  # waterline strategy needs image border to have ok ambient.
            a.fill(1 - neg)

        else:  # other operations like parallel need to reach the border
            a.fill(neg)  #
        # 2*o.borderwidth
        a[o.borderwidth:-o.borderwidth, o.borderwidth:-o.borderwidth] = rawimage
        a = a[sx:ex + o.borderwidth * 2, sy:ey + o.borderwidth * 2]

        if o.source_image_scale_z < 0:
            # negative images place themselves under the 0 plane by inverting through scale multiplication
            a = (a - mina)  # first, put the image down, se we know the image minimum is on 0
            a *= o.source_image_scale_z

        else:  # place positive images under 0 plane, this is logical
            a = (a - mina)  # first, put the image down, se we know the image minimum is on 0
            a *= o.source_image_scale_z
            a -= (maxa - mina) * o.source_image_scale_z

        a += o.source_image_offset.z  # after that, image gets offset.

        o.minz = numpy.min(a)  # TODO: I really don't know why this is here...
        o.min.z = numpy.min(a)
        print('min z ', o.min.z)
        print('max z ', o.max.z)
        print('max image ', numpy.max(a))
        print('min image ', numpy.min(a))
        o.zbuffer_image = a
    # progress('got z buffer also with conversion in:')
    simple.progress(time.time() - t)

    # progress(a)
    o.update_zbufferimage_tag = False
    return o.zbuffer_image


# return numpy.array([])

def prepareArea(o):
    # if not o.use_exact:
    renderSampleImage(o)
    samples = o.zbuffer_image

    iname = simple.getCachePath(o) + '_off.exr'

    if not o.update_offsetimage_tag:
        progress('loading offset image')
        try:
            o.offset_image = imagetonumpy(bpy.data.images.load(iname))

        except:
            o.update_offsetimage_tag = True

    if o.update_offsetimage_tag:
        if o.inverse:
            samples = numpy.maximum(samples, o.min.z - 0.00001)
        offsetArea(o, samples)
        numpysave(o.offset_image, iname)
