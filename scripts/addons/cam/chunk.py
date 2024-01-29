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
from shapely import geometry as sgeometry
from cam import polygon_utils_cam
from cam.simple import *
from cam.exception import CamException
from cam.numba_wrapper import jit,prange

import math
import numpy as np


def Rotate_pbyp(originp, p, ang):  # rotate point around another point with angle
    ox, oy, oz = originp
    px, py, oz = p

    if ang == abs(math.pi / 2):
        d = ang / abs(ang)
        qx = ox + d * (oy - py)
        qy = oy + d * (px - ox)
    else:
        qx = ox + math.cos(ang) * (px - ox) - math.sin(ang) * (py - oy)
        qy = oy + math.sin(ang) * (px - ox) + math.cos(ang) * (py - oy)
    rot_p = [qx, qy, oz]
    return rot_p

@jit(nopython=True,parallel=True,fastmath=True,cache=True)
def _internalXyDistanceTo(ourpoints,theirpoints,cutoff):
    v1=ourpoints[0]
    v2=theirpoints[0]
    minDistSq = (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2
    cutoffSq= cutoff**2
    for v1 in ourpoints:
        for v2 in theirpoints:
            distSq= (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2
            if distSq<cutoffSq:
                return sqrt(distSq)
            minDistSq=min(distSq,minDistSq)
    return sqrt(minDistSq)


# for building points - stores points as lists for easy insert /append behaviour
class camPathChunkBuilder:
    def __init__(self,inpoints=None, startpoints=None, endpoints=None, rotations=None):
        if inpoints is None:
            inpoints=[]
        self.points=inpoints
        self.startpoints=startpoints
        self.endpoints=endpoints
        self.rotations=rotations

    def to_chunk(self):
        chunk = camPathChunk(self.points,self.startpoints,self.endpoints,self.rotations)
        if len(self.points)>2 and np.array_equal(self.points[0],self.points[-1]):
            chunk.closed = True
        return chunk

# an actual chunk - stores points as numpy arrays
class camPathChunk:
    # parents=[]
    # children=[]
    # sorted=False

    # progressIndex=-1# for e.g. parallel strategy, when trying to save time..
    def __init__(self, inpoints, startpoints=None, endpoints=None, rotations=None):
        # name this as _points so nothing external accesses it directly
        self._points = np.array(inpoints)  # for 3 axes, this is only storage of points. For N axes, here go the sampled points
        self.poly = None # get polygon just in time 
        self.simppoly = None
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
        self.length = 0  # this is total length of this chunk.
        self.zstart = 0  # this is stored for ramps mainly,
        # because they are added afterwards, but have to use layer info
        self.zend = 0  #

    def update_poly(self):
        if len(self._points) > 2:
            self.poly = sgeometry.Polygon(self._points)
        else:
            self.poly = sgeometry.Polygon()


    def get_point(self,n):
        return self._points[n].tolist()


    def get_points(self):
        return self._points.tolist()

    def set_points(self,points):
        self._points=np.array(points)

    def count(self):
        return len(self._points)

    def copy(self):
        nchunk = camPathChunk(inpoints=self._points.copy(), startpoints=self.startpoints, endpoints=self.endpoints, rotations=self.rotations)
        nchunk.closed = self.closed
        nchunk.children = self.children
        nchunk.parents = self.parents
        nchunk.sorted = self.sorted
        nchunk.length = self.length
        return nchunk

    def shift(self, x, y, z):
        self._points = self._points + np.array([x,y,z])
        for i, p in enumerate(self.startpoints):
            self.startpoints[i] = (p[0] + x, p[1] + y, p[2] + z)
        for i, p in enumerate(self.endpoints):
            self.endpoints[i] = (p[0] + x, p[1] + y, p[2] + z)

    def setZ(self, z,if_bigger=False):
        if if_bigger:
            self._points[:,2]=z if z>self._points[:,2] else self._points[:,2]
        else:
            self._points[:,2]=z
            

    def offsetZ(self, z):
        self._points[:,2]+=z

    def flipX(self, x_centre):
        self._points[:,0]= x_centre - self._points[:,0]


    def isbelowZ(self, z):
        return np.any(self._points[:,2]<z)

    def clampZ(self, z):
        np.clip(self._points[:,2],z,None,self._points[:,2])

    def clampmaxZ(self, z):
        np.clip(self._points[:,2],None,z,self._points[:,2])

    def dist(self, pos, o):
        if self.closed:
            dist_sq = (pos[0]-self._points[:,0])**2 + (pos[1]-self._points[:,1])**2
            return sqrt(np.min(dist_sq))
        else:
            if o.movement.type == 'MEANDER':
                d1 = dist2d(pos, self._points[0])
                d2 = dist2d(pos, self._points[-1])
                # if d2<d1:
                #   ch.points.reverse()
                return min(d1, d2)
            else:
                return dist2d(pos, self._points[0])

    def distStart(self, pos, o):
        return dist2d(pos, self._points[0])


    # if cutoff is set, then the first distance < cutoff is returned
    def xyDistanceTo(self,other,cutoff=0):
        if self.poly is None:
            self.update_poly()
        if other.poly is None:
            other.update_poly()
        if not self.poly.is_empty and not other.poly.is_empty:
            # both polygons have >2 points
            # simplify them if they aren't already, to speed up distance finding
            if self.simppoly is None:
                self.simppoly=self.poly.simplify(0.0003).boundary
            if other.simppoly is None:
                other.simppoly=other.poly.simplify(0.0003).boundary
            return self.simppoly.distance(other.simppoly)
        else:  # this is the old method, preferably should be replaced in most cases except parallel
            # where this method works probably faster.
            # print('warning, sorting will be slow due to bad parenting in parentChildDist')
            return _internalXyDistanceTo(self._points,other._points,cutoff)

    def adaptdist(self, pos, o):
        # reorders chunk so that it starts at the closest point to pos.
        if self.closed:
            dist_sq = (pos[0]-self._points[:,0])**2 + (pos[1]-self._points[:,1])**2
            point_idx = np.argmin(dist_sq)
            new_points = np.concatenate((self._points[point_idx:],self._points[:point_idx+1]))
            self._points=new_points
        else:
            if o.movement.type == 'MEANDER':
                d1 = dist2d(pos, self._points[0])
                d2 = dist2d(pos, self._points[-1])
                if d2 < d1:
                    self.points=np.flip(self._points,axis=0)

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
            if not chtest.sorted:
                self.cango = False
                cango = True

                for child in chtest.children:
                    if not child.sorted:
                        if child not in tested:
                            testlist.append(child)
                            tested.append(child)
                        cango = False

                if cango:
                    d = chtest.dist(pos, o)
                    if d < mind:
                        ch = chtest
                        mind = d
        if ch is not None:
            # print('found some')
            return ch
        # print('returning none')
        return None

    def getLength(self):
        # computes length of the chunk - in 3d

        point_differences=self._points[0:-1,:] - self._points[1:,:]
        distances=np.linalg.norm(point_differences,axis=1)
        self.length = np.sum(distances)

    def reverse(self):
        self._points=np.flip(self._points,axis=0)
        self.startpoints.reverse()
        self.endpoints.reverse()
        self.rotations.reverse()

    def pop(self, index):
        print("WARNING: Popping from chunk is slow",self,index)
        self._points=np.concatenate((self._points[0:index],self._points[index+1:]),axis=0)
        if len(self.startpoints) > 0:
            self.startpoints.pop(index)
            self.endpoints.pop(index)
            self.rotations.pop(index)

    def append(self, point, startpoint=None, endpoint=None, rotation=None,at_index=None):
        if at_index is None:
            self._points=np.concatenate((self._points,np.array([point])))
            if startpoint is not None:
                self.startpoints.append(startpoint)
            if endpoint is not None:
                self.endpoints.append(endpoint)
            if rotation is not None:
                self.rotations.append(rotation)
        else:
            self._points=np.concatenate((self._points[0:at_index],np.array([point]),self._points[at_index:]))
            if startpoint is not None:
                self.startpoints[at_index:at_index]=[startpoint]
            if endpoint is not None:
                self.endpoints[at_index:at_index]=[endpoint]
            if rotation is not None:
                self.rotations[at_index:at_index]=[rotation]

    def extend(self, points, startpoints=None, endpoints=None, rotations=None,at_index=None):
        if len(points)==0:
            return
        if at_index is None:
            self._points=np.concatenate((self._points,np.array(points)))
            if startpoints is not None:
                self.startpoints.extend(startpoints)
            if endpoints is not None:
                self.endpoints.extend(endpoints)
            if rotations is not None:
                self.rotations.extend(rotations)
        else:
            self._points=np.concatenate((self._points[0:at_index],np.array(points),self._points[at_index:]))
            if startpoints is not None:
                self.startpoints[at_index:at_index]=startpoints
            if endpoints is not None:
                self.endpoints[at_index:at_index]=endpoints
            if rotations is not None:
                self.rotations[at_index:at_index]=rotations

    def clip_points(self,minx,maxx,miny,maxy):
        """ remove any points outside this range """
        included_values= (self._points[:,0]>=minx) and ((self._points[:,0]<=maxx)
            and (self._points[:,1]>=maxy) and (self._points[:,1]<=maxy))
        self._points=self._points[included_values]


    def rampContour(self, zstart, zend, o):

        stepdown = zstart - zend
        chunk_points=[]
        estlength = (zstart - zend) / tan(o.movement.ramp_in_angle)
        self.getLength()
        ramplength = estlength  # min(ch.length,estlength)
        ltraveled = 0
        endpoint = None
        i = 0
        # z=zstart
        znew = 10
        rounds = 0  # for counting if ramping makes more layers
        while endpoint is None and not (znew == zend and i == 0):  #
            # for i,s in enumerate(ch.points):
            # print(i, znew, zend, len(ch.points))
            s = self._points[i]

            if i > 0:
                s2 = self._points[i - 1]
                ltraveled += dist2d(s, s2)
                ratio = ltraveled / ramplength
            elif rounds > 0 and i == 0:
                s2 = self._points[-1]
                ltraveled += dist2d(s, s2)
                ratio = ltraveled / ramplength
            else:
                ratio = 0
            znew = zstart - stepdown * ratio
            if znew <= zend:

                ratio = ((z - zend) / (z - znew))
                v1 = Vector(chunk_points[-1])
                v2 = Vector((s[0], s[1], znew))
                v = v1 + ratio * (v2 - v1)
                chunk_points.append((v.x, v.y, max(s[2], v.z)))

                if zend == o.min.z and endpoint is None and self.closed:
                    endpoint = i + 1
                    if endpoint == len(self._points):
                        endpoint = 0
            # print(endpoint,len(ch.points))
            # else:
            znew = max(znew, zend, s[2])
            chunk_points.append((s[0], s[1], znew))
            z = znew
            if endpoint is not None:
                break
            i += 1
            if i >= len(self._points):
                i = 0
                rounds += 1
        # if not o.use_layers:
        # endpoint=0
        if endpoint is not None:  # append final contour on the bottom z level
            i = endpoint
            started = False
            # print('finaliz')
            if i == len(self._points):
                i = 0
            while i != endpoint or not started:
                started = True
                s = self._points[i]
                chunk_points.append((s[0], s[1], s[2]))
                # print(i,endpoint)
                i += 1
                if i == len(self._points):
                    i = 0
        # ramp out
        if o.movement.ramp_out and (not o.use_layers or not o.first_down or (o.first_down and endpoint is not None)):
            z = zend
            # i=endpoint

            while z < o.maxz:
                if i == len(self._points):
                    i = 0
                s1 = self._points[i]
                i2 = i - 1
                if i2 < 0:
                    i2 = len(self._points) - 1
                s2 = self._points[i2]
                l = dist2d(s1, s2)
                znew = z + tan(o.movement.ramp_out_angle) * l
                if znew > o.maxz:
                    ratio = ((z - o.maxz) / (z - znew))
                    v1 = Vector(chunk_points[-1])
                    v2 = Vector((s1[0], s1[1], znew))
                    v = v1 + ratio * (v2 - v1)
                    chunk_points.append((v.x, v.y, v.z))

                else:
                    chunk_points.append((s1[0], s1[1], znew))
                z = znew
                i += 1

        # TODO: convert to numpy properly
        self._points = np.array(chunk_points)

    def rampZigZag(self, zstart, zend, o):
        # TODO: convert to numpy properly
        if zend==None:
            zend = self._points[0][2]
        chunk_points = []
        # print(zstart,zend)
        if zend < zstart:  # this check here is only for stupid setup,
            # when the chunks lie actually above operation start z.

            stepdown = zstart - zend

            estlength = (zstart - zend) / tan(o.movement.ramp_in_angle)
            self.getLength()
            if self.length > 0:  # for single point chunks..
                ramplength = estlength
                zigzaglength = ramplength / 2.000
                turns = 1
                print('turns %i' % turns)
                if zigzaglength > self.length:
                    turns = ceil(zigzaglength / self.length)
                    ramplength = turns * self.length * 2.0
                    zigzaglength = self.length
                    ramppoints = self._points.tolist()

                else:
                    zigzagtraveled = 0.0
                    haspoints = False
                    ramppoints = [(self._points[0][0], self._points[0][1], self._points[0][2])]
                    i = 1
                    while not haspoints:
                        # print(i,zigzaglength,zigzagtraveled)
                        p1 = ramppoints[-1]
                        p2 = self._points[i]
                        d = dist2d(p1, p2)
                        zigzagtraveled += d
                        if zigzagtraveled >= zigzaglength or i + 1 == len(self._points):
                            ratio = 1 - (zigzagtraveled - zigzaglength) / d
                            if (i + 1 == len(
                                    self._points)):  # this condition is for a rare case of combined layers+bridges+ramps..
                                ratio = 1
                            v = p1 + ratio * (p2 - p1)
                            ramppoints.append(v.tolist())
                            haspoints = True
                        else:
                            ramppoints.append(p2)
                        i += 1
                negramppoints = ramppoints.copy()
                negramppoints.reverse()
                ramppoints.extend(negramppoints[1:])

                traveled = 0.0
                chunk_points.append((self._points[0][0], self._points[0][1], max(self._points[0][2], zstart)))
                for r in range(turns):
                    for p in range(0, len(ramppoints)):
                        p1 = chunk_points[-1]
                        p2 = ramppoints[p]
                        d = dist2d(p1, p2)
                        traveled += d
                        ratio = traveled / ramplength
                        znew = zstart - stepdown * ratio
                        chunk_points.append((p2[0], p2[1], max(p2[2], znew)))  # max value here is so that it doesn't go
                        # below surface in the case of 3d paths

                # chunks = setChunksZ([ch],zend)
                chunk_points.extend(self._points.tolist())

            ######################################
            # ramp out - this is the same thing, just on the other side..
            if o.movement.ramp_out:
                zstart = o.maxz
                zend = self._points[-1][2]
                if zend < zstart:  # again, sometimes a chunk could theoretically end above the starting level.
                    stepdown = zstart - zend

                    estlength = (zstart - zend) / tan(o.movement.ramp_out_angle)
                    self.getLength()
                    if self.length > 0:
                        ramplength = estlength
                        zigzaglength = ramplength / 2.000
                        turns = 1
                        print('turns %i' % turns)
                        if zigzaglength > self.length:
                            turns = ceil(zigzaglength / self.length)
                            ramplength = turns * self.length * 2.0
                            zigzaglength = self.length
                            ramppoints = self._points.tolist()
                            ramppoints.reverse()  # revert points here, we go the other way.

                        else:
                            zigzagtraveled = 0.0
                            haspoints = False
                            ramppoints = [(self._points[-1][0], self._points[-1][1], self._points[-1][2])]
                            i = len(self._points) - 2
                            while not haspoints:
                                # print(i,zigzaglength,zigzagtraveled)
                                p1 = ramppoints[-1]
                                p2 = self._points[i]
                                d = dist2d(p1, p2)
                                zigzagtraveled += d
                                if zigzagtraveled >= zigzaglength or i + 1 == len(self._points):
                                    ratio = 1 - (zigzagtraveled - zigzaglength) / d
                                    if (i + 1 == len(
                                            self._points)):  # this condition is for a rare case of
                                        # combined layers+bridges+ramps...
                                        ratio = 1
                                    # print((ratio,zigzaglength))
                                    v = p1 + ratio * (p2 - p1)
                                    ramppoints.append(v.tolist())
                                    haspoints = True
                                # elif :

                                else:
                                    ramppoints.append(p2)
                                i -= 1
                        negramppoints = ramppoints.copy()
                        negramppoints.reverse()
                        ramppoints.extend(negramppoints[1:])

                        traveled = 0.0
                        for r in range(turns):
                            for p in range(0, len(ramppoints)):
                                p1 = chunk_points[-1]
                                p2 = ramppoints[p]
                                d = dist2d(p1, p2)
                                traveled += d
                                ratio = 1 - (traveled / ramplength)
                                znew = zstart - stepdown * ratio
                                chunk_points.append((p2[0], p2[1], max(p2[2], znew)))
                                # max value here is so that it doesn't go below surface in the case of 3d paths
        self._points = np.array(chunk_points)

    #  modify existing path start point
    def changePathStart(self, o):
        if o.profile_start > 0:
            newstart = o.profile_start
            chunkamt = len(self._points)
            newstart = newstart % chunkamt
            self._points=np.concatenate((self._points[newstart:],self._points[:newstart]))


    def breakPathForLeadinLeadout(self, o):
        iradius = o.lead_in
        oradius = o.lead_out
        if iradius + oradius > 0:
            chunkamt = len(self._points)

            for i in range(chunkamt - 1):
                apoint = self._points[i]
                bpoint = self._points[i + 1]
                bmax = bpoint[0] - apoint[0]
                bmay = bpoint[1] - apoint[1]
                segmentLength = math.hypot(bmax, bmay)  # find segment length

                if segmentLength > 2 * max(iradius,
                                           oradius):  # Be certain there is enough room for the leadin and leadiout
                    # add point on the line here
                    newpointx = (bpoint[0] + apoint[0]) / 2  # average of the two x points to find center
                    newpointy = (bpoint[1] + apoint[1]) / 2  # average of the two y points to find center
                    self._points=np.concatenate((self._points[:i+1],np.array([[newpointx, newpointy, apoint[2]]]),self._points[i+1:]))

    def leadContour(self, o):
        perimeterDirection = 1  # 1 is clockwise, 0 is CCW
        if o.movement.spindle_rotation == 'CW':
            if o.movement.type == 'CONVENTIONAL':
                perimeterDirection = 0

        if self.parents:  # if it is inside another parent
            perimeterDirection ^= 1  # toggle with a bitwise XOR
            print("has parent")

        if perimeterDirection == 1:
            print("path direction is Clockwise")
        else:
            print("path direction is counterclockwise")
        iradius = o.lead_in
        oradius = o.lead_out
        start = self._points[0]
        nextp = self._points[1]
        rpoint = Rotate_pbyp(start, nextp, math.pi / 2)
        dx = rpoint[0] - start[0]
        dy = rpoint[1] - start[1]
        la = math.hypot(dx, dy)
        pvx = (iradius * dx) / la + start[0]  # arc center(x)
        pvy = (iradius * dy) / la + start[1]  # arc center(y)
        arc_c = [pvx, pvy, start[2]]

        # TODO: this could easily be numpy
        chunk_points = []  # create a new cutting path

        # add lead in arc in the begining
        if round(o.lead_in, 6) > 0.0:
            for i in range(15):
                iangle = -i * (math.pi / 2) / 15
                arc_p = Rotate_pbyp(arc_c, start, iangle)
                chunk_points.insert(0, arc_p)

        # glue rest of the path to the arc
        chunk_points.extend(self._points.tolist())
        # for i in range(len(self._points)):
        #     chunk_points.append(self._points[i])

        # add lead out arc to the end
        if round(o.lead_in, 6) > 0.0:
            for i in range(15):
                iangle = i * (math.pi / 2) / 15
                arc_p = Rotate_pbyp(arc_c, start, iangle)
                chunk_points.append(arc_p)

        self._points = np.array(chunk_points)


def chunksCoherency(chunks):
    # checks chunks for their stability, for pencil path.
    # it checks if the vectors direction doesn't jump too much too quickly,
    # if this happens it splits the chunk on such places,
    # too much jumps = deletion of the chunk. this is because otherwise the router has to slow down too often,
    # but also means that some parts detected by cavity algorithm won't be milled
    nchunks = []
    for chunk in chunks:
        if len(chunk._points) > 2:
            nchunk = camPathChunkBuilder()

            # doesn't check for 1 point chunks here, they shouldn't get here at all.
            lastvec = Vector(chunk._points[1]) - Vector(chunk._points[0])
            for i in range(0, len(chunk._points) - 1):
                nchunk.points.append(chunk._points[i])
                vec = Vector(chunk._points[i + 1]) - Vector(chunk._points[i])
                angle = vec.angle(lastvec, vec)
                # print(angle,i)
                if angle > 1.07:  # 60 degrees is maximum toleration for pencil paths.
                    if len(nchunk_points) > 4:  # this is a testing threshold
                        nchunks.append(nchunk.to_chunk())
                    nchunk = camPathChunkBuilder()
                lastvec = vec
            if len(nchunk_points) > 4:  # this is a testing threshold
                nchunk._points=np.array(nchunk_points)
                nchunks.append(nchunk)
    return nchunks


def setChunksZ(chunks, z):
    newchunks = []
    for ch in chunks:
        chunk = ch.copy()
        chunk.setZ(z)
        newchunks.append(chunk)
    return newchunks

# don't make this @jit parallel, because it sometimes gets called with small N
# and the overhead of threading is too much.
@jit(nopython=True,fastmath=True)
def _optimize_internal(points,keep_points,e,protect_vertical,protect_vertical_limit):
    # inlined so that numba can optimize it nicely
    def _mag_sq(v1):
        return v1[0]**2 + v1[1]**2 + v1[2]**2

    def _dot_pr(v1,v2):
        return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

    def _applyVerticalLimit(v1, v2, cos_limit):
        """test path segment on verticality threshold, for protect_vertical option"""
        z = abs(v1[2] - v2[2])
        if z > 0:
            # don't use this vector because dot product of 0,0,1 is trivially just v2[2]
            #            vec_up = np.array([0, 0, 1])
            vec_diff= v1-v2
            vec_diff2 = v2-v1
            vec_diff_mag = np.sqrt(_mag_sq(vec_diff))
            # dot product = cos(angle) * mag1 * mag2
            cos1_times_mag = vec_diff[2]
            cos2_times_mag = vec_diff2[2]
            if cos1_times_mag > cos_limit*vec_diff_mag:
                # vertical, moving down
                v1[0] = v2[0]
                v1[1] = v2[1]
            elif cos2_times_mag > cos_limit*vec_diff_mag:
                # vertical, moving up
                v2[0] = v1[0]
                v2[1] = v1[1]

    cos_limit = cos( protect_vertical_limit )
    prev_i = 0
    for i in range(1,points.shape[0]-1):
        v1 = points[prev_i]
        v2=points[i+1]
        vmiddle=points[i]

        line_direction = v2-v1
        line_length = sqrt(_mag_sq(line_direction))
        if line_length==0:
            # don't keep duplicate points
            keep_points[i]=False
            continue
        # normalize line direction
        line_direction*= (1.0/line_length) # N in formula below
        # X = A + tN (line formula) Distance to point P
        # A = v1, N = line_direction, P = vmiddle
        # distance = || (P - A) - ((P-A).N)N ||
        point_offset = vmiddle - v1
        distance_sq = _mag_sq(point_offset - (line_direction * _dot_pr(point_offset,line_direction)))
        # compare on squared distance to save a sqrt
        if distance_sq < e*e:
            keep_points[i]=False
        else:
            keep_points[i]=True
            if protect_vertical:
                _applyVerticalLimit(points[prev_i], points[i], cos_limit)
            prev_i=i


def optimizeChunk(chunk, operation):
    if len(chunk._points) > 2:
        points = chunk._points
        naxispoints = False
        if len(chunk.startpoints) > 0:
            startpoints = chunk.startpoints
            endpoints = chunk.endpoints
            naxispoints = True

        protect_vertical = operation.movement.protect_vertical and operation.machine_axes == '3'
        keep_points=np.full(points.shape[0],True)
        # shape points need to be on line,
        # but we need to protect vertical - which
        # means changing point values
        # bits of this are moved from simple.py so that
        # numba can optimize as a whole
        _optimize_internal(points,keep_points,operation.optimisation.optimize_threshold * 0.000001,protect_vertical,operation.movement.protect_vertical_limit)

        # now do numpy select by boolean array
        chunk._points=points[keep_points]
        if naxispoints:
            # list comprehension so we don't have to do tons of appends
            chunk.startpoints=[chunk.startpoints[i] for i,b in enumerate(keep_points) if b==True]
            chunk.endpoints=[chunk.endpoints[i] for i,b in enumerate(keep_points) if b==True]
            chunk.rotations=[chunk.rotations[i] for i,b in enumerate(keep_points) if b==True]
    return chunk


def limitChunks(chunks, o,
                force=False):  # TODO: this should at least add point on area border...
    # but shouldn't be needed at all at the first place...
    if o.use_limit_curve or force:
        nchunks = []
        for ch in chunks:
            prevsampled = True
            nch = camPathChunkBuilder()
            nch1 = None
            closed = True
            for s in ch._points:
                sampled = o.ambient.contains(sgeometry.Point(s[0], s[1]))
                if not sampled and len(nch.points) > 0:
                    nch.closed = False
                    closed = False
                    nchunks.append(nch.to_chunk())
                    if nch1 is None:
                        nch1=nchunks[-1]
                    nch = camPathChunkBuilder()
                elif sampled:
                    nch.points.append(s)
                prevsampled = sampled
            if len(nch.points) > 2 and closed and ch.closed and np.array_equal(ch._points[0] ,ch._points[-1]):
                nch.closed = True
            elif ch.closed and nch1 is not None and len(nch.points) > 1 and np.array_equal(nch.points[-1], nch1._points[0]):
                # here adds beginning of closed chunk to the end, if the chunks were split during limiting
                nch.points.extend(nch1._points.tolist())
                nchunks.remove(nch1)
                print('joining stuff')
            if len(nch.points) > 0:
                nchunks.append(nch.to_chunk())
        return nchunks
    else:
        return chunks


def parentChildPoly(parents, children, o):
    # hierarchy based on polygons - a polygon inside another is his child.
    # hierarchy works like this: - children get milled first.

    for parent in parents:
        if parent.poly is None: 
            parent.update_poly()
        for child in children:
            if child.poly is None: 
                child.update_poly()
            if child != parent:  # and len(child.poly)>0
                if parent.poly.contains(sgeometry.Point(child.poly.boundary.coords[0])):
                    parent.children.append(child)
                    child.parents.append(parent)


def parentChildDist(parents, children, o, distance=None):
    # parenting based on x,y distance between chunks
    # hierarchy works like this: - children get milled first.

    if distance is None:
        dlim = o.dist_between_paths * 2
        if (o.strategy == 'PARALLEL' or o.strategy == 'CROSS') and o.movement.parallel_step_back:
            dlim = dlim * 2
    else:
        dlim = distance
    
    for child in children:
        for parent in parents:
            isrelation = False
            if parent != child:
                d = parent.xyDistanceTo(child,cutoff=dlim)
                if d< dlim:
                    isrelation = True
                if isrelation:
                    parent.children.append(child)
                    child.parents.append(parent)


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

    for ch in chunks:  # first convert chunk to poly
        if len(ch._points) > 2:
            # pchunk=[]
            ch.poly = sgeometry.Polygon(ch._points)

    for ppart in chunks:  # then add hierarchy relations
        for ptest in chunks:

            if ppart != ptest:
                if ptest.poly.contains(ppart.poly):
                    # hierarchy works like this: - children get milled first.
                    ppart.parents.append(ptest)

    for ch in chunks:  # now make only simple polygons with holes, not more polys inside others
        found = False
        if len(ch.parents) % 2 == 1:

            for parent in ch.parents:
                if len(parent.parents) + 1 == len(ch.parents):
                    ch.nparents = [parent]  # nparents serves as temporary storage for parents,
                    # not to get mixed with the first parenting during the check
                    found = True
                    break

        if not found:
            ch.nparents = []

    for ch in chunks:  # then subtract the 1st level holes
        ch.parents = ch.nparents
        ch.nparents = None
        if len(ch.parents) > 0:

            try:
                ch.parents[0].poly = ch.parents[0].poly.difference(
                    ch.poly)  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)
            except:

                print('chunksToShapely oops!')

                lastPt = False
                tolerance = 0.0000003
                newPoints = []

                for pt in ch._points:
                    toleranceXok = True
                    toleranceYok = True
                    if lastPt:
                        if abs(pt[0] - lastPt[0]) < tolerance:
                            toleranceXok = False
                        if abs(pt[1] - lastPt[1]) < tolerance:
                            toleranceYok = False

                        if toleranceXok or toleranceYok:
                            newPoints.append(pt)
                            lastPt = pt
                    else:
                        newPoints.append(pt)
                        lastPt = pt

                toleranceXok = True
                toleranceYok = True
                if abs(newPoints[0][0] - lastPt[0]) < tolerance:
                    toleranceXok = False
                if abs(newPoints[0][1] - lastPt[1]) < tolerance:
                    toleranceYok = False

                if not toleranceXok and not toleranceYok:
                    newPoints.pop()

                ch._points = np.array(newPoints)
                ch.poly = sgeometry.Polygon(ch._points)

                try:
                    ch.parents[0].poly = ch.parents[0].poly.difference(ch.poly)
                except:

                    # print('chunksToShapely double oops!')

                    lastPt = False
                    tolerance = 0.0000003
                    newPoints = []

                    for pt in ch.parents[0]._points:
                        toleranceXok = True
                        toleranceYok = True
                        # print( '{0:.9f}, {0:.9f}, {0:.9f}'.format(pt[0], pt[1], pt[2]) )
                        # print(pt)
                        if lastPt:
                            if abs(pt[0] - lastPt[0]) < tolerance:
                                toleranceXok = False
                            if abs(pt[1] - lastPt[1]) < tolerance:
                                toleranceYok = False

                            if toleranceXok or toleranceYok:
                                newPoints.append(pt)
                                lastPt = pt
                        else:
                            newPoints.append(pt)
                            lastPt = pt

                    toleranceXok = True
                    toleranceYok = True
                    if abs(newPoints[0][0] - lastPt[0]) < tolerance:
                        toleranceXok = False
                    if abs(newPoints[0][1] - lastPt[1]) < tolerance:
                        toleranceYok = False

                    if not toleranceXok and not toleranceYok:
                        newPoints.pop()
                    # print('starting and ending points too close, removing ending point')

                    ch.parents[0]._points = np.array(newPoints)
                    ch.parents[0].poly = sgeometry.Polygon(ch.parents[0]._points)

                    ch.parents[0].poly = ch.parents[0].poly.difference(
                        ch.poly)  # sgeometry.Polygon( ch.parents[0].poly, ch.poly)

    returnpolys = []

    for polyi in range(0, len(chunks)):  # export only the booleaned polygons
        ch = chunks[polyi]
        if len(ch.parents) == 0:
            returnpolys.append(ch.poly)
    from shapely.geometry import MultiPolygon
    polys = MultiPolygon(returnpolys)
    return polys


def meshFromCurveToChunk(object):
    mesh = object.data
    # print('detecting contours from curve')
    chunks = []
    chunk = camPathChunkBuilder()
    ek = mesh.edge_keys
    d = {}
    for e in ek:
        d[e] = 1  #
    dk = d.keys()
    x = object.location.x
    y = object.location.y
    z = object.location.z
    lastvi = 0
    vtotal = len(mesh.vertices)
    perc = 0
    progress('processing curve - START - Vertices: ' + str(vtotal))
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
                chunk.points.append((mesh.vertices[lastvi].co + object.location).to_tuple())
                # add first point to end#originally the z was mesh.vertices[lastvi].co.z+z
            lastvi = vi + 1
            chunks.append(chunk.to_chunk())
            chunk = camPathChunkBuilder()

    progress('processing curve - FINISHED')

    vi = len(mesh.vertices) - 1
    chunk.points.append((mesh.vertices[vi].co.x + x, mesh.vertices[vi].co.y + y, mesh.vertices[vi].co.z + z))
    if not (dk.isdisjoint([(vi, lastvi)])) or not (dk.isdisjoint([(lastvi, vi)])):
        chunk.closed = True
        chunk.points.append(
            (mesh.vertices[lastvi].co.x + x, mesh.vertices[lastvi].co.y + y, mesh.vertices[lastvi].co.z + z))
    chunks.append(chunk.to_chunk())
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
    activate(o)
    bpy.ops.object.duplicate()

    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    co = bpy.context.active_object

    if co.type == 'FONT':  # support for text objects is only and only here, just convert them to curves.
        bpy.ops.object.convert(target='CURVE', keep_original=False)
    elif co.type != 'CURVE': # curve must be a curve...
        bpy.ops.object.delete() # delete temporary object
        raise CamException("Source curve object must be of type CURVE")
    co.data.dimensions = '3D'
    co.data.bevel_depth = 0
    co.data.extrude = 0

    # first, convert to mesh to avoid parenting issues with hooks, then apply locrotscale.
    bpy.ops.object.convert(target='MESH', keep_original=False)

    if use_modifiers:
        eval_object = co.evaluated_get(bpy.context.evaluated_depsgraph_get())
        newmesh = bpy.data.meshes.new_from_object(eval_object)
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

    return bpy.context.active_object


def curveToChunks(o, use_modifiers=False):
    co = meshFromCurve(o, use_modifiers)
    chunks = meshFromCurveToChunk(co)

    co = bpy.context.active_object

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[co.name].select_set(True)
    bpy.ops.object.delete()

    return chunks


def shapelyToChunks(p, zlevel):  #
    chunk_builders = []
    # p=sortContours(p)
    seq = polygon_utils_cam.shapelyToCoords(p)
    i = 0
    for s in seq:
        # progress(p[i])
        if len(s) > 1:
            chunk = camPathChunkBuilder([])
            for v in s:
                if p.has_z:
                    chunk.points.append((v[0], v[1], v[2]))
                else:
                    chunk.points.append((v[0], v[1], zlevel))

            chunk_builders.append(chunk)
        i += 1
    chunk_builders.reverse()  # this is for smaller shapes first.
    return [c.to_chunk() for c in chunk_builders]


def chunkToShapely(chunk):
    p = spolygon.Polygon(chunk._points)
    return p


def chunksRefine(chunks, o):
    """add extra points in between for chunks"""
    for ch in chunks:
        # print('before',len(ch))
        newchunk = []
        v2 = Vector(ch._points[0])
        # print(ch.points)
        for s in ch._points:

            v1 = Vector(s)
            v = v1 - v2

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
        ch._points = np.array(newchunk)

    return chunks


def chunksRefineThreshold(chunks, distance, limitdistance):
    """add extra points in between for chunks. For medial axis strategy only !"""
    for ch in chunks:
        newchunk = []
        v2 = Vector(ch._points[0])

        for s in ch._points:

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
                    vref = v * distance * i  # because of the condition, so it doesn't run again.
                while i > 0:
                    vref = v * distance * i
                    if vref.length < d:
                        p = v1 - vref

                        newchunk.append((p.x, p.y, p.z))
                    i -= 1

            newchunk.append(s)
            v2 = v1
        ch._points = np.array(newchunk)

    return chunks
