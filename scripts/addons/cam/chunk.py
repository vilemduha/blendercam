# blender CAM chunk.py (c) 2012 Vilem Novak
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


import shapely
from shapely.geometry import polygon as spolygon
from shapely import ops
from shapely import geometry as sgeometry
from cam import polygon_utils_cam
from cam import simple
from cam.simple import *


class camPathChunk:
    # parents=[]
    # children=[]
    # sorted=False

    # progressIndex=-1# for e.g. parallel strategy, when trying to save time..
    def __init__(self, inpoints, startpoints=None, endpoints=None, rotations=None):
        if len(inpoints) > 2:
            self.poly = sgeometry.Polygon(inpoints)
        else:
            self.poly = sgeometry.Polygon()
        self.points = inpoints  # for 3 axes, this is only storage of points. For N axes, here go the sampled points
        if startpoints:
            self.startpoints = startpoints  # from where the sweep test begins, but also retract point for given path
        else:
            self.startpoints = []
        if endpoints:
            self.endpoints = endpoints
        else:
            self.endpoints = []  # where sweep test ends
        if rotations:
            self.rotations = rotations
        else:
            self.rotations = []  # rotation of the machine axes
        self.closed = False
        self.children = []
        self.parents = []
        # self.unsortedchildren=False
        self.sorted = False  # if the chunk has allready been milled in the simulation
        self.length = 0;  # this is total length of this chunk.
        self.zstart = 0  # this is stored for ramps mainly, because they are added afterwards, but have to use layer info
        self.zend = 0  #

    def copy(self):
        nchunk = camPathChunk([])
        nchunk.points.extend(self.points)
        nchunk.startpoints.extend(self.startpoints)
        nchunk.endpoints.extend(self.endpoints)
        nchunk.rotations.extend(self.rotations)
        nchunk.closed = self.closed
        nchunk.children = self.children
        nchunk.parents = self.parents
        nchunk.sorted = self.sorted
        nchunk.length = self.length
        return nchunk

    def shift(self, x, y, z):

        for i, p in enumerate(self.points):
            self.points[i] = (p[0] + x, p[1] + y, p[2] + z)
        for i, p in enumerate(self.startpoints):
            self.startpoints[i] = (p[0] + x, p[1] + y, p[2] + z)
        for i, p in enumerate(self.endpoints):
            self.endpoints[i] = (p[0] + x, p[1] + y, p[2] + z)

    def setZ(self, z):
        for i, p in enumerate(self.points):
            self.points[i] = (p[0], p[1], z)

    def isbelowZ(self, z):
        isbelow = False
        for p in (self.points):
            if p[2] <= z:
                isbelow = True
        return isbelow

    def clampZ(self, z):
        for i, p in enumerate(self.points):
            if p[2] < z:
                self.points[i] = (p[0], p[1], z)

    def dist(self, pos, o):
        if self.closed:
            mind = 10000000
            minv = -1
            for vi in range(0, len(self.points)):
                v = self.points[vi]
                # print(v,pos)
                d = dist2d(pos, v)
                if d < mind:
                    mind = d
                    minv = vi
            return mind
        else:
            if o.movement_type == 'MEANDER':
                d1 = dist2d(pos, self.points[0])
                d2 = dist2d(pos, self.points[-1])
                # if d2<d1:
                #   ch.points.reverse()
                return min(d1, d2)
            else:
                return dist2d(pos, self.points[0])

    def distStart(self, pos, o):
        return dist2d(pos, self.points[0])

    def adaptdist(self, pos, o):
        # reorders chunk so that it starts at the closest point to pos.
        if self.closed:
            mind = 10000000
            minv = -1
            for vi in range(0, len(self.points)):
                v = self.points[vi]
                # print(v,pos)
                d = dist2d(pos, v)
                if d < mind:
                    mind = d
                    minv = vi

            newchunk = []
            newchunk.extend(self.points[minv:])
            newchunk.extend(self.points[:minv + 1])
            self.points = newchunk


        else:
            if o.movement_type == 'MEANDER':
                d1 = dist2d(pos, self.points[0])
                d2 = dist2d(pos, self.points[-1])
                if d2 < d1:
                    self.points.reverse()

    # replaced with getNextClosest
    # def getNext(self):#this should be deprecated after reworking sortchunks a bit
    #	for child in self.children:
    #		if child.sorted==False:
    #			#unsortedchildren=True
    #			return child.getNext()
    # self.unsortedchildren=False
    #	return self

    def getNextClosest(self, o, pos):
        # finds closest chunk that can be milled, when inside sorting hierarchy.
        mind = 100000000000

        self.cango = False
        closest = None
        testlist = []
        testlist.extend(self.children)
        tested = []
        tested.extend(self.children)
        ch = None
        while len(testlist) > 0:
            chtest = testlist.pop()
            if chtest.sorted == False:
                self.cango = False
                cango = True

                for child in chtest.children:
                    if child.sorted == False:
                        if child not in tested:
                            testlist.append(child)
                            tested.append(child)
                        cango = False

                if cango:
                    d = chtest.dist(pos, o)
                    if d < mind:
                        ch = chtest
                        mind = d
        if ch != None:
            # print('found some')
            return ch
        # print('returning none')
        return None

    def getLength(self):
        # computes length of the chunk - in 3d
        self.length = 0

        for vi, v1 in enumerate(self.points):
            # print(len(self.points),vi)
            v2 = Vector(v1)  # this is for case of last point and not closed chunk..
            if self.closed and vi == len(self.points) - 1:
                v2 = Vector(self.points[0])
            elif vi < len(self.points) - 1:
                v2 = Vector(self.points[vi + 1])
            v1 = Vector(v1)
            v = v2 - v1
            self.length += v.length

    # print(v,pos)

    def reverse(self):
        self.points.reverse()
        self.startpoints.reverse()
        self.endpoints.reverse()
        self.rotations.reverse()

    def pop(self, index):
        self.points.pop(index)
        if len(self.startpoints) > 0:
            self.startpoints.pop(index)
            self.endpoints.pop(index)
            self.rotations.pop(index)

    def append(self, point, startpoint=None, endpoint=None, rotation=None):
        self.points.append(point)
        if startpoint != None:
            self.startpoints.append(startpoint)
        if endpoint != None:
            self.endpoints.append(endpoint)
        if rotation != None:
            self.rotations.append(rotation)

    def rampContour(self, zstart, zend, o):

        stepdown = zstart - zend
        ch = self
        chunk = camPathChunk([])
        estlength = (zstart - zend) / tan(o.ramp_in_angle)
        ch.getLength()
        ramplength = estlength  # min(ch.length,estlength)
        ltraveled = 0
        endpoint = None
        i = 0
        # z=zstart
        znew = 10
        rounds = 0  # for counting if ramping makes more layers
        while endpoint == None and not (znew == zend and i == 0):  #
            # for i,s in enumerate(ch.points):
            # print(i, znew, zend, len(ch.points))
            s = ch.points[i]

            if i > 0:
                s2 = ch.points[i - 1]
                ltraveled += dist2d(s, s2)
                ratio = ltraveled / ramplength
            elif rounds > 0 and i == 0:
                s2 = ch.points[-1]
                ltraveled += dist2d(s, s2)
                ratio = ltraveled / ramplength
            else:
                ratio = 0
            znew = zstart - stepdown * ratio
            if znew <= zend:

                ratio = ((z - zend) / (z - znew))
                v1 = Vector(chunk.points[-1])
                v2 = Vector((s[0], s[1], znew))
                v = v1 + ratio * (v2 - v1)
                chunk.points.append((v.x, v.y, max(s[2], v.z)))

                if zend == o.min.z and endpoint == None and ch.closed == True:
                    endpoint = i + 1
                    if endpoint == len(ch.points):
                        endpoint = 0
            # print(endpoint,len(ch.points))
            # else:
            znew = max(znew, zend, s[2])
            chunk.points.append((s[0], s[1], znew))
            z = znew
            if endpoint != None:
                break;
            i += 1
            if i >= len(ch.points):
                i = 0
                rounds += 1
        # if not o.use_layers:
        #	endpoint=0
        if endpoint != None:  # append final contour on the bottom z level
            i = endpoint
            started = False
            # print('finaliz')
            if i == len(ch.points):
                i = 0
            while i != endpoint or not started:
                started = True
                s = ch.points[i]
                chunk.points.append((s[0], s[1], s[2]))
                # print(i,endpoint)
                i += 1
                if i == len(ch.points):
                    i = 0
        # ramp out
        if o.ramp_out and (not o.use_layers or o.first_down == False or (o.first_down and endpoint != None)):
            z = zend
            # i=endpoint

            while z < o.maxz:
                if i == len(ch.points):
                    i = 0
                s1 = ch.points[i]
                i2 = i - 1
                if i2 < 0: i2 = len(ch.points) - 1
                s2 = ch.points[i2]
                l = dist2d(s1, s2)
                znew = z + tan(o.ramp_out_angle) * l
                if znew > o.maxz:
                    ratio = ((z - o.maxz) / (z - znew))
                    v1 = Vector(chunk.points[-1])
                    v2 = Vector((s1[0], s1[1], znew))
                    v = v1 + ratio * (v2 - v1)
                    chunk.points.append((v.x, v.y, v.z))

                else:
                    chunk.points.append((s1[0], s1[1], znew))
                z = znew
                i += 1

        self.points = chunk.points

    def rampZigZag(self, zstart, zend, o):
        chunk = camPathChunk([])
        # print(zstart,zend)
        if zend < zstart:  # this check here is only for stupid setup, when the chunks lie actually above operation start z.

            stepdown = zstart - zend
            ch = self

            estlength = (zstart - zend) / tan(o.ramp_in_angle)
            ch.getLength()
            if ch.length > 0:  # for single point chunks..
                ramplength = estlength
                zigzaglength = ramplength / 2.000
                turns = 1
                print('turns %i' % turns)
                if zigzaglength > ch.length:
                    turns = ceil(zigzaglength / ch.length)
                    ramplength = turns * ch.length * 2.0
                    zigzaglength = ch.length
                    ramppoints = ch.points

                else:
                    zigzagtraveled = 0.0
                    haspoints = False
                    ramppoints = [(ch.points[0][0], ch.points[0][1], ch.points[0][2])]
                    i = 1
                    while not haspoints:
                        # print(i,zigzaglength,zigzagtraveled)
                        p1 = ramppoints[-1]
                        p2 = ch.points[i]
                        d = dist2d(p1, p2)
                        zigzagtraveled += d
                        if zigzagtraveled >= zigzaglength or i + 1 == len(ch.points):
                            ratio = 1 - (zigzagtraveled - zigzaglength) / d
                            if (i + 1 == len(
                                    ch.points)):  # this condition is for a rare case of combined layers+bridges+ramps...
                                ratio = 1
                            # print((ratio,zigzaglength))
                            v1 = Vector(p1)
                            v2 = Vector(p2)
                            v = v1 + ratio * (v2 - v1)
                            ramppoints.append((v.x, v.y, v.z))
                            haspoints = True
                        # elif :

                        else:
                            ramppoints.append(p2)
                        i += 1
                negramppoints = ramppoints.copy()
                negramppoints.reverse()
                ramppoints.extend(negramppoints[1:])

                traveled = 0.0
                chunk.points.append((ch.points[0][0], ch.points[0][1], max(ch.points[0][2], zstart)))
                for r in range(turns):
                    for p in range(0, len(ramppoints)):
                        p1 = chunk.points[-1]
                        p2 = ramppoints[p]
                        d = dist2d(p1, p2)
                        traveled += d
                        ratio = traveled / ramplength
                        znew = zstart - stepdown * ratio
                        chunk.points.append((p2[0], p2[1], max(p2[2],
                                                               znew)))  # max value here is so that it doesn't go below surface in the case of 3d paths

                # chunks = setChunksZ([ch],zend)
                chunk.points.extend(ch.points)

            ######################################
            # ramp out - this is the same thing, just on the other side..
            if o.ramp_out:
                zstart = o.maxz
                zend = ch.points[-1][2]
                if zend < zstart:  # again, sometimes a chunk could theoretically end above the starting level.
                    stepdown = zstart - zend

                    estlength = (zstart - zend) / tan(o.ramp_out_angle)
                    ch.getLength()
                    if ch.length > 0:
                        ramplength = estlength
                        zigzaglength = ramplength / 2.000
                        turns = 1
                        print('turns %i' % turns)
                        if zigzaglength > ch.length:
                            turns = ceil(zigzaglength / ch.length)
                            ramplength = turns * ch.length * 2.0
                            zigzaglength = ch.length
                            ramppoints = ch.points.copy()
                            ramppoints.reverse()  # revert points here, we go the other way.

                        else:
                            zigzagtraveled = 0.0
                            haspoints = False
                            ramppoints = [(ch.points[-1][0], ch.points[-1][1], ch.points[-1][2])]
                            i = len(ch.points) - 2
                            while not haspoints:
                                # print(i,zigzaglength,zigzagtraveled)
                                p1 = ramppoints[-1]
                                p2 = ch.points[i]
                                d = dist2d(p1, p2)
                                zigzagtraveled += d
                                if zigzagtraveled >= zigzaglength or i + 1 == len(ch.points):
                                    ratio = 1 - (zigzagtraveled - zigzaglength) / d
                                    if (i + 1 == len(
                                            ch.points)):  # this condition is for a rare case of combined layers+bridges+ramps...
                                        ratio = 1
                                    # print((ratio,zigzaglength))
                                    v1 = Vector(p1)
                                    v2 = Vector(p2)
                                    v = v1 + ratio * (v2 - v1)
                                    ramppoints.append((v.x, v.y, v.z))
                                    haspoints = True
                                # elif :

                                else:
                                    ramppoints.append(p2)
                                i -= 1
                        negramppoints = ramppoints.copy()
                        negramppoints.reverse()
                        ramppoints.extend(negramppoints[1:])

                        traveled = 0.0
                        # chunk.points.append((ch.points[0][0],ch.points[0][1],max(ch.points[0][1],zstart)))
                        for r in range(turns):
                            for p in range(0, len(ramppoints)):
                                p1 = chunk.points[-1]
                                p2 = ramppoints[p]
                                d = dist2d(p1, p2)
                                traveled += d
                                ratio = 1 - (traveled / ramplength)
                                znew = zstart - stepdown * ratio
                                chunk.points.append((p2[0], p2[1], max(p2[2],
                                                                       znew)))  # max value here is so that it doesn't go below surface in the case of 3d paths
        self.points = chunk.points


# def appendChunk(sorted,ch,o,pos)

def chunksCoherency(chunks):
    # checks chunks for their stability, for pencil path. it checks if the vectors direction doesn't jump too much too quickly, if this happens it splits the chunk on such places, too much jumps = deletion of the chunk. this is because otherwise the router has to slow down too often, but also means that some parts detected by cavity algorithm won't be milled
    nchunks = []
    for chunk in chunks:
        if len(chunk.points) > 2:
            nchunk = camPathChunk([])

            # doesn't check for 1 point chunks here, they shouldn't get here at all.
            lastvec = Vector(chunk.points[1]) - Vector(chunk.points[0])
            for i in range(0, len(chunk.points) - 1):
                nchunk.points.append(chunk.points[i])
                vec = Vector(chunk.points[i + 1]) - Vector(chunk.points[i])
                angle = vec.angle(lastvec, vec)
                # print(angle,i)
                if angle > 1.07:  # 60 degrees is maximum toleration for pencil paths.
                    if len(nchunk.points) > 4:  # this is a testing threshold
                        nchunks.append(nchunk)
                    nchunk = camPathChunk([])
                lastvec = vec
            if len(nchunk.points) > 4:  # this is a testing threshold
                nchunks.append(nchunk)
    return nchunks


def setChunksZ(chunks, z):
    newchunks = []
    for ch in chunks:
        chunk = ch.copy()
        chunk.setZ(z)
        newchunks.append(chunk)
    return newchunks


def optimizeChunk(chunk, operation):
    if len(chunk.points) > 2:
        points = chunk.points

        chunk.points = [points[0]]
        naxispoints = False
        if len(chunk.startpoints) > 0:
            startpoints = chunk.startpoints
            endpoints = chunk.endpoints
            chunk.startpoints = [startpoints[0]]
            chunk.endpoints = [endpoints[0]]
            rotations = chunk.rotations
            chunk.rotations = [rotations[
                                   0]]  # TODO FIRST THIS ROTATIONS E.T.C. NEED TO MAKE A POINT ADDING FUNCTION SINCE THIS IS A MESS, WOULD BE TOO MUCH IF'S
            naxispoints = True
        # if len(chunk.rotations)>0:

        '''this was replaced by append. Pop method was much much slower! still testing however.
        for vi in range(len(chunk.points)-2,0,-1):
            #vmiddle=Vector()
            #v1=Vector()
            #v2=Vector()
            if compare(chunk.points[vi-1],chunk.points[vi+1],chunk.points[vi],operation.optimize_threshold):
                
                chunk.pop(vi)
        '''
        protect_vertical = operation.protect_vertical and operation.machine_axes == '3'
        for vi in range(0, len(points) - 1):
            # vmiddle=Vector()
            # v1=Vector()
            # v2=Vector()
            if not compare(chunk.points[-1], points[vi + 1], points[vi], operation.optimize_threshold * 0.000001):
                if naxispoints:
                    chunk.append(points[vi], startpoints[vi], endpoints[vi], rotations[vi])
                else:
                    chunk.points.append(points[vi])
                if protect_vertical:
                    v1 = chunk.points[-1]
                    v2 = chunk.points[-2]
                    v1c, v2c = isVerticalLimit(v1, v2, operation.protect_vertical_limit)
                    if v1c != v1:  # TODO FIX THIS FOR N AXIS?
                        chunk.points[-1] = v1c
                    elif v2c != v2:
                        chunk.points[-2] = v2c
        # add last point
        if naxispoints:
            chunk.append(points[-1], startpoints[-1], endpoints[-1], rotations[-1])
        else:
            chunk.points.append(points[-1])
        # =True
        '''
        if:#protect vertical surfaces so far only for 3 axes..doesn't have now much logic for n axes, right? or does it?
            #print('verticality test')
            
            
            for vi in range(len(chunk.points)-1,0,-1):
                v1=chunk.points[vi]
                v2=chunk.points[vi-1]
                v1c,v2c=isVerticalLimit(v1,v2,operation.protect_vertical_limit)
                if v1c!=v1:
                    chunk.points[vi]=v1c
                elif v2c!=v2:
                    chunk.points[vi-1]=v2c
                
                
            #print(vcorrected)
        '''
    return chunk


def limitChunks(chunks, o,
                force=False):  # TODO: this should at least add point on area border... but shouldn't be needed at all at the first place...
    if o.use_limit_curve or force:
        nchunks = []
        for ch in chunks:
            prevsampled = True
            nch = camPathChunk([])
            nch1 = nch
            closed = True
            for s in ch.points:
                sampled = o.ambient.contains(sgeometry.Point(s[0], s[1]))
                if not sampled and len(nch.points) > 0:
                    nch.closed = False
                    closed = False
                    nchunks.append(nch)
                    nch = camPathChunk([])
                elif sampled:
                    nch.points.append(s)
                prevsampled = sampled
            if len(nch.points) > 2 and closed and ch.closed and ch.points[0] == ch.points[1]:
                nch.closed = True
            elif ch.closed and nch != nch1 and len(nch.points) > 1 and nch.points[-1] == nch1.points[
                0]:  # here adds beginning of closed chunk to the end, if the chunks were split during limiting
                nch.points.extend(nch1.points)
                nchunks.remove(nch1)
                print('joining stuff')
            if len(nch.points) > 0:
                nchunks.append(nch)
        return nchunks
    else:
        return chunks


def parentChildPoly(parents, children, o):
    # hierarchy based on polygons - a polygon inside another is his child.
    # hierarchy works like this: - children get milled first.

    for parent in parents:
        # print(parent.poly)
        for child in children:
            # print(child.poly)
            if child != parent:  # and len(child.poly)>0
                if parent.poly.contains(sgeometry.Point(child.poly.boundary.coords[0])):
                    parent.children.append(child)
                    child.parents.append(parent)


def parentChildDist(parents, children, o, distance=None):
    # parenting based on x,y distance between chunks
    # hierarchy works like this: - children get milled first.
    if distance == None:
        dlim = o.dist_between_paths * 2
        if (o.strategy == 'PARALLEL' or o.strategy == 'CROSS') and o.parallel_step_back:
            dlim = dlim * 2
    else:
        dlim = distance
    # print('distance')
    # print(len(children),len(parents))
    # i=0
    # simplification greatly speeds up the distance finding algorithms.
    for child in children:
        if not child.poly.is_empty:
            child.simppoly = child.poly.simplify(0.0003).boundary
    for parent in parents:
        if not parent.poly.is_empty:
            parent.simppoly = parent.poly.simplify(0.0003).boundary

    for child in children:
        for parent in parents:
            # print(len(children),len(parents))
            isrelation = False
            if parent != child:
                if not parent.poly.is_empty and not child.poly.is_empty:
                    # print(dir(parent.simppoly))
                    d = parent.simppoly.distance(child.simppoly)
                    if d < dlim:
                        isrelation = True
                else:  # this is the old method, preferably should be replaced in most cases except parallell where this method works probably faster.
                    # print('warning, sorting will be slow due to bad parenting in parentChildDist')
                    for v in child.points:
                        for v1 in parent.points:
                            if dist2d(v, v1) < dlim:
                                isrelation = True
                                break
                        if isrelation:
                            break
                if isrelation:
                    # print('truelink',dist2d(v,v1))
                    parent.children.append(child)
                    child.parents.append(parent)


# print('distance done')

'''
def parentChildDist(parents, children,o, distance= None):
	#parenting based on distance between chunks
	#hierarchy works like this: - children get milled first.
	if distance==None:
		dlim=o.dist_between_paths*2
		if (o.strategy=='PARALLEL' or o.strategy=='CROSS') and o.parallel_step_back:
			dlim=dlim*2
	else:
		dlim = distance
		
	for child in children:
		for parent in parents:
			isrelation=False
			if parent!=child:
				for v in child.points:
					for v1 in parent.points:
						
						if dist2d(v,v1)<dlim:
							isrelation=True
							break
					if isrelation:
						break
				if isrelation:
					#print('truelink',dist2d(v,v1))
					parent.children.append(child)
					child.parents.append(parent)
'''


def parentChild(parents, children, o):
    # connect all children to all parents. Useful for any type of defining hierarchy.
    # hierarchy works like this: - children get milled first.

    for child in children:
        for parent in parents:
            if parent != child:
                parent.children.append(child)
                child.parents.append(parent)


def chunksToShapely(chunks):  # this does more cleve chunks to Poly with hierarchies... ;)
    # print ('analyzing paths')
    # verts=[]
    # pverts=[]
    polys = []
    for ch in chunks:  # first convert chunk to poly
        if len(ch.points) > 2:
            # pchunk=[]
            ch.poly = sgeometry.Polygon(ch.points)

    for ppart in chunks:  # then add hierarchy relations
        for ptest in chunks:

            # if ppart!=ptest and len(ptest.poly)>0 and len(ppart.poly)>0 and ptest.poly.nPoints(0)>0 and ppart.poly.nPoints(0)>0:
            if ppart != ptest:
                if ptest.poly.contains(ppart.poly):
                    # hierarchy works like this: - children get milled first.
                    # ptest.children.append(ppart)
                    ppart.parents.append(ptest)

    for ch in chunks:  # now make only simple polygons with holes, not more polys inside others
        # print(len(chunks[polyi].parents))
        found = False
        if len(ch.parents) % 2 == 1:

            for parent in ch.parents:
                if len(parent.parents) + 1 == len(ch.parents):
                    ch.nparents = [
                        parent]  # nparents serves as temporary storage for parents, not to get mixed with the first parenting during the check
                    found = True
                    break

        if not found:
            ch.nparents = []

    for ch in chunks:  # then subtract the 1st level holes
        ch.parents = ch.nparents
        ch.nparents = None
        if len(ch.parents) > 0:
            # print(len(ch.parents))
            # ch.parents[0].poly=ch.parents[0].poly-ch.poly
            # print(ch.parents[0].poly,[ch.poly])
            print('addparent')
            # polygon_utils_cam.shapelyToCurve('crust',ch.parents[0].poly,0)
            # polygon_utils_cam.shapelyToCurve('hole',ch.poly,0)
            try:
                ch.parents[0].poly = ch.parents[0].poly.difference(
                    ch.poly)  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)
            except:

                print('chunksToShapely oops!')

                lastPt = False
                tolerance = 0.0000003
                newPoints = []

                for pt in ch.points:
                    toleranceXok = True
                    toleranceYok = True
                    # print( '{0:.9f}, {1:.9f}, {2:.9f}'.format(pt[0], pt[1], pt[2]) )
                    # print(pt)
                    if lastPt:
                        # print( 'Distance Vector: {0:.9f}, {1:.9f}'.format(abs(pt[0] - lastPt[0]), abs(pt[1] - lastPt[1])) )
                        # print( 'pt[0] is {} tolerance'.format( 'OUT of' if abs( pt[0] - lastPt[0] ) < tolerance else 'IN' ) )
                        # print( 'pt[1] is {} tolerance'.format( 'OUT of' if abs( pt[1] - lastPt[1] ) < tolerance else 'IN' ) )
                        if (abs(pt[0] - lastPt[0]) < tolerance):
                            toleranceXok = False
                        if (abs(pt[1] - lastPt[1]) < tolerance):
                            toleranceYok = False

                        if (toleranceXok or toleranceYok):
                            # print('point ok, including')
                            # ch.points.remove( pt )
                            newPoints.append(pt)
                            lastPt = pt
                    else:
                        newPoints.append(pt)
                        lastPt = pt

                toleranceXok = True
                toleranceYok = True
                if (abs(newPoints[0][0] - lastPt[0]) < tolerance):
                    toleranceXok = False
                if (abs(newPoints[0][1] - lastPt[1]) < tolerance):
                    toleranceYok = False

                if (not toleranceXok and not toleranceYok):
                    newPoints.pop()
                # print('starting and ending points too close, removing ending point')

                # if ( abs( lastPt[0] - ch.points[0][0] ) < tolerance ):
                # if ( abs( lastPt[1] - ch.points[0][1] ) < tolerance ):
                # newPoints.pop()
                # print('starting and ending points too close, removing ending point')

                ch.points = newPoints
                ch.poly = sgeometry.Polygon(ch.points)

                try:
                    ch.parents[0].poly = ch.parents[0].poly.difference(
                        ch.poly)  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)

                except:

                    # print('chunksToShapely double oops!')

                    lastPt = False
                    tolerance = 0.0000003
                    newPoints = []

                    for pt in ch.parents[0].points:
                        toleranceXok = True
                        toleranceYok = True
                        # print( '{0:.9f}, {0:.9f}, {0:.9f}'.format(pt[0], pt[1], pt[2]) )
                        # print(pt)
                        if lastPt:
                            # print( 'Distance Vector: {0:.9f}, {0:.9f}'.format((pt[0] - lastPt[0]), (pt[1] - lastPt[1])) )
                            if (abs(pt[0] - lastPt[0]) < tolerance):
                                toleranceXok = False
                            if (abs(pt[1] - lastPt[1]) < tolerance):
                                toleranceYok = False

                            if (toleranceXok or toleranceYok):
                                # print('point ok, including')
                                # ch.points.remove( pt )
                                newPoints.append(pt)
                                lastPt = pt
                        else:
                            newPoints.append(pt)
                            lastPt = pt

                    toleranceXok = True
                    toleranceYok = True
                    if (abs(newPoints[0][0] - lastPt[0]) < tolerance):
                        toleranceXok = False
                    if (abs(newPoints[0][1] - lastPt[1]) < tolerance):
                        toleranceYok = False

                    if (not toleranceXok and not toleranceYok):
                        newPoints.pop()
                    # print('starting and ending points too close, removing ending point')

                    # if ( abs( lastPt[0] - ch.parents[0].points[0][0] ) < tolerance ):
                    # if ( abs( lastPt[1] - ch.parents[0].points[0][1] ) < tolerance ):
                    # newPoints.pop()
                    # print('starting and ending points too close, removing ending point')

                    ch.parents[0].points = newPoints
                    ch.parents[0].poly = sgeometry.Polygon(ch.parents[0].points)

                    ch.parents[0].poly = ch.parents[0].poly.difference(
                        ch.poly)  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)

    # p=spolygon.Polygon(ch.points)
    # p.simplify(1.0, preserve_topology=False)
    # sc=shapelyToChunks(p,0)

    # pParent=spolygon.Polygon(ch.parents[0].points)
    # pParent.simplify(1.0, preserve_topology=False)
    # scParent=shapelyToChunks(pParent,0)

    # ch.parents[0].poly = scParent[0].poly.difference(sc[0].poly)

    # print('points dumped.!')

    returnpolys = []

    for polyi in range(0, len(chunks)):  # export only the booleaned polygons
        ch = chunks[polyi]
        if len(ch.parents) == 0:
            # ch.poly.simplify()#TODO:THIS CHECK
            returnpolys.append(ch.poly)
    # if len(ch.poly.interiors)>0:
    #	print(ch.poly.interiors[0].coords[0])
    # polygon_utils_cam.shapelyToCurve('test',ch.poly,0)
    # print(ch.poly.boundary)
    # print('shapely hierarchies')
    # print(len(returnpolys))

    return returnpolys


def meshFromCurveToChunk(object):
    mesh = object.data
    # print('detecting contours from curve')
    chunks = []
    chunk = camPathChunk([])
    ek = mesh.edge_keys
    d = {}
    for e in ek:
        d[e] = 1  #
    # d=dict(ek)
    dk = d.keys()
    x = object.location.x
    y = object.location.y
    z = object.location.z
    lastvi = 0
    vtotal = len(mesh.vertices)
    perc = 0
    for vi in range(0, len(mesh.vertices) - 1):
        co = (mesh.vertices[vi].co + object.location).to_tuple()
        if not dk.isdisjoint([(vi, vi + 1)]) and d[(vi, vi + 1)] == 1:
            chunk.points.append(co)
        else:
            chunk.points.append(co)
            if len(chunk.points) > 2 and (not (dk.isdisjoint([(vi, lastvi)])) or not (
            dk.isdisjoint([(lastvi, vi)]))):  # this was looping chunks of length of only 2 points...
                # print('itis')

                chunk.closed = True
                chunk.points.append((mesh.vertices[
                                         lastvi].co + object.location).to_tuple())  # add first point to end#originally the z was mesh.vertices[lastvi].co.z+z
            # chunk.append((mesh.vertices[lastvi].co.x+x,mesh.vertices[lastvi].co.y+y,mesh.vertices[lastvi].co.z+z))
            # else:
            # print('itisnot')
            lastvi = vi + 1
            chunks.append(chunk)
            chunk = camPathChunk([])

        if perc != int(100 * vi / vtotal):
            perc = int(100 * vi / vtotal)
            progress('processing curve', perc)

    vi = len(mesh.vertices) - 1
    chunk.points.append((mesh.vertices[vi].co.x + x, mesh.vertices[vi].co.y + y, mesh.vertices[vi].co.z + z))
    if not (dk.isdisjoint([(vi, lastvi)])) or not (dk.isdisjoint([(lastvi, vi)])):
        # print('itis')
        chunk.closed = True
        chunk.points.append(
            (mesh.vertices[lastvi].co.x + x, mesh.vertices[lastvi].co.y + y, mesh.vertices[lastvi].co.z + z))
    # else:
    #   print('itisnot')

    chunks.append(chunk)
    return chunks


def makeVisible(o):
    storage = [True, []]

    if not o.visible_get():
        storage[0] = False

    cam_collection = D.collections.new("cam")
    C.scene.collection.children.link(cam_collection)
    cam_collection.objects.link(C.object)

    for i in range(0, 20):
        storage[1].append(o.layers[i])

        o.layers[i] = bpy.context.scene.layers[i]

    return storage


def restoreVisibility(o, storage):
    o.hide_viewport = storage[0]
    # print(storage)
    for i in range(0, 20):
        o.layers[i] = storage[1][i]


def meshFromCurve(o, use_modifiers=False):
    # print(o.name,o)
    # storage = makeVisible(o)   # this is here because all of this doesn't work when object is not visible or on current layer
    activate(o)
    bpy.ops.object.duplicate()
    # bpy.ops.group.objects_remove_all()

    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    co = bpy.context.active_object

    if co.type == 'FONT':  # support for text objects is only and only here, just convert them to curves.
        bpy.ops.object.convert(target='CURVE', keep_original=False)
    co.data.dimensions = '3D'
    co.data.bevel_depth = 0
    co.data.extrude = 0

    # first, convert to mesh to avoid parenting issues with hooks, then apply locrotscale.
    bpy.ops.object.convert(target='MESH', keep_original=False)

    if use_modifiers:
        newmesh = co.to_mesh(bpy.context.depsgraph, True, calc_undeformed=False)
        oldmesh = co.data
        co.modifiers.clear()
        co.data = newmesh
        bpy.data.meshes.remove(oldmesh)

    try:
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    except:
        pass

    # restoreVisibility(o, storage)
    return bpy.context.active_object


def curveToChunks(o, use_modifiers=False):
    co = meshFromCurve(o, use_modifiers)
    # if co.type!='MESH':
    #	return []
    chunks = meshFromCurveToChunk(co)

    co = bpy.context.active_object

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[co.name].select_set(True)
    bpy.ops.object.delete()

    return chunks


def shapelyToChunks(p, zlevel):  #
    chunks = []
    # p=sortContours(p)
    seq = polygon_utils_cam.shapelyToCoords(p)
    i = 0
    for s in seq:
        # progress(p[i])
        if len(s) > 1:
            chunk = camPathChunk([])
            if len(s) == 2:
                sgeometry.LineString(s)
            else:
                chunk.poly = spolygon.Polygon(
                    s)  # this should maybe be LineString? but for sorting, we need polygon inside functions.
            for v in s:
                # progress (v)
                # print(v)
                if p.has_z:
                    chunk.points.append((v[0], v[1], v[2]))
                else:
                    chunk.points.append((v[0], v[1], zlevel))

            # chunk.points.append((chunk.points[0][0],chunk.points[0][1],chunk.points[0][2]))#last point =first point
            if chunk.points[0] == chunk.points[-1] and len(s) > 2:
                chunk.closed = True
            chunks.append(chunk)
        i += 1
    chunks.reverse()  # this is for smaller shapes first.
    #
    return chunks


def chunkToShapely(chunk):
    # pverts=[]

    # for v in chunk.points:

    #	pverts.append((v[0],v[1]))

    p = spolygon.Polygon(chunk.points)
    return p


def chunksRefine(chunks, o):
    '''add extra points in between for chunks'''
    for ch in chunks:
        # print('before',len(ch))
        newchunk = []
        v2 = Vector(ch.points[0])
        # print(ch.points)
        for s in ch.points:

            v1 = Vector(s)
            # print(v1,v2)
            v = v1 - v2

            # print(v.length,o.dist_along_paths)
            if v.length > o.dist_along_paths:
                d = v.length
                v.normalize()
                i = 0
                vref = Vector((0, 0, 0))

                while vref.length < d:
                    i += 1
                    vref = v * o.dist_along_paths * i
                    if vref.length < d:
                        p = v2 + vref

                        newchunk.append((p.x, p.y, p.z))

            newchunk.append(s)
            v2 = v1
        # print('after',len(newchunk))
        ch.points = newchunk

    return chunks


def chunksRefineThreshold(chunks, distance, limitdistance):
    '''add extra points in between for chunks. For medial axis strategy only !'''
    for ch in chunks:
        # print('before',len(ch))
        newchunk = []
        v2 = Vector(ch.points[0])
        # print(ch.points)
        for s in ch.points:

            v1 = Vector(s)
            # print(v1,v2)
            v = v1 - v2

            # print(v.length,o.dist_along_paths)
            if v.length > limitdistance:
                d = v.length
                v.normalize()
                i = 1
                vref = Vector((0, 0, 0))
                vhalf = v * d / 2
                while vref.length < d / 2:

                    vref = v * distance * i
                    if vref.length < d:
                        p = v2 + vref

                        newchunk.append((p.x, p.y, p.z))
                    i += 1
                    vref = v * distance * i  # because of the condition, so it doesn't run again.
                while i > 0:
                    vref = v * distance * i
                    if vref.length < d:
                        p = v1 - vref

                        newchunk.append((p.x, p.y, p.z))
                    i -= 1
                    vref = v * distance * i

            newchunk.append(s)
            v2 = v1
        # print('after',len(newchunk))
        ch.points = newchunk

    return chunks
