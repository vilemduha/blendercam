# blender CAM utils.py (c) 2012 Vilem Novak
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

# here is the main functionality of Blender CAM. The functions here are called with operators defined in ops.py.

import bpy
import mathutils
import math
import time
from bpy.props import *
from cam import utils
import numpy as np

from cam import simple
from cam import image_utils
def createSimulationObject(name, operations, i):
    oname = 'csim_' + name

    o = operations[0]

    if oname in bpy.data.objects:
        ob = bpy.data.objects[oname]
    else:
        bpy.ops.mesh.primitive_plane_add(align='WORLD', enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
        ob = bpy.context.active_object
        ob.name = oname

        bpy.ops.object.modifier_add(type='SUBSURF')
        ss = ob.modifiers[-1]
        ss.subdivision_type = 'SIMPLE'
        ss.levels = 6
        ss.render_levels = 6
        bpy.ops.object.modifier_add(type='SUBSURF')
        ss = ob.modifiers[-1]
        ss.subdivision_type = 'SIMPLE'
        ss.levels = 4
        ss.render_levels = 3
        bpy.ops.object.modifier_add(type='DISPLACE')

    ob.location = ((o.max.x + o.min.x) / 2, (o.max.y + o.min.y) / 2, o.min.z)
    ob.scale.x = (o.max.x - o.min.x) / 2
    ob.scale.y = (o.max.y - o.min.y) / 2
    print(o.max.x, o.min.x)
    print(o.max.y, o.min.y)
    print('bounds')
    disp = ob.modifiers[-1]
    disp.direction = 'Z'
    disp.texture_coords = 'LOCAL'
    disp.mid_level = 0

    if oname in bpy.data.textures:
        t = bpy.data.textures[oname]

        t.type = 'IMAGE'
        disp.texture = t

        t.image = i
    else:
        bpy.ops.texture.new()
        for t in bpy.data.textures:
            if t.name == 'Texture':
                t.type = 'IMAGE'
                t.name = oname
                t = t.type_recast()
                t.type = 'IMAGE'
                t.image = i
                disp.texture = t
    ob.hide_render = True
    bpy.ops.object.shade_smooth()


def doSimulation(name, operations):
    """perform simulation of operations. Currently only for 3 axis"""
    for o in operations:
        utils.getOperationSources(o)
    limits = utils.getBoundsMultiple(
        operations)  # this is here because some background computed operations still didn't have bounds data
    i = generateSimulationImage(operations, limits)
#    cp = simple.getCachePath(operations[0])[:-len(operations[0].name)] + name
    cp = simple.getSimulationPath()+name
    print('cp=',cp)
    iname = cp + '_sim.exr'


    image_utils.numpysave(i, iname)
    i = bpy.data.images.load(iname)
    createSimulationObject(name, operations, i)

def generateSimulationImage(operations, limits):
    minx, miny, minz, maxx, maxy, maxz = limits
    # print(minx,miny,minz,maxx,maxy,maxz)
    sx = maxx - minx
    sy = maxy - miny
    t = time.time()
    o = operations[0]  # getting sim detail and others from first op.
    simulation_detail = o.simulation_detail
    borderwidth = o.borderwidth
    resx = math.ceil(sx / simulation_detail) + 2 * borderwidth
    resy = math.ceil(sy / simulation_detail) + 2 * borderwidth
    # resx=ceil(sx/o.pixsize)+2*o.borderwidth
    # resy=ceil(sy/o.pixsize)+2*o.borderwidth
    # create array in which simulation happens, similar to an image to be painted in.
    si = np.array((0.1), dtype=float)
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
                simple.progress('simulation', perc)
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

def getCutterArray(operation, pixsize):
    type = operation.cutter_type
    # print('generating cutter')
    r = operation.cutter_diameter / 2 + operation.skin  # /operation.pixsize
    res = math.ceil((r * 2) / pixsize)
    # if res%2==0:#compensation for half-pixels issue, which wasn't an issue, so commented out
    # res+=1
    # m=res/2
    m = res / 2.0
    car = np.array((0), dtype=float)
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
                    z = math.sin(math.acos(v.length / r)) * r - r
                    car.itemset((a, b), z)  # [a,b]=z

    elif type == 'VCARVE':
        angle = operation.cutter_tip_angle
        s = math.tan(math.pi * (90 - angle / 2) / 180)  # angle in degrees
        #s = math.tan((math.pi - angle) / 2)  # angle in radians
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    z = (-v.length * s)
                    car.itemset((a, b), z)
    elif type == 'CYLCONE':
        angle = operation.cutter_tip_angle
        cyl_r = operation.cylcone_diameter/2
        s = math.tan(math.pi * (90 - angle / 2) / 180)  # angle in degrees
        #s = math.tan((math.pi - angle) / 2)  # angle in radians
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= r:
                    z = (-(v.length - cyl_r) * s)
                    if v.length <= cyl_r:
                        z =0
                    car.itemset((a, b), z)
    elif type == 'BALLCONE':
        angle =math.radians(operation.cutter_tip_angle)/2
        ball_r = operation.ball_radius
        cutter_r = operation.cutter_diameter / 2
        conedepth = (cutter_r - ball_r)/math.tan(angle)
        Ball_R = ball_r/math.cos(angle)
        D_ofset = ball_r * math.tan(angle)
        s = math.tan(math.pi/2-angle)
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps
            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps
                if v.length <= cutter_r:
                    z = -(v.length - ball_r ) * s -Ball_R + D_ofset
                    if v.length <= ball_r:
                      z = math.sin(math.acos(v.length / Ball_R)) * Ball_R - Ball_R
                    car.itemset((a, b), z)
    elif type == 'CUSTOM':
        cutob = bpy.data.objects[operation.cutter_object_name]
        scale = ((cutob.dimensions.x / cutob.scale.x) / 2) / r  #
        # print(cutob.scale)
        vstart = mathutils.Vector((0, 0, -10))
        vend = mathutils.Vector((0, 0, 10))
        print('sampling custom cutter')
        maxz = -1
        for a in range(0, res):
            vstart.x = (a + 0.5 - m) * ps * scale
            vend.x = vstart.x

            for b in range(0, res):
                vstart.y = (b + 0.5 - m) * ps * scale
                vend.y = vstart.y
                v = vend - vstart
                c = cutob.ray_cast(vstart, v, distance=1.70141e+38)
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


def simCutterSpot(xs, ys, z, cutterArray, si, getvolume=False):
    """simulates a cutter cutting into stock, taking away the volume, and optionally returning the volume that has been milled. This is now used for feedrate tweaking."""
    # xs=int(xs)
    # ys=int(ys)
    m = int(cutterArray.shape[0] / 2)
    size = cutterArray.shape[0]
    if xs > m and xs < si.shape[0] - m and ys > m and ys < si.shape[1] - m:  # whole cutter in image there
        if getvolume:
            volarray = si[xs - m:xs - m + size, ys - m:ys - m + size].copy()
        si[xs - m:xs - m + size, ys - m:ys - m + size] = np.minimum(si[xs - m:xs - m + size, ys - m:ys - m + size],
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
        si[startx:endx, starty:endy] = np.minimum(si[startx:endx, starty:endy],
                                                     cutterArray[castartx:caendx, castarty:caendy] + z)
        if getvolume:
            volarray = si[startx:endx, starty:endy] - volarray
            vsum = abs(volarray.sum())
            # print(vsum)
            return vsum

    return 0
