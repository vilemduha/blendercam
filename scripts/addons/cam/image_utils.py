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


def getCircle(r, z):
    car = numpy.array((0), dtype=float)
    res = 2 * r
    m = r
    car.resize(r * 2, r * 2)
    car.fill(-10)
    v = mathutils.Vector((0, 0, 0))
    for a in range(0, res):
        v.x = (a + 0.5 - m)
        for b in range(0, res):
            v.y = (b + 0.5 - m)
            if (v.length <= r):
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
def getCutterArray(operation, pixsize):
    type = operation.cutter_type
    # print('generating cutter')
    r = operation.cutter_diameter / 2 + operation.skin  # /operation.pixsize
    res = ceil((r * 2) / pixsize)
    # if res%2==0:#compensation for half-pixels issue, which wasn't an issue, so commented out
    # res+=1
    # m=res/2
    m = res / 2.0
    car = numpy.array((0), dtype=float)
    car.resize(res, res)
    car.fill(-10)

    v = mathutils.Vector((0, 0, 0))
    ps = pixsize
    if type == 'END':
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if (v.length <= r):
                    car.itemset((a, b), 0)
    elif type == 'BALL' or type == 'BALLNOSE':
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if (v.length <= r):
                    z = sin(acos(v.length / r)) * r - r
                    car.itemset((a, b), z)  # [a,b]=z

    elif type == 'VCARVE':
        angle = operation.cutter_tip_angle
        s = math.tan(math.pi * (90 - angle / 2) / 180)
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    z = (-v.length * s)
                    car.itemset((a, b), z)
    elif type == 'CUSTOM':
        cutob = bpy.data.objects[operation.cutter_object_name]
        scale = ((cutob.dimensions.x / cutob.scale.x) / 2) / r  #
        # print(cutob.scale)
        vstart = Vector((0, 0, -10))
        vend = Vector((0, 0, 10))
        print('sampling custom cutter')
        maxz = -1
        for a in range(0, res):
            vstart.x = (a + 0.5 - m) * ps * scale
            vend.x = vstart.x

            for b in range(0, res):
                vstart.y = (b + 0.5 - m) * ps * scale
                vend.y = vstart.y
                v = vend - vstart
                c = cutob.ray_cast(vstart, v, v.length)
                # print(c)
                if c[3] != -1:
                    z = -c[1][2] / scale
                    # print(c)
                    if z > -9:
                        # print(z)
                        if z > maxz:
                            maxz = z
                        car.itemset((a, b), z)
        car -= maxz
    return car


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
    # i.pixels=a this was 50 percent slower...
    i.pixels[:] = a[:]  # this gives big speedup!
    print('\ntime ' + str(time.time() - t))
    return i


def imagetonumpy(i):
    t = time.time()
    inc = 0

    width = i.size[0]
    height = i.size[1]
    x = 0
    y = 0
    count = 0
    na = numpy.array((0.1), dtype=float)

    size = width * height
    na.resize(size * 4)

    p = i.pixels[
        :]  # these 2 lines are about 15% faster than na[:]=i.pixels[:].... whyyyyyyyy!!?!?!?!?! Blender image data access is evil.
    na[:] = p
    # na=numpy.array(i.pixels[:])#this was terribly slow... at least I know why now, it probably
    na = na[::4]
    na = na.reshape(height, width)
    na = na.swapaxes(0, 1)

    print('\ntime of image to numpy ' + str(time.time() - t))
    return na


def offsetArea(o, samples):
    ''' offsets the whole image with the cutter + skin offsets '''
    if o.update_offsetimage_tag:
        minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
        o.offset_image.fill(-10)

        sourceArray = samples
        cutterArray = getCutterArray(o, o.pixsize)

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
            progress('offset ', int(x * 100 / cwidth))
            for y in range(0,
                           cwidth):  # TODO:OPTIMIZE THIS - this can run much faster when the areas won't be created each run????tests dont work now
                if cutterArray[x, y] > -10:
                    # i+=1
                    # progress(i)
                    # winner
                    numpy.maximum(sourceArray[x: width - cwidth + x, y: height - cwidth + y] + cutterArray[x, y],
                                  comparearea, comparearea)
                    # contest of performance
                    '''
					if bpy.app.debug_value==0 :#original
						comparearea=numpy.maximum(sourceArray[  x : width-cwidth+x ,y : height-cwidth+y]+cutterArray[x,y],comparearea)
					elif bpy.app.debug_value==1:
						narea = numpy.maximum(sourceArray[  x : width-cwidth+x ,y : height-cwidth+y]+cutterArray[x,y],comparearea)
						comparearea = narea
					elif bpy.app.debug_value==3:
						numpy.maximum(sourceArray[  x : width-cwidth+x ,y : height-cwidth+y]+cutterArray[x,y],comparearea, comparearea)
						'''

        o.offset_image[m: width - cwidth + m, m:height - cwidth + m] = comparearea
        # progress('offseting done')

        progress('\ntime ' + str(time.time() - t))

        o.update_offsetimage_tag = False
    # progress('doing offsetimage')
    # numpytoimage(o.offset_image,o)
    return o.offset_image


"""
deprecated function, currently not used anywhere inside blender CAM.
def outlineImageBinary(o,radius,i,offset):
	'''takes a binary image, and performs offset on it, something like delate/erode, just with circular patter. The oldest offset solution in Blender CAM. '''
	t=time.time()
	progress('outline image')
	r=ceil(radius/o.pixsize)
	c=getCircleBinary(r)
	w=len(i)
	h=len(i[0])
	oar=i.copy()
	#oar.fill(-10000000)
	
	ar = i[:,:-1] != i[:,1:] 
	indices1=ar.nonzero()
	if offset:
		dofunc=numpy.logical_or
	else:
		c=numpy.logical_not(c)
		dofunc=numpy.logical_and
	w=i.shape[0]
	h=i.shape[1]
	for id in range(0,len(indices1[0])):
		a=indices1[0].item(id)
		b=indices1[1].item(id)
		if a>r and b>r and a<w-r and b<h-r:
			#progress(oar.shape,c.shape)
			oar[a-r:a+r,b-r:b+r]=dofunc(oar[a-r:a+r,b-r:b+r],c)
		
	ar=i[:-1,:]!=i[1:,:]
	indices2=ar.nonzero()
	for id in range(0,len(indices2[0])):
		a=indices2[0].item(id)
		b=indices2[1].item(id)
		if a>r and b>r and a<w-r and b<h-r:
			#progress(oar.shape,c.shape)
			oar[a-r:a+r,b-r:b+r]=dofunc(oar[a-r:a+r,b-r:b+r],c)
	progress(time.time()-t)
	return oar

def outlineImage(o,radius,i,minz):
	'''takes a binary image, and performs offset on it, something like delate/erode, just with circular patter. The oldest offset solution in Blender CAM. was used to add ambient to the operation in the image based method'''
	minz=minz-0.0000001#correction test
	t=time.time()
	progress('outline image')
	r=ceil(radius/o.pixsize)
	c=getCircle(r,minz)
	w=len(i)
	h=len(i[0])
	oar=i.copy()
	#oar.fill(-10000000)
	for a in range(r,len(i)-1-r):
		for b in range(r,len(i[0])-1-r):
			p1=i[a,b]
			p2=i[a+1,b]
			p3=i[a,b+1]
			if p1<minz<p2 or p1>minz>p2 or p1<minz<p3 or p1>minz>p3:
				oar[a-r:a+r,b-r:b+r]=numpy.maximum(oar[a-r:a+r,b-r:b+r],c)
	progress(time.time()-t)
	return oar
"""


def dilateAr(ar, cycles):
    for c in range(cycles):
        ar[1:-1, :] = numpy.logical_or(ar[1:-1, :], ar[:-2, :])
        # ar[1:-1,:]=numpy.logical_or(ar[1:-1,:],ar[2:,:] )
        ar[:, 1:-1] = numpy.logical_or(ar[:, 1:-1], ar[:, :-2])


# ar[:,1:-1]=numpy.logical_or(ar[:,1:-1],ar[:,2:] )

def getOffsetImageCavities(o, i):  # for pencil operation mainly
    '''detects areas in the offset image which are 'cavities' - the curvature changes.'''
    # i=numpy.logical_xor(lastislice , islice)
    progress('detect corners in the offset image')
    vertical = i[:-2, 1:-1] - i[1:-1, 1:-1] - o.pencil_threshold > i[1:-1, 1:-1] - i[2:, 1:-1]
    horizontal = i[1:-1, :-2] - i[1:-1, 1:-1] - o.pencil_threshold > i[1:-1, 1:-1] - i[1:-1, 2:]
    # if bpy.app.debug_value==2:

    ar = numpy.logical_or(vertical, horizontal)

    if 0:  # this is newer strategy, finds edges nicely, but pff.going exacty on edge, it has tons of spikes and simply is not better than the old one
        iname = getCachePath(o) + '_pencilthres.exr'
        # numpysave(ar,iname)#save for comparison before
        chunks = imageEdgeSearch_online(o, ar, i)
        iname = getCachePath(o) + '_pencilthres_comp.exr'
    # numpysave(ar,iname)#and after
    else:  # here is the old strategy with
        dilateAr(ar, 1)
        iname = getCachePath(o) + '_pencilthres.exr'
        # numpysave(ar,iname)#save for comparison before

        chunks = imageToChunks(o, ar)

        for ch in chunks:  # convert 2d chunks to 3d
            for i, p in enumerate(ch.points):
                ch.points[i] = (p[0], p[1], 0)

        chunks = chunksRefine(chunks, o)

    ###crop pixels that are on outer borders
    for chi in range(len(chunks) - 1, -1, -1):
        chunk = chunks[chi]
        for si in range(len(chunk.points) - 1, -1, -1):
            if not (o.min.x < chunk.points[si][0] < o.max.x and o.min.y < chunk.points[si][1] < o.max.y):
                chunk.points.pop(si)
        if len(chunk.points) < 2:
            chunks.pop(chi)

    return chunks


def imageEdgeSearch_online(o, ar, zimage):  # search edges for pencil strategy, another try.
    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.pixsize
    edges = []

    r = 3  # ceil((o.cutter_diameter/12)/o.pixsize)
    d = 2 * r
    coef = 0.75
    # sx=o.max.x-o.min.x
    # sy=o.max.y-o.min.y
    # size=ar.shape[0]
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    directions = ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))

    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()  #
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
    maxtests = 500
    maxtotaltests = startpix * 4

    ar[xs, ys] = False

    while totpix > 0 and totaltests < maxtotaltests:  # a ratio when the algorithm is allowed to end

        if perc != int(100 - 100 * totpix / startpix):
            perc = int(100 - 100 * totpix / startpix)
            progress('pencil path searching', perc)
        # progress('simulation ',int(100*i/l))
        success = False
        testangulardistance = 0  # distance from initial direction in the list of direction
        testleftright = False  # test both sides from last vector
        # achjo=0
        while not success:
            # print(achjo)
            # achjo+=1
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

                # dindex=directions.index(last_direction)
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
        # vecchunk=[]
        # vecchunks.append(vecchunk)
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = (
            (ch[i][0] + coef - o.borderwidth) * o.pixsize + minx, (ch[i][1] + coef - o.borderwidth) * o.pixsize + miny,
            ch[i][2])
    # vecchunk.append(Vector(ch[i]))
    return chunks


def simCutterSpot(xs, ys, z, cutterArray, si, getvolume=False):
    '''simulates a cutter cutting into stock, taking away the volume, and optionally returning the volume that has been milled. This is now used for feedrate tweaking.'''
    # xs=int(xs)
    # ys=int(ys)
    m = int(cutterArray.shape[0] / 2)
    size = cutterArray.shape[0]
    if xs > m and xs < si.shape[0] - m and ys > m and ys < si.shape[1] - m:  # whole cutter in image there
        if getvolume:
            volarray = si[xs - m:xs - m + size, ys - m:ys - m + size].copy()
        si[xs - m:xs - m + size, ys - m:ys - m + size] = numpy.minimum(si[xs - m:xs - m + size, ys - m:ys - m + size],
                                                                       cutterArray + z)
        if getvolume:
            volarray = si[xs - m:xs - m + size, ys - m:ys - m + size] - volarray
            vsum = abs(volarray.sum())
            # print(vsum)
            return vsum

    elif xs > -m and xs < si.shape[0] + m and ys > -m and ys < si.shape[
        1] + m:  # part of cutter in image, for extra large cutters

        startx = max(0, xs - m)
        starty = max(0, ys - m)
        endx = min(si.shape[0], xs - m + size)
        endy = min(si.shape[0], ys - m + size)
        castartx = max(0, m - xs)
        castarty = max(0, m - ys)
        caendx = min(size, si.shape[0] - xs + m)
        caendy = min(size, si.shape[1] - ys + m)
        # print(startx,endx,starty,endy,castartx,caendx,castarty, caendy)
        if getvolume:
            volarray = si[startx:endx, starty:endy].copy()
        si[startx:endx, starty:endy] = numpy.minimum(si[startx:endx, starty:endy],
                                                     cutterArray[castartx:caendx, castarty:caendy] + z)
        if getvolume:
            volarray = si[startx:endx, starty:endy] - volarray
            vsum = abs(volarray.sum())
            # print(vsum)
            return vsum

    return 0


def generateSimulationImage(operations, limits):
    minx, miny, minz, maxx, maxy, maxz = limits
    # print(minx,miny,minz,maxx,maxy,maxz)
    sx = maxx - minx
    sy = maxy - miny
    t = time.time()
    o = operations[0]  # getting sim detail and others from first op.
    simulation_detail = o.simulation_detail
    borderwidth = o.borderwidth
    resx = ceil(sx / simulation_detail) + 2 * borderwidth
    resy = ceil(sy / simulation_detail) + 2 * borderwidth
    # resx=ceil(sx/o.pixsize)+2*o.borderwidth
    # resy=ceil(sy/o.pixsize)+2*o.borderwidth
    # create array in which simulation happens, similar to an image to be painted in.
    si = numpy.array((0.1), dtype=float)
    si.resize(resx, resy)
    si.fill(maxz)

    for o in operations:
        ob = bpy.data.objects["cam_path_{}".format(o.name)]
        m = ob.data
        verts = m.vertices

        if o.do_simulation_feedrate:
            kname = 'feedrates'
            m.use_customdata_edge_crease = True

            if m.shape_keys is None or m.shape_keys.key_blocks.find(kname) == -1:
                ob.shape_key_add()
                if len(m.shape_keys.key_blocks) == 1:
                    ob.shape_key_add()
                shapek = m.shape_keys.key_blocks[-1]
                shapek.name = kname
            else:
                shapek = m.shape_keys.key_blocks[kname]
            shapek.data[0].co = (0.0, 0, 0)
        # print(len(shapek.data))
        # print(len(verts_rotations))

        # for i,co in enumerate(verts_rotations):#TODO: optimize this. this is just rewritten too many times...
        # print(r)
        #	shapek.data[i].co=co

        totalvolume = 0.0

        cutterArray = getCutterArray(o, simulation_detail)
        # cb=cutterArray<-1
        # cutterArray[cb]=1
        cutterArray = -cutterArray
        mid = int(cutterArray.shape[0] / 2)
        size = cutterArray.shape[0]
        # print(si.shape)
        # for ch in chunks:
        lasts = verts[1].co
        perc = -1
        vtotal = len(verts)
        dropped = 0

        xs = 0
        ys = 0

        for i, vert in enumerate(verts):
            if perc != int(100 * i / vtotal):
                perc = int(100 * i / vtotal)
                progress('simulation', perc)
            # progress('simulation ',int(100*i/l))

            if i > 0:
                volume = 0
                volume_partial = 0
                s = vert.co
                v = s - lasts

                l = v.length
                if (lasts.z < maxz or s.z < maxz) and not (
                        v.x == 0 and v.y == 0 and v.z > 0):  # only simulate inside material, and exclude lift-ups
                    if (
                            v.x == 0 and v.y == 0 and v.z < 0):  # if the cutter goes straight down, we don't have to interpolate.
                        pass;

                    elif v.length > simulation_detail:  # and not :

                        v.length = simulation_detail
                        lastxs = xs
                        lastys = ys
                        while v.length < l:
                            xs = int((
                                                 lasts.x + v.x - minx) / simulation_detail + borderwidth + simulation_detail / 2)  # -middle
                            ys = int((
                                                 lasts.y + v.y - miny) / simulation_detail + borderwidth + simulation_detail / 2)  # -middle
                            z = lasts.z + v.z
                            # print(z)
                            if lastxs != xs or lastys != ys:
                                volume_partial = simCutterSpot(xs, ys, z, cutterArray, si, o.do_simulation_feedrate)
                                if o.do_simulation_feedrate:
                                    totalvolume += volume
                                    volume += volume_partial
                                lastxs = xs
                                lastys = ys
                            else:
                                dropped += 1
                            v.length += simulation_detail

                    xs = int((s.x - minx) / simulation_detail + borderwidth + simulation_detail / 2)  # -middle
                    ys = int((s.y - miny) / simulation_detail + borderwidth + simulation_detail / 2)  # -middle
                    volume_partial = simCutterSpot(xs, ys, s.z, cutterArray, si, o.do_simulation_feedrate)
                if o.do_simulation_feedrate:  # compute volumes and write data into shapekey.
                    volume += volume_partial
                    totalvolume += volume
                    if l > 0:
                        load = volume / l
                    else:
                        load = 0

                    # this will show the shapekey as debugging graph and will use same data to estimate parts with heavy load
                    if l != 0:
                        shapek.data[i].co.y = (load) * 0.000002
                    else:
                        shapek.data[i].co.y = shapek.data[i - 1].co.y
                    shapek.data[i].co.x = shapek.data[i - 1].co.x + l * 0.04
                    shapek.data[i].co.z = 0
                lasts = s

        # print('dropped '+str(dropped))
        if o.do_simulation_feedrate:  # smoothing ,but only backward!
            xcoef = shapek.data[len(shapek.data) - 1].co.x / len(shapek.data)
            for a in range(0, 10):
                # print(shapek.data[-1].co)
                nvals = []
                val1 = 0  #
                val2 = 0
                w1 = 0  #
                w2 = 0

                for i, d in enumerate(shapek.data):
                    val = d.co.y

                    if i > 1:
                        d1 = shapek.data[i - 1].co
                        val1 = d1.y
                        if d1.x - d.co.x != 0:
                            w1 = 1 / (abs(d1.x - d.co.x) / xcoef)

                    if i < len(shapek.data) - 1:
                        d2 = shapek.data[i + 1].co
                        val2 = d2.y
                        if d2.x - d.co.x != 0:
                            w2 = 1 / (abs(d2.x - d.co.x) / xcoef)

                    # print(val,val1,val2,w1,w2)

                    val = (val + val1 * w1 + val2 * w2) / (1.0 + w1 + w2)
                    nvals.append(val)
                for i, d in enumerate(shapek.data):
                    d.co.y = nvals[i]

            # apply mapping - convert the values to actual feedrates.
            total_load = 0
            max_load = 0
            for i, d in enumerate(shapek.data):
                total_load += d.co.y
                max_load = max(max_load, d.co.y)
            normal_load = total_load / len(shapek.data)

            thres = 0.5

            scale_graph = 0.05  # warning this has to be same as in export in utils!!!!

            totverts = len(shapek.data)
            for i, d in enumerate(shapek.data):
                if d.co.y > normal_load:
                    d.co.z = scale_graph * max(0.3,
                                               normal_load / d.co.y)  # original method was : max(0.4,1-2*(d.co.y-max_load*thres)/(max_load*(1-thres)))
                else:
                    d.co.z = scale_graph * 1
                if i < totverts - 1:
                    m.edges[i].crease = d.co.y / (normal_load * 4)

    # d.co.z*=0.01#debug

    o = operations[0]
    si = si[borderwidth:-borderwidth, borderwidth:-borderwidth]
    si += -minz

    # print(si.shape[0],si.shape[1])

    # print('simulation done in %f seconds' % (time.time()-t))
    return si


def crazyPath(
        o):  # TODO: try to do something with this  stuff, it's just a stub. It should be a greedy adaptive algorithm. started another thing below.
    MAX_BEND = 0.1  # in radians...#TODO: support operation chains ;)
    prepareArea(o)
    # o.millimage =
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.simulation_detail) + 2 * o.borderwidth
    resy = ceil(sy / o.simulation_detail) + 2 * o.borderwidth

    o.millimage = numpy.array((0.1), dtype=float)
    o.millimage.resize(resx, resy)
    o.millimage.fill(0)
    o.cutterArray = -getCutterArray(o, o.simulation_detail)  # getting inverted cutter
    crazy = camPathChunk([(0, 0, 0)])
    testpos = (o.min.x, o.min.y, o.min.z)


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
        # strokeArray(samplesx[i]-r:samplesx[i]+r,samplesy[i]-r:samplesy[i]+r)
        # strokeArray(samplesx[i]-r:samplesx[i]+r,samplesy[i]-r:samplesy[i]+r)
        # cutterArray+samplesz[i]
        strokeArray[samplesx[i] - r:samplesx[i] + r, samplesy[i] - r:samplesy[i] + r] = numpy.maximum(
            strokeArray[samplesx[i] - r:samplesx[i] + r, samplesy[i] - r:samplesy[i] + r], cutterArray + samplesz[i])
    return strokeArray


def testStroke():
    pass;


def applyStroke():
    pass;


def testStrokeBinary(img, stroke):
    pass;  # buildstroke()


def crazyStrokeImage(
        o):  # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.pixsize
    edges = []

    r = int((o.cutter_diameter / 2.0) / o.pixsize)  # ceil((o.cutter_diameter/12)/o.pixsize)
    d = 2 * r
    coef = 0.75
    # sx=o.max.x-o.min.x
    # sy=o.max.y-o.min.y
    # size=ar.shape[0]

    ar = o.offset_image.copy()
    sampleimage = o.offset_image
    finalstate = o.zbuffer_image
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = getCircleBinary(r)
    cutterArrayNegative = -cutterArray
    # cutterArray=1-cutterArray

    cutterimagepix = cutterArray.sum()
    # ar.fill(True)
    satisfypix = cutterimagepix * o.crazy_threshold1  # a threshold which says if it is valuable to cut in a direction
    toomuchpix = cutterimagepix * o.crazy_threshold2
    indices = ar.nonzero()  # first get white pixels
    startpix = ar.sum()  #
    totpix = startpix
    chunks = []
    xs = indices[0][0] - r
    if xs < r: xs = r
    ys = indices[1][0] - r
    if ys < r: ys = r
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

        # if perc!=int(100*totpix/startpix):
        #   perc=int(100*totpix/startpix)
        #   progress('crazy path searching what to mill!',perc)
        # progress('simulation ',int(100*i/l))
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
                # nchunk.append([xs,ys])#for debugging purpose
                # ar.shape[0]
                # TODO: after all angles were tested into material higher than toomuchpix, it should cancel, otherwise there is no problem with long travel in free space.....
                # TODO:the testing should start not from the same angle as lastvector, but more towards material. So values closer to toomuchpix are obtained rather than satisfypix
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

                '''
				if testlength>10:#weird test 
					indices1=ar.nonzero()
					nchunk.append(indices1[0])
					lastvec=Vector((1,0,0))
					testvec=Vector((1,0,0))
					testlength=r
					success=True
				'''
                rot.z = testangle

                testvect.rotate(rot)
                if 0:
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(totpix)
            itests += 1
            totaltests += 1
            # achjo
            if itests > maxtests or testlength > r * 1.5:
                # print('resetting location')
                indices = ar.nonzero()
                chunks.append(nchunk)
                if len(indices[0]) > 0:
                    index = random.randint(0, len(indices[0]) - 1)
                    # print(index,len(indices[0]))
                    xs = indices[0][0] - r
                    if xs < r: xs = r
                    ys = indices[1][0] - r
                    if ys < r: ys = r
                    nchunk = camPathChunk([(xs, ys)])  # startposition
                    ar[xs - r:xs - r + d, ys - r:ys - r + d] = ar[xs - r:xs - r + d,
                                                               ys - r:ys - r + d] * cutterArrayNegative
                    # lastvect=Vector((r,0,0))#vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
                    r = random.random() * 2 * pi
                    e = Euler((0, 0, r))
                    testvect = lastvect.normalized() * 4  # multiply *2 not to get values <1 pixel
                    testvect.rotate(e)
                    lastvect = testvect.copy()
                success = True
                itests = 0
        # xs=(s.x-o.min.x)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
        # ys=(s.y-o.min.y)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
        i += 1
        if i % 100 == 0:
            print('100 succesfull tests done')
            totpix = ar.sum()
            print(totpix)
            print(totaltests)
            i = 0
    chunks.append(nchunk)
    for ch in chunks:
        # vecchunk=[]
        # vecchunks.append(vecchunk)
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = (
            (ch[i][0] + coef - o.borderwidth) * o.pixsize + minx, (ch[i][1] + coef - o.borderwidth) * o.pixsize + miny,
            0)
    # vecchunk.append(Vector(ch[i]))
    return chunks


def crazyStrokeImageBinary(o, ar,
                           avoidar):  # this surprisingly works, and can be used as a basis for something similar to adaptive milling strategy.
    # works like this:
    # start 'somewhere'
    # try to go in various directions.
    # if somewhere the cutter load is appropriate - it is correct magnitude and side, continue in that directon
    # try to continue straight or around that, looking
    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.pixsize
    edges = []
    # TODO this should be somewhere else, but here it is now to get at least some ambient for start of the operation.
    ar[:o.borderwidth, :] = 0
    ar[-o.borderwidth:, :] = 0
    ar[:, :o.borderwidth] = 0
    ar[:, -o.borderwidth:] = 0
    debug = numpytoimage(ar, 'start')

    r = int((o.cutter_diameter / 2.0) / o.pixsize)  # ceil((o.cutter_diameter/12)/o.pixsize)
    d = 2 * r
    coef = 0.75
    # sx=o.max.x-o.min.x
    # sy=o.max.y-o.min.y
    # size=ar.shape[0]
    maxarx = ar.shape[0]
    maxary = ar.shape[1]

    cutterArray = getCircleBinary(r)
    cutterArrayNegative = -cutterArray
    # cutterArray=1-cutterArray

    cutterimagepix = cutterArray.sum()
    # ar.fill(True)

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
    if xs < r: xs = r
    ys = indices[1][0] - r
    if ys < r: ys = r

    nchunk = camPathChunk([(xs, ys)])  # startposition
    print(indices)
    print(indices[0][0], indices[1][0])
    lastvect = Vector((r, 0, 0))  # vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
    testvect = lastvect.normalized() * r / 4.0  # multiply *2 not to get values <1 pixel
    rot = Euler((0, 0, 1))
    i = 0
    perc = 0
    itests = 0
    totaltests = 0
    maxtests = 2000
    maxtotaltests = 20000  # 1000000

    margin = 0

    # print(xs,ys,indices[0][0],indices[1][0],r)
    ar[xs - r:xs + r, ys - r:ys + r] = ar[xs - r:xs + r, ys - r:ys + r] * cutterArrayNegative
    anglerange = [-pi,
                  pi]  # range for angle of toolpath vector versus material vector - probably direction negative to the force applied on cutter by material.
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

        # if perc!=int(100*totpix/startpix):
        #   perc=int(100*totpix/startpix)
        #   progress('crazy path searching what to mill!',perc)
        # progress('simulation ',int(100*i/l))
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
                    if 0:
                        print('test')
                        print(testar.sum(), satisfypix, toomuchpix)
                        print(xs, ys, testlength, testangle)
                        print(lastvect)
                        print(testvect)
                        print(totpix)

                    eatpix = testar.sum()
                    cindices = testar.nonzero()
                    cx = cindices[0].sum() / eatpix
                    cy = cindices[1].sum() / eatpix
                    v = Vector((cx - r, cy - r))
                    # print(testvect.length,testvect)

                    if v.length != 0:
                        angle = testvect.to_2d().angle_signed(v)
                        # if angle>pi:
                        # print('achjo\n\n\n\n\n',angle)
                        if (anglerange[0] < angle < anglerange[1] and toomuchpix > eatpix > satisfypix) or (
                                eatpix > 0 and totpix < startpix * 0.025):  # this could be righthanded milling? lets see :)
                            # print(xs,ys,angle)
                            foundsolutions.append([testvect.copy(), eatpix])
                            if len(foundsolutions) >= 10:  # or totpix < startpix*0.025:
                                success = True
            itests += 1
            totaltests += 1
            # achjo

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
                '''
				v1=foundsolutions[0][0]
				v2=foundsolutions[1][0]
				pix1=foundsolutions[0][1]
				pix2=foundsolutions[1][1]
				if pix1 == pix2:
					ratio=0.5
				else:
					ratio=((optimalpix-pix1)/(pix2-pix1))
				print(v2,v1,pix1,pix2)
				print(ratio)
				'''
                testvect = bestsolution[0]  # v1#+(v2-v1)*ratio#rewriting with interpolated vect.
                xs = int(nchunk.points[-1][0] + testvect.x)
                ys = int(nchunk.points[-1][1] + testvect.y)
                # if xs>r+margin and xs<ar.shape[0]-r-margin and ys>r+margin and ys<ar.shape[1]-r-margin :
                # nchunk.points.append([xs+v.x,ys+v.y])
                nchunk.points.append([xs, ys])
                lastvect = testvect

                ar[xs - r:xs + r, ys - r:ys + r] = ar[xs - r:xs + r, ys - r:ys + r] * cutterArrayNegative
                totpix -= bestsolution[1]
                itests = 0
                if 0:
                    print('success')
                    print(testar.sum(), satisfypix, toomuchpix)
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(itests)
                totaltests = 0
            else:
                # nchunk.append([xs,ys])#for debugging purpose
                # ar.shape[0]
                # TODO: after all angles were tested into material higher than toomuchpix, it should cancel, otherwise there is no problem with long travel in free space.....
                # TODO:the testing should start not from the same angle as lastvector, but more towards material. So values closer to toomuchpix are obtained rather than satisfypix
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

                '''
				if testlength>10:#weird test 
					indices1=ar.nonzero()
					nchunk.append(indices1[0])
					lastvec=Vector((1,0,0))
					testvec=Vector((1,0,0))
					testlength=r
					success=True
				'''
                rot.z = testangle
                # if abs(testvect.normalized().y<-0.99):
                #	print(testvect,rot.z)
                testvect.rotate(rot)

                if 0:
                    print(xs, ys, testlength, testangle)
                    print(lastvect)
                    print(testvect)
                    print(totpix)
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
                            # xs=random.randint(r,maxarx-r)
                            # ys=random.randint(r,maxary-r)
                            xs = indices[0][index]
                            ys = indices[1][index]
                            v = Vector((r - 1, 0, 0))
                            randomrot = random.random() * 2 * pi
                            e = Euler((0, 0, randomrot))
                            v.rotate(e)
                            xs += int(v.x)
                            ys += int(v.y)
                            if xs < r: xs = r
                            if ys < r: ys = r
                            '''
								avoidtest=avoidar[xs-r:xs+r,ys-r:ys+r]*cutterArray
								asum=avoidtest.sum()
								if asum>0:
									cindices=avoidtest.nonzero()
									cx=cindices[0].sum()/asum
									cy=cindices[1].sum()/asum
									v=Vector((cx-r,cy-r))
									print(v,r)
									v.length=max(1,r-v.length)
									xs-=v.x
									ys-=v.y
								'''
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
                                    # lastvect=Vector((r,0,0))#vector is 3d, blender somehow doesn't rotate 2d vectors with angles.
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
        # xs=(s.x-o.min.x)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
        # ys=(s.y-o.min.y)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
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
    # chunks=setChunksZ(chunks,o.minz)
    debug = numpytoimage(ar, 'debug')
    debug = numpytoimage(cutterArray, 'debil')

    for ch in chunks:
        # vecchunk=[]
        # vecchunks.append(vecchunk)
        ch = ch.points
        for i in range(0, len(ch)):
            ch[i] = (
            (ch[i][0] + coef - o.borderwidth) * o.pixsize + minx, (ch[i][1] + coef - o.borderwidth) * o.pixsize + miny,
            o.minz)

    # vecchunk.append(Vector(ch[i]))
    return chunks


def imageToChunks(o, image, with_border=False):
    t = time.time()
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    pixsize = o.pixsize

    # progress('detecting outline')
    edges = []
    ar = image[:, :-1] - image[:, 1:]

    indices1 = ar.nonzero()
    borderspread = 2  # o.cutter_diameter/o.pixsize#when the border was excluded precisely, sometimes it did remove some silhouette parts
    r = o.borderwidth - borderspread  # to prevent outline of the border was 3 before and also (o.cutter_diameter/2)/pixsize+o.borderwidth
    if with_border:
        #	print('border')
        r = 0  # o.borderwidth/2
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

    i = 0
    chi = 0

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

    # progress(time.time()-t)
    t = time.time()
    if len(edges) > 0:

        ch = [edges[0][0], edges[0][1]]  # first and his reference

        d[edges[0][0]].remove(edges[0][1])
        # d.pop(edges[0][0])

        i = 0
        # verts=[123]
        specialcase = 0
        closed = False
        # progress('condensing outline')
        while len(
                d) > 0 and i < 20000000:  # and verts!=[]:  ####bacha na pripade krizku takzvane, kdy dva pixely na sebe uhlopricne jsou
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
                # if specialcase>=2:
                # print('thisisit')
                v1 = ch[-1]
                v2 = ch[-2]
                white = image[v1[0], v1[1]]
                comesfromtop = v1[1] < v2[1]
                comesfrombottom = v1[1] > v2[1]
                comesfromleft = v1[0] > v2[0]
                comesfromright = v1[0] < v2[0]
                take = False
                for v in verts:
                    if (v[0] == ch[-2][0] and v[1] == ch[-2][1]):
                        pass;
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
                    #   break

            else:  # here it has to be 2 always
                done = False
                for vi in range(len(verts) - 1, -1, -1):
                    if not done:
                        v = verts[vi]
                        if (v[0] == ch[-2][0] and v[1] == ch[-2][1]):
                            pass
                            verts.remove(v)
                        else:

                            ch.append(v)
                            done = True
                            verts.remove(v)
                            if (v[0] == ch[0][0] and v[1] == ch[0][1]):  # or len(verts)<=1:
                                closed = True

            if closed:
                polychunks.append(ch)
                for si, s in enumerate(ch):
                    # print(si)
                    if si > 0:  # first one was popped
                        if d.get(s, None) != None and len(
                                d[s]) == 0:  # this makes the case much less probable, but i think not impossible
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

        # polychunks.append(ch)

        vecchunks = []

        for ch in polychunks:
            vecchunk = []
            vecchunks.append(vecchunk)
            for i in range(0, len(ch)):
                ch[i] = (
                (ch[i][0] + coef - o.borderwidth) * pixsize + minx, (ch[i][1] + coef - o.borderwidth) * pixsize + miny,
                0)
                vecchunk.append(Vector(ch[i]))
        t = time.time()
        # print('optimizing outline')

        # print('directsimplify')
        reduxratio = 1.25  # was 1.25
        soptions = ['distance', 'distance', o.pixsize * reduxratio, 5, o.pixsize * reduxratio]
        # soptions=['distance','distance',0.0,5,0,5,0]#o.pixsize*1.25,5,o.pixsize*1.25]
        # polychunks=[]
        nchunks = []
        for i, ch in enumerate(vecchunks):

            s = curve_simplify.simplify_RDP(ch, soptions)
            # print(s)
            nch = camPathChunk([])
            for i in range(0, len(s)):
                nch.points.append((ch[s[i]].x, ch[s[i]].y))

            if len(nch.points) > 2:
                # polychunks[i].points=nch
                nchunks.append(nch)
        # m=

        return nchunks
    else:
        return []


def imageToShapely(o, i, with_border=False):
    polychunks = imageToChunks(o, i, with_border)
    polys = chunksToShapely(polychunks)

    t = time.time()

    return polys  # [polys]


def getSampleImage(s, sarray, minz):
    x = s[0]
    y = s[1]
    if (x < 0 or x > len(sarray) - 1) or (y < 0 or y > len(sarray[0]) - 1):
        return -10
    # return None;#(sarray[y,x] bugs
    else:
        # return(sarray[int(x),int(y)])
        minx = floor(x)
        maxx = minx + 1
        # maxx=ceil(x)
        # if maxx==minx:
        #	maxx+=1
        miny = floor(y)
        maxy = miny + 1
        # maxy=ceil(y)
        # if maxy==miny:
        #	maxy+=1
        # if maxx-1!=minx or maxy-1!=miny:
        #	print('not right')

        '''
		s1a=sarray[minx,miny]#
		s2a=sarray[maxx,miny]
		s1b=sarray[minx,maxy]
		s2b=sarray[maxx,maxy]
		'''
        # if bpy.app.debug_value == 0:
        s1a = sarray.item(minx, miny)  # most optimal access to array so far
        s2a = sarray.item(maxx, miny)
        s1b = sarray.item(minx, maxy)
        s2b = sarray.item(maxx, maxy)
        # elif 0:#bpy.app.debug_value >0:
        #	sar=sarray[minx:maxx+1,miny:maxy]
        #	s1a=sar.item(0,0)
        #	s2a=sar.item(1,0)
        #	s1b=sar.item(0,1)
        #	s2b=sar.item(1,1)
        # elif bpy.app.debug_value >0:
        #	s1a,s2a,s1b,s2b=sarray[minx:maxx+1,miny:maxy+1]
        # if s1a==minz and s2a==minz and s1b==minz and s2b==minz:
        #  return
        '''
		if min(s1a,s2a,s1b,s2b)<-10:
			#return -10
			if s1a<-10:
				s1a=s2a
			if s2a<-10:
				s2a=s1a
			if s1b<-10:
				s1b=s2b
			if s2b<-10:
				s2b=s1b
	
			sa=s1a*(maxx-x)+s2a*(x-minx)
			sb=s1b*(maxx-x)+s2b*(x-minx)
			if sa<-10:
				sa=sb
			if sb<-10:
				sb=sa
			z=sa*(maxy-y)+sb*(y-miny)
			return z
			
		else:
		'''
        sa = s1a * (maxx - x) + s2a * (x - minx)
        sb = s1b * (maxx - x) + s2b * (x - minx)
        z = sa * (maxy - y) + sb * (y - miny)
        return z


def getResolution(o):
    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y

    resx = ceil(sx / o.pixsize) + 2 * o.borderwidth
    resy = ceil(sy / o.pixsize) + 2 * o.borderwidth


# def renderZbuffer():

# this basically renders blender zbuffer and makes it accessible by saving & loading it again.
# that's because blender doesn't allow accessing pixels in render :(
def renderSampleImage(o):
    t = time.time()
    progress('getting zbuffer')
    # print(o.zbuffer_image)

    if o.geometry_source == 'OBJECT' or o.geometry_source == 'GROUP':
        pixsize = o.pixsize

        sx = o.max.x - o.min.x
        sy = o.max.y - o.min.y

        resx = ceil(sx / o.pixsize) + 2 * o.borderwidth
        resy = ceil(sy / o.pixsize) + 2 * o.borderwidth

        if not o.update_zbufferimage_tag and len(o.zbuffer_image) == resx and len(o.zbuffer_image[
                                                                                      0]) == resy:  # if we call this accidentally in more functions, which currently happens...
            # print('has zbuffer')
            return o.zbuffer_image
        ####setup image name
        # fn=bpy.data.filepath
        # iname=bpy.path.abspath(fn)
        # l=len(bpy.path.basename(fn))
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
            n.links.new(n1.outputs['Z'], n2.inputs['Image'])
            n.links.new(n1.outputs['Z'], n3.inputs['Image'])
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

            r.engine = 'BLENDER_RENDER'
            r.use_antialiasing = False
            r.use_raytrace = False
            r.use_shadows = False
            ff = r.image_settings.file_format
            cm = r.image_settings.color_mode
            r.image_settings.file_format = 'OPEN_EXR'
            r.image_settings.color_mode = 'BW'
            r.image_settings.color_depth = '32'

            # camera settings
            camera = s.camera
            if camera == None:
                bpy.ops.object.camera_add(align='WORLD', enter_editmode=False, location=(0, 0, 0),
                                          rotation=(0, 0, 0))
                camera = bpy.context.active_object
                bpy.context.scene.camera = camera
            # bpy.ops.view3d.object_as_camera()

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
        progress('pixel size in the image source', o.pixsize)

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

        if o.source_image_scale_z < 0:  # negative images place themselves under the 0 plane by inverting through scale multiplication
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
    progress(time.time() - t)

    # progress(a)
    o.update_zbufferimage_tag = False
    return o.zbuffer_image


# return numpy.array([])

def prepareArea(o):
    # if not o.use_exact:
    renderSampleImage(o)
    samples = o.zbuffer_image

    iname = getCachePath(o) + '_off.exr'

    if not o.update_offsetimage_tag:
        progress('loading offset image')
        try:
            o.offset_image = imagetonumpy(bpy.data.images.load(iname))

        except:
            o.update_offsetimage_tag = True;

    if o.update_offsetimage_tag:
        if o.inverse:
            samples = numpy.maximum(samples, o.min.z - 0.00001)
        offsetArea(o, samples)
        numpysave(o.offset_image, iname)
