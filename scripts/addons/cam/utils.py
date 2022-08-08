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
import time
import mathutils
import math
from math import *
from mathutils import *
from bpy.props import *
from bpy_extras import object_utils

import sys
import numpy
import pickle

from cam.chunk import *
from cam.collision import *
from cam.simple import *
from cam.pattern import *
from cam.polygon_utils_cam import *
from cam.image_utils import *

from cam.opencamlib.opencamlib import oclSample, oclSamplePoints, oclResampleChunks, oclGetWaterline

from shapely.geometry import polygon as spolygon
from shapely.geometry import MultiPolygon
from shapely import ops as sops
from shapely import geometry as sgeometry

# from shapely.geometry import * not possible until Polygon libs gets out finally..
SHAPELY = True


def positionObject(operation):
    ob = bpy.data.objects[operation.object_name]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    minx, miny, minz, maxx, maxy, maxz = getBoundsWorldspace([ob], operation.use_modifiers)
    totx = maxx - minx
    toty = maxy - miny
    totz = maxz - minz
    if operation.material_center_x:
        ob.location.x -= minx + totx / 2
    else:
        ob.location.x -= minx

    if operation.material_center_y:
        ob.location.y -= miny + toty / 2
    else:
        ob.location.y -= miny

    if operation.material_Z == 'BELOW':
        ob.location.z -= maxz
    elif operation.material_Z == 'ABOVE':
        ob.location.z -= minz
    elif operation.material_Z == 'CENTERED':
        ob.location.z -= minz + totz / 2

    if ob.type != 'CURVE':
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    # addMaterialAreaObject()


def getBoundsWorldspace(obs, use_modifiers=False):
    # progress('getting bounds of object(s)')
    t = time.time()

    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    for ob in obs:
        # bb=ob.bound_box
        mw = ob.matrix_world
        if ob.type == 'MESH':
            if use_modifiers:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                mesh_owner = ob.evaluated_get(depsgraph)
                mesh = mesh_owner.to_mesh()
            else:
                mesh = ob.data

            for c in mesh.vertices:
                coord = c.co
                worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                minx = min(minx, worldCoord.x)
                miny = min(miny, worldCoord.y)
                minz = min(minz, worldCoord.z)
                maxx = max(maxx, worldCoord.x)
                maxy = max(maxy, worldCoord.y)
                maxz = max(maxz, worldCoord.z)

            if use_modifiers:
                mesh_owner.to_mesh_clear()

        elif ob.type == "FONT":
            activate(ob)
            bpy.ops.object.duplicate()
            co = bpy.context.active_object
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.ops.object.convert(target='MESH', keep_original=False)
            mesh = co.data
            for c in mesh.vertices:
                coord = c.co
                worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                minx = min(minx, worldCoord.x)
                miny = min(miny, worldCoord.y)
                minz = min(minz, worldCoord.z)
                maxx = max(maxx, worldCoord.x)
                maxy = max(maxy, worldCoord.y)
                maxz = max(maxz, worldCoord.z)
            bpy.ops.object.delete()
            bpy.ops.outliner.orphans_purge()
        else:

            # for coord in bb:
            for c in ob.data.splines:
                for p in c.bezier_points:
                    coord = p.co
                    # this can work badly with some imported curves, don't know why...
                    # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
                    worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                    minx = min(minx, worldCoord.x)
                    miny = min(miny, worldCoord.y)
                    minz = min(minz, worldCoord.z)
                    maxx = max(maxx, worldCoord.x)
                    maxy = max(maxy, worldCoord.y)
                    maxz = max(maxz, worldCoord.z)
                for p in c.points:
                    coord = p.co
                    # this can work badly with some imported curves, don't know why...
                    # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
                    worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                    minx = min(minx, worldCoord.x)
                    miny = min(miny, worldCoord.y)
                    minz = min(minz, worldCoord.z)
                    maxx = max(maxx, worldCoord.x)
                    maxy = max(maxy, worldCoord.y)
                    maxz = max(maxz, worldCoord.z)
    # progress(time.time()-t)
    return minx, miny, minz, maxx, maxy, maxz


def getSplineBounds(ob, curve):
    # progress('getting bounds of object(s)')
    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    mw = ob.matrix_world

    for p in curve.bezier_points:
        coord = p.co
        # this can work badly with some imported curves, don't know why...
        # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
        worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
        minx = min(minx, worldCoord.x)
        miny = min(miny, worldCoord.y)
        minz = min(minz, worldCoord.z)
        maxx = max(maxx, worldCoord.x)
        maxy = max(maxy, worldCoord.y)
        maxz = max(maxz, worldCoord.z)
    for p in curve.points:
        coord = p.co
        # this can work badly with some imported curves, don't know why...
        # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
        worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
        minx = min(minx, worldCoord.x)
        miny = min(miny, worldCoord.y)
        minz = min(minz, worldCoord.z)
        maxx = max(maxx, worldCoord.x)
        maxy = max(maxy, worldCoord.y)
        maxz = max(maxz, worldCoord.z)
    # progress(time.time()-t)
    return minx, miny, minz, maxx, maxy, maxz


def getOperationSources(o):
    if o.geometry_source == 'OBJECT':
        # bpy.ops.object.select_all(action='DESELECT')
        ob = bpy.data.objects[o.object_name]
        o.objects = [ob]
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if o.enable_B or o.enable_A:
            if o.old_rotation_A != o.rotation_A or o.old_rotation_B != o.rotation_B:
                o.old_rotation_A = o.rotation_A
                o.old_rotation_B = o.rotation_B
                ob = bpy.data.objects[o.object_name]
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
                if o.A_along_x:  # A parallel with X
                    if o.enable_A:
                        bpy.context.active_object.rotation_euler.x = o.rotation_A
                    if o.enable_B:
                        bpy.context.active_object.rotation_euler.y = o.rotation_B
                else:  # A parallel with Y
                    if o.enable_A:
                        bpy.context.active_object.rotation_euler.y = o.rotation_A
                    if o.enable_B:
                        bpy.context.active_object.rotation_euler.x = o.rotation_B

    elif o.geometry_source == 'COLLECTION':
        collection = bpy.data.collections[o.collection_name]
        o.objects = collection.objects
    elif o.geometry_source == 'IMAGE':
        o.use_exact = False

    if o.geometry_source == 'OBJECT' or o.geometry_source == 'COLLECTION':
        o.onlycurves = True
        for ob in o.objects:
            if ob.type == 'MESH':
                o.onlycurves = False
    else:
        o.onlycurves = False


def getBounds(o):
    # print('kolikrat sem rpijde')
    if o.geometry_source == 'OBJECT' or o.geometry_source == 'COLLECTION' or o.geometry_source == 'CURVE':
        print("valid geometry")
        minx, miny, minz, maxx, maxy, maxz = getBoundsWorldspace(o.objects, o.use_modifiers)

        if o.minz_from_ob:
            if minz == 10000000:
                minz = 0
            print("minz from object:" + str(minz))
            o.min.z = minz
            o.minz = o.min.z
        else:
            o.min.z = o.minz  # max(bb[0][2]+l.z,o.minz)#
            print("not minz from object")

        if o.material_from_model:
            print("material_from_model")

            o.min.x = minx - o.material_radius_around_model
            o.min.y = miny - o.material_radius_around_model
            o.max.z = max(o.maxz, maxz)

            o.max.x = maxx + o.material_radius_around_model
            o.max.y = maxy + o.material_radius_around_model
        else:
            print("not material from model")
            o.min.x = o.material_origin.x
            o.min.y = o.material_origin.y
            o.min.z = o.material_origin.z - o.material_size.z
            o.max.x = o.min.x + o.material_size.x
            o.max.y = o.min.y + o.material_size.y
            o.max.z = o.material_origin.z

    else:
        i = bpy.data.images[o.source_image_name]
        if o.source_image_crop:
            sx = int(i.size[0] * o.source_image_crop_start_x / 100)
            ex = int(i.size[0] * o.source_image_crop_end_x / 100)
            sy = int(i.size[1] * o.source_image_crop_start_y / 100)
            ey = int(i.size[1] * o.source_image_crop_end_y / 100)
        else:
            sx = 0
            ex = i.size[0]
            sy = 0
            ey = i.size[1]

        o.pixsize = o.source_image_size_x / i.size[0]

        o.min.x = o.source_image_offset.x + sx * o.pixsize
        o.max.x = o.source_image_offset.x + ex * o.pixsize
        o.min.y = o.source_image_offset.y + sy * o.pixsize
        o.max.y = o.source_image_offset.y + ey * o.pixsize
        o.min.z = o.source_image_offset.z + o.minz
        o.max.z = o.source_image_offset.z
    s = bpy.context.scene
    m = s.cam_machine
    if o.max.x - o.min.x > m.working_area.x or o.max.y - o.min.y > m.working_area.y \
            or o.max.z - o.min.z > m.working_area.z:
        o.warnings += 'Operation exceeds your machine limits\n'


def getBoundsMultiple(operations):
    """gets bounds of multiple operations, mainly for purpose of simulations or rest milling. highly suboptimal."""
    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    for o in operations:
        getBounds(o)
        maxx = max(maxx, o.max.x)
        maxy = max(maxy, o.max.y)
        maxz = max(maxz, o.max.z)
        minx = min(minx, o.min.x)
        miny = min(miny, o.min.y)
        minz = min(minz, o.min.z)

    return minx, miny, minz, maxx, maxy, maxz


def samplePathLow(o, ch1, ch2, dosample):
    v1 = Vector(ch1.points[-1])
    v2 = Vector(ch2.points[0])

    v = v2 - v1
    d = v.length
    v.normalize()

    vref = Vector((0, 0, 0))
    bpath = camPathChunk([])
    i = 0
    while vref.length < d:
        i += 1
        vref = v * o.dist_along_paths * i
        if vref.length < d:
            p = v1 + vref
            bpath.points.append([p.x, p.y, p.z])
    # print('between path')
    # print(len(bpath))
    pixsize = o.pixsize
    if dosample:
        if not (o.use_opencamlib and o.use_exact):
            if o.use_exact:
                if o.update_bullet_collision_tag:
                    prepareBulletCollision(o)
                    o.update_bullet_collision_tag = False

                cutterdepth = o.cutter_shape.dimensions.z / 2
                for p in bpath.points:
                    z = getSampleBullet(o.cutter_shape, p[0], p[1], cutterdepth, 1, o.minz)
                    if z > p[2]:
                        p[2] = z
            else:
                for p in bpath.points:
                    xs = (p[0] - o.min.x) / pixsize + o.borderwidth + pixsize / 2  # -m
                    ys = (p[1] - o.min.y) / pixsize + o.borderwidth + pixsize / 2  # -m
                    z = getSampleImage((xs, ys), o.offset_image, o.minz) + o.skin
                    if z > p[2]:
                        p[2] = z
    return bpath


# def threadedSampling():#not really possible at all without running more blenders for same operation :( python!
# samples in both modes now - image and bullet collision too.
def sampleChunks(o, pathSamples, layers):
    #
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z
    getAmbient(o)

    if o.use_exact:  # prepare collision world
        if o.use_opencamlib:
            oclSample(o, pathSamples)
            cutterdepth = 0
        else:
            if o.update_bullet_collision_tag:
                prepareBulletCollision(o)

                o.update_bullet_collision_tag = False
            # print (o.ambient)
            cutter = o.cutter_shape
            cutterdepth = cutter.dimensions.z / 2
    else:
        if o.strategy != 'WATERLINE':  # or prepare offset image, but not in some strategies.
            prepareArea(o)

        pixsize = o.pixsize

        coordoffset = o.borderwidth + pixsize / 2  # -m

        res = ceil(o.cutter_diameter / o.pixsize)
        m = res / 2

    t = time.time()
    # print('sampling paths')

    totlen = 0  # total length of all chunks, to estimate sampling time.
    for ch in pathSamples:
        totlen += len(ch.points)
    layerchunks = []
    minz = o.minz - 0.000001  # correction for image method problems
    layeractivechunks = []
    lastrunchunks = []

    for l in layers:
        layerchunks.append([])
        layeractivechunks.append(camPathChunk([]))
        lastrunchunks.append([])

    zinvert = 0
    if o.inverse:
        ob = bpy.data.objects[o.object_name]
        zinvert = ob.location.z + maxz  # ob.bound_box[6][2]

    n = 0
    last_percent = -1
    # timing for optimisation
    samplingtime = timinginit()
    sortingtime = timinginit()
    totaltime = timinginit()
    timingstart(totaltime)
    lastz = minz
    for patternchunk in pathSamples:
        thisrunchunks = []
        for l in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None
        # threads_count=4

        # for t in range(0,threads):

        for s in patternchunk.points:
            if o.strategy != 'WATERLINE' and int(100 * n / totlen) != last_percent:
                last_percent = int(100 * n / totlen)
                progress('sampling paths ', last_percent)
            n += 1
            x = s[0]
            y = s[1]
            if not o.ambient.contains(sgeometry.Point(x, y)):
                newsample = (x, y, 1)
            else:
                if o.use_opencamlib and o.use_exact:
                    z = s[2]
                    if minz > z:
                        z = minz
                    newsample = (x, y, z)
                # ampling
                elif o.use_exact and not o.use_opencamlib:

                    if lastsample is not None:  # this is an optimalization,
                        # search only for near depths to the last sample. Saves about 30% of sampling time.
                        z = getSampleBullet(cutter, x, y, cutterdepth, 1,
                                            lastsample[2] - o.dist_along_paths)  # first try to the last sample
                        if z < minz - 1:
                            z = getSampleBullet(cutter, x, y, cutterdepth, lastsample[2] - o.dist_along_paths, minz)
                    else:
                        z = getSampleBullet(cutter, x, y, cutterdepth, 1, minz)

                # print(z)
                else:
                    timingstart(samplingtime)
                    xs = (x - minx) / pixsize + coordoffset
                    ys = (y - miny) / pixsize + coordoffset
                    timingadd(samplingtime)
                    z = getSampleImage((xs, ys), o.offset_image, minz) + o.skin

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
                    if lastlayer is not None and lastlayer != currentlayer:  # and lastsample[2]!=newsample[2]:
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
                        # print(r)
                        li = 0
                        for ls in r:
                            splitz = layers[ls][1]
                            # print(ls)

                            v1 = lastsample
                            v2 = newsample
                            if o.protect_vertical:
                                v1, v2 = isVerticalLimit(v1, v2, o.protect_vertical_limit)
                            v1 = Vector(v1)
                            v2 = Vector(v2)
                            # print(v1,v2)
                            ratio = (splitz - v1.z) / (v2.z - v1.z)
                            # print(ratio)
                            betweensample = v1 + (v2 - v1) * ratio

                            # ch.points.append(betweensample.to_tuple())

                            if growing:
                                if li > 0:
                                    layeractivechunks[ls].points.insert(-1, betweensample.to_tuple())
                                else:
                                    layeractivechunks[ls].points.append(betweensample.to_tuple())
                                layeractivechunks[ls + 1].points.append(betweensample.to_tuple())
                            else:
                                # print(v1,v2,betweensample,lastlayer,currentlayer)
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
                        layerchunks[i].append(ch)
                        thisrunchunks[i].append(ch)
                        layeractivechunks[i] = camPathChunk([])
            lastsample = newsample

        for i, l in enumerate(layers):
            ch = layeractivechunks[i]
            if len(ch.points) > 0:
                layerchunks[i].append(ch)
                thisrunchunks[i].append(ch)
                layeractivechunks[i] = camPathChunk([])

            # PARENTING
            if o.strategy == 'PARALLEL' or o.strategy == 'CROSS' or o.strategy == 'OUTLINEFILL':
                timingstart(sortingtime)
                parentChildDist(thisrunchunks[i], lastrunchunks[i], o)
                timingadd(sortingtime)

        lastrunchunks = thisrunchunks

    # print(len(layerchunks[i]))
    progress('checking relations between paths')
    timingstart(sortingtime)

    if o.strategy == 'PARALLEL' or o.strategy == 'CROSS' or o.strategy == 'OUTLINEFILL':
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

                parentChild(parents, children, o)  # parent only last and first chunk, before it did this for all.
    timingadd(sortingtime)
    chunks = []

    for i, l in enumerate(layers):
        if o.ramp:
            for ch in layerchunks[i]:
                ch.zstart = layers[i][0]
                ch.zend = layers[i][1]
        chunks.extend(layerchunks[i])
    timingadd(totaltime)
    print(samplingtime)
    print(sortingtime)
    print(totaltime)
    return chunks


def sampleChunksNAxis(o, pathSamples, layers):
    #
    minx, miny, minz, maxx, maxy, maxz = o.min.x, o.min.y, o.min.z, o.max.x, o.max.y, o.max.z

    # prepare collision world
    if o.update_bullet_collision_tag:
        prepareBulletCollision(o)
        # print('getting ambient')
        getAmbient(o)
        o.update_bullet_collision_tag = False
    # print (o.ambient)
    cutter = o.cutter_shape
    cutterdepth = cutter.dimensions.z / 2

    t = time.time()
    print('sampling paths')

    totlen = 0  # total length of all chunks, to estimate sampling time.
    for chs in pathSamples:
        totlen += len(chs.startpoints)
    layerchunks = []
    minz = o.minz
    layeractivechunks = []
    lastrunchunks = []

    for l in layers:
        layerchunks.append([])
        layeractivechunks.append(camPathChunk([]))
        lastrunchunks.append([])
    n = 0

    lastz = minz
    for patternchunk in pathSamples:
        # print (patternchunk.endpoints)
        thisrunchunks = []
        for l in layers:
            thisrunchunks.append([])
        lastlayer = None
        currentlayer = None
        lastsample = None
        # threads_count=4
        lastrotation = (0, 0, 0)
        # for t in range(0,threads):
        # print(len(patternchunk.startpoints),len( patternchunk.endpoints))
        spl = len(patternchunk.startpoints)
        for si in range(0, spl):  # ,startp in enumerate(patternchunk.startpoints):
            # #TODO: seems we are writing into the source chunk ,
            #  and that is why we need to write endpoints everywhere too?

            if n / 200.0 == int(n / 200.0):
                progress('sampling paths ', int(100 * n / totlen))
            n += 1
            sampled = False
            # print(si)

            # get the vector to sample
            startp = Vector(patternchunk.startpoints[si])
            endp = Vector(patternchunk.endpoints[si])
            rotation = patternchunk.rotations[si]
            sweepvect = endp - startp
            sweepvect.normalize()
            # sampling
            if rotation != lastrotation:

                cutter.rotation_euler = rotation
                # cutter.rotation_euler.x=-cutter.rotation_euler.x
                # print(rotation)

                if o.cutter_type == 'VCARVE':  # Bullet cone is always pointing Up Z in the object
                    cutter.rotation_euler.x += pi
                cutter.update_tag()
                bpy.context.scene.frame_set(1)  # this has to be :( it resets the rigidbody world.
                # No other way to update it probably now :(
                bpy.context.scene.frame_set(2)  # actually 2 frame jumps are needed.
                bpy.context.scene.frame_set(0)

            newsample = getSampleBulletNAxis(cutter, startp, endp, rotation, cutterdepth)

            # print('totok',startp,endp,rotation,newsample)
            ################################
            # handling samples
            ############################################
            if newsample is not None:  # this is weird, but will leave it this way now.. just prototyping here.
                sampled = True
            else:  # TODO: why was this here?
                newsample = startp
                sampled = True
            # print(newsample)

            # elif o.ambient_behaviour=='ALL' and not o.inverse:#handle ambient here
            # newsample=(x,y,minz)
            if sampled:
                for i, l in enumerate(layers):
                    terminatechunk = False
                    ch = layeractivechunks[i]

                    # print(i,l)
                    # print(l[1],l[0])
                    v = startp - newsample
                    distance = -v.length

                    if l[1] <= distance <= l[0]:
                        lastlayer = currentlayer
                        currentlayer = i

                        if lastsample is not None and lastlayer is not None and currentlayer is not None \
                                and lastlayer != currentlayer:  # sampling for sorted paths in layers-
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
                            # print(r)
                            li = 0

                            for ls in r:
                                splitdistance = layers[ls][1]

                                ratio = (splitdistance - lastdistance) / (distance - lastdistance)
                                # print(ratio)
                                betweensample = lastsample + (newsample - lastsample) * ratio
                                # this probably doesn't work at all!!!! check this algoritm>
                                betweenrotation = tuple_add(lastrotation,
                                                            tuple_mul(tuple_sub(rotation, lastrotation), ratio))
                                # startpoint = retract point, it has to be always available...
                                betweenstartpoint = laststartpoint + (startp - laststartpoint) * ratio
                                # here, we need to have also possible endpoints always..
                                betweenendpoint = lastendpoint + (endp - lastendpoint) * ratio
                                if growing:
                                    if li > 0:
                                        layeractivechunks[ls].points.insert(-1, betweensample)
                                        layeractivechunks[ls].rotations.insert(-1, betweenrotation)
                                        layeractivechunks[ls].startpoints.insert(-1, betweenstartpoint)
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

                                # layeractivechunks[ls+1].points.insert(0,betweensample)
                                li += 1
                        # this chunk is terminated, and allready in layerchunks /

                        # ch.points.append(betweensample)#
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

        for i, l in enumerate(layers):
            ch = layeractivechunks[i]
            if len(ch.points) > 0:
                layerchunks[i].append(ch)
                thisrunchunks[i].append(ch)
                layeractivechunks[i] = camPathChunk([])

            if o.strategy == 'PARALLEL' or o.strategy == 'CROSS' or o.strategy == 'OUTLINEFILL':
                parentChildDist(thisrunchunks[i], lastrunchunks[i], o)

        lastrunchunks = thisrunchunks

    # print(len(layerchunks[i]))

    progress('checking relations between paths')
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


def extendChunks5axis(chunks, o):
    s = bpy.context.scene
    m = s.cam_machine
    s = bpy.context.scene
    free_movement_height = o.free_movement_height  # o.max.z +
    if m.use_position_definitions:  # dhull
        cutterstart = Vector((m.starting_position.x, m.starting_position.y,
                              max(o.max.z, m.starting_position.z)))  # start point for casting
    else:
        cutterstart = Vector((0, 0, max(o.max.z, free_movement_height)))  # start point for casting
    cutterend = Vector((0, 0, o.min.z))
    oriname = o.name + ' orientation'
    ori = s.objects[oriname]
    # rotationaxes = rotTo2axes(ori.rotation_euler,'CA')#warning-here it allready is reset to 0!!
    print('rot', o.rotationaxes)
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
                (a, b, 0))  # TODO: this is a placeholder. It does 99.9% probably write total nonsense.


def curveToShapely(cob, use_modifiers=False):
    chunks = curveToChunks(cob, use_modifiers)
    polys = chunksToShapely(chunks)
    return polys


# separate function in blender, so you can offset any curve.
# FIXME: same algorithms as the cutout strategy, because that is hierarchy-respecting.

def silhoueteOffset(context, offset, style=1, mitrelimit=1.0):
    bpy.context.scene.cursor.location = (0, 0, 0)
    ob = bpy.context.active_object
    if ob.type == 'CURVE' or ob.type == 'FONT':
        silhs = curveToShapely(ob)
    else:
        silhs = getObjectSilhouete('OBJECTS', [ob])

    polys = []
    mp = shapely.ops.unary_union(silhs)
    print("offset attributes:")
    print(offset, style)
    mp = mp.buffer(offset, cap_style=1, join_style=style, resolution=16, mitre_limit=mitrelimit)
    shapelyToCurve(ob.name + '_offset_' + str(round(offset, 5)), mp, ob.location.z)

    return {'FINISHED'}


def polygonBoolean(context, boolean_type):
    bpy.context.scene.cursor.location = (0, 0, 0)
    ob = bpy.context.active_object
    obs = []
    for ob1 in bpy.context.selected_objects:
        if ob1 != ob:
            obs.append(ob1)
    plist = curveToShapely(ob)
    p1 = MultiPolygon(plist)
    polys = []
    for o in obs:
        plist = curveToShapely(o)
        p2 = MultiPolygon(plist)
        polys.append(p2)
    # print(polys)
    if boolean_type == 'UNION':
        for p2 in polys:
            p1 = p1.union(p2)
    elif boolean_type == 'DIFFERENCE':
        for p2 in polys:
            p1 = p1.difference(p2)
    elif boolean_type == 'INTERSECT':
        for p2 in polys:
            p1 = p1.intersection(p2)

    shapelyToCurve('boolean', p1, ob.location.z)
    # bpy.ops.object.convert(target='CURVE')
    # bpy.context.scene.cursor_location=ob.location
    # bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    return {'FINISHED'}


def polygonConvexHull(context):
    coords = []

    bpy.ops.object.duplicate()
    bpy.ops.object.join()
    bpy.context.object.data.dimensions = '3D'  #  force curve to be a 3D curve
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.name = "_tmp"

    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.view_layer.objects.active

    for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
        c = (v.co.x, v.co.y)
        coords.append(c)

    simple.select_multiple('_tmp')  # delete temporary mesh
    simple.select_multiple('ConvexHull')  # delete old hull

    points = sgeometry.MultiPoint(coords)  # convert coordinates to shapely MultiPoint datastructure

    hull = points.convex_hull
    shapelyToCurve('ConvexHull', hull, 0.0)

    return {'FINISHED'}


def Helix(r, np, zstart, pend, rev):
    c = []
    pi = math.pi
    v = mathutils.Vector((r, 0, zstart))
    e = mathutils.Euler((0, 0, 2.0 * pi / np))
    zstep = (zstart - pend[2]) / (np * rev)
    for a in range(0, int(np * rev)):
        c.append((v.x + pend[0], v.y + pend[1], zstart - (a * zstep)))
        v.rotate(e)
    c.append((v.x + pend[0], v.y + pend[1], pend[2]))

    return c


def comparezlevel(x):
    return x[5]


def overlaps(bb1, bb2):  # true if bb1 is child of bb2
    ch1 = bb1
    ch2 = bb2
    if (ch2[1] > ch1[1] > ch1[0] > ch2[0] and ch2[3] > ch1[3] > ch1[2] > ch2[2]):
        return True


def connectChunksLow(chunks, o):
    """ connects chunks that are close to each other without lifting, sampling them 'low' """
    if not o.stay_low or (o.strategy == 'CARVE' and o.carve_depth > 0):
        return chunks

    connectedchunks = []
    chunks_to_resample = []  # for OpenCAMLib sampling
    mergedist = 3 * o.dist_between_paths
    if o.strategy == 'PENCIL':  # this is bigger for pencil path since it goes on the surface to clean up the rests,
        # and can go to close points on the surface without fear of going deep into material.
        mergedist = 10 * o.dist_between_paths

    if o.strategy == 'MEDIAL_AXIS':
        mergedist = 1 * o.medial_axis_subdivision

    if o.parallel_step_back:
        mergedist *= 2

    if o.merge_dist > 0:
        mergedist = o.merge_dist
    # mergedist=10
    lastch = None
    i = len(chunks)
    pos = (0, 0, 0)

    for ch in chunks:
        if len(ch.points) > 0:
            if lastch is not None and (ch.distStart(pos, o) < mergedist):
                # CARVE should lift allways, when it goes below surface...
                # print(mergedist,ch.dist(pos,o))
                if o.strategy == 'PARALLEL' or o.strategy == 'CROSS' or o.strategy == 'PENCIL':
                    # for these paths sorting happens after sampling, thats why they need resample the connection
                    between = samplePathLow(o, lastch, ch, True)
                else:
                    # print('addbetwee')
                    between = samplePathLow(o, lastch, ch,
                                            False)  # other paths either dont use sampling or are sorted before it.
                if o.use_opencamlib and o.use_exact and (
                        o.strategy == 'PARALLEL' or o.strategy == 'CROSS' or o.strategy == 'PENCIL'):
                    chunks_to_resample.append(
                        (connectedchunks[-1], len(connectedchunks[-1].points), len(between.points)))

                connectedchunks[-1].points.extend(between.points)
                connectedchunks[-1].points.extend(ch.points)
            else:
                connectedchunks.append(ch)
            lastch = ch
            pos = lastch.points[-1]

    if o.use_opencamlib and o.use_exact and o.strategy != 'CUTOUT' and o.strategy != 'POCKET':
        oclResampleChunks(o, chunks_to_resample)

    return connectedchunks


def getClosest(o, pos, chunks):
    # ch=-1
    mind = 2000
    d = 100000000000
    ch = None
    for chtest in chunks:
        cango = True
        for child in chtest.children:  # here was chtest.getNext==chtest, was doing recursion error and slowing down.
            if not child.sorted:
                cango = False
                break
        if cango:
            d = chtest.dist(pos, o)
            if d < mind:
                ch = chtest
                mind = d
    return ch


def sortChunks(chunks, o):
    if o.strategy != 'WATERLINE':
        progress('sorting paths')
    sys.setrecursionlimit(100000)  # the getNext() function of CamPathChunk was running out of recursion limits.
    sortedchunks = []
    chunks_to_resample = []

    lastch = None
    i = len(chunks)
    pos = (0, 0, 0)
    # for ch in chunks:
    # ch.getNext()#this stores the unsortedchildren properties
    # print('numofchunks')
    # print(len(chunks))
    while len(chunks) > 0:
        ch = None
        if len(sortedchunks) == 0 or len(
                lastch.parents) == 0:  # first chunk or when there are no parents -> parents come after children here...
            ch = getClosest(o, pos, chunks)
        elif len(lastch.parents) > 0:  # looks in parents for next candidate, recursively
            for parent in lastch.parents:
                ch = parent.getNextClosest(o, pos)
                if ch is not None:
                    break
            if ch is None:
                ch = getClosest(o, pos, chunks)

        if ch is not None:  # found next chunk, append it to list
            # only adaptdist the chunk if it has not been sorted before
            if not ch.sorted:
                ch.adaptdist(pos, o)
                ch.sorted = True
            # print(len(ch.parents),'children')
            chunks.remove(ch)
            sortedchunks.append(ch)
            lastch = ch
            pos = lastch.points[-1]
        # print(i, len(chunks))
        # experimental fix for infinite loop problem
        # else:
        # THIS PROBLEM WASN'T HERE AT ALL. but keeping it here, it might fix the problems somwhere else:)
        # can't find chunks close enough and still some chunks left
        # to be sorted. For now just move the remaining chunks over to
        # the sorted list.
        # This fixes an infinite loop condition that occurs sometimes.
        # This is a bandaid fix: need to find the root cause of this problem
        # suspect it has to do with the sorted flag?
        # print("no chunks found closest. Chunks not sorted: ", len(chunks))
        # sortedchunks.extend(chunks)
        # chunks[:] = []

        i -= 1

    sys.setrecursionlimit(1000)
    if o.strategy != 'DRILL' and o.strategy != 'OUTLINEFILL':
        # THIS SHOULD AVOID ACTUALLY MOST STRATEGIES, THIS SHOULD BE DONE MANUALLY,
        # BECAUSE SOME STRATEGIES GET SORTED TWICE.
        sortedchunks = connectChunksLow(sortedchunks, o)
    return sortedchunks


def getVectorRight(lastv, verts):  # most right vector from a set regarding angle..
    defa = 100
    v1 = Vector(lastv[0])
    v2 = Vector(lastv[1])
    va = v2 - v1
    for i, v in enumerate(verts):
        if v != lastv[0]:
            vb = Vector(v) - v2
            a = va.angle_signed(Vector(vb))

            if a < defa:
                defa = a
                returnvec = i
    return returnvec


def cleanUpDict(ndict):
    print('removing lonely points')  # now it should delete all junk first, iterate over lonely verts.
    # found_solitaires=True
    # while found_solitaires:
    found_solitaires = False
    keys = []
    keys.extend(ndict.keys())
    removed = 0
    for k in keys:
        print(k)
        print(ndict[k])
        if len(ndict[k]) <= 1:
            newcheck = [k]
            while (len(newcheck) > 0):
                v = newcheck.pop()
                if len(ndict[v]) <= 1:
                    for v1 in ndict[v]:
                        newcheck.append(v)
                    dictRemove(ndict, v)
            removed += 1
            found_solitaires = True
    print(removed)


def dictRemove(dict, val):
    for v in dict[val]:
        dict[v].remove(val)
    dict.pop(val)


def addLoop(parentloop, start, end):
    added = False
    for l in parentloop[2]:
        if l[0] < start and l[1] > end:
            addLoop(l, start, end)
            return
    parentloop[2].append([start, end, []])


def cutloops(csource, parentloop, loops):
    copy = csource[parentloop[0]:parentloop[1]]

    for li in range(len(parentloop[2]) - 1, -1, -1):
        l = parentloop[2][li]
        # print(l)
        copy = copy[:l[0] - parentloop[0]] + copy[l[1] - parentloop[0]:]
    loops.append(copy)
    for l in parentloop[2]:
        cutloops(csource, l, loops)


def getOperationSilhouete(operation):
    """gets silhouete for the operation
        uses image thresholding for everything except curves.
    """
    if operation.update_silhouete_tag:
        image = None
        objects = None
        if operation.geometry_source == 'OBJECT' or operation.geometry_source == 'COLLECTION':
            if not operation.onlycurves:
                stype = 'OBJECTS'
            else:
                stype = 'CURVES'
        else:
            stype = 'IMAGE'

        totfaces = 0
        if stype == 'OBJECTS':
            for ob in operation.objects:
                if ob.type == 'MESH':
                    totfaces += len(ob.data.polygons)

        if (stype == 'OBJECTS' and totfaces > 200000) or stype == 'IMAGE':
            print('image method')
            samples = renderSampleImage(operation)
            if stype == 'OBJECTS':
                i = samples > operation.minz - 0.0000001
                # numpy.min(operation.zbuffer_image)-0.0000001#
                # #the small number solves issue with totally flat meshes, which people tend to mill instead of
                # proper pockets. then the minimum was also maximum, and it didn't detect contour.
            else:
                i = samples > numpy.min(operation.zbuffer_image)  # this fixes another numeric imprecision.

            chunks = imageToChunks(operation, i)
            operation.silhouete = chunksToShapely(chunks)
        # print(operation.silhouete)
        # this conversion happens because we need the silh to be oriented, for milling directions.
        else:
            print('object method for retrieving silhouette')  #
            operation.silhouete = getObjectSilhouete(stype, objects=operation.objects,
                                                     use_modifiers=operation.use_modifiers)

        operation.update_silhouete_tag = False
    return operation.silhouete


def getObjectSilhouete(stype, objects=None, use_modifiers=False):
    # o=operation
    if stype == 'CURVES':  # curve conversion to polygon format
        allchunks = []
        for ob in objects:
            chunks = curveToChunks(ob)
            allchunks.extend(chunks)
        silhouete = chunksToShapely(allchunks)

    elif stype == 'OBJECTS':
        totfaces = 0
        for ob in objects:
            totfaces += len(ob.data.polygons)

        if totfaces < 20000000:  # boolean polygons method originaly was 20 000 poly limit, now limitless,
            # it might become teribly slow, but who cares?
            t = time.time()
            print('shapely getting silhouette')
            polys = []
            for ob in objects:
                if use_modifiers:
                    ob = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
                    m = ob.to_mesh()
                else:
                    m = ob.data
                mw = ob.matrix_world
                mwi = mw.inverted()
                r = ob.rotation_euler
                m.calc_loop_triangles()
                id = 0
                e = 0.000001
                scaleup = 100
                for tri in m.loop_triangles:
                    n = tri.normal.copy()
                    n.rotate(r)

                    if tri.area > 0 and n.z != 0:  # n.z>0.0 and f.area>0.0 :
                        s = []
                        c = mw @ tri.center
                        c = c.xy
                        for vert_index in tri.vertices:
                            v = mw @ m.vertices[vert_index].co
                            s.append((v.x, v.y))
                        if len(s) > 2:
                            # print(s)
                            p = spolygon.Polygon(s)
                            # print(dir(p))
                            if p.is_valid:
                                # polys.append(p)
                                polys.append(p.buffer(e, resolution=0))
                        id += 1

            if totfaces < 20000:
                p = sops.unary_union(polys)
            else:
                print('computing in parts')
                bigshapes = []
                i = 1
                part = 20000
                while i * part < totfaces:
                    print(i)
                    ar = polys[(i - 1) * part:i * part]
                    bigshapes.append(sops.unary_union(ar))
                    i += 1
                if (i - 1) * part < totfaces:
                    last_ar = polys[(i - 1) * part:]
                    bigshapes.append(sops.unary_union(last_ar))
                print('joining')
                p = sops.unary_union(bigshapes)

            print(time.time() - t)

            t = time.time()
            silhouete = [p]  # [polygon_utils_cam.Shapely2Polygon(p)]

    return silhouete


def getAmbient(o):
    if o.update_ambient_tag:
        if o.ambient_cutter_restrict:  # cutter stays in ambient & limit curve
            m = o.cutter_diameter / 2
        else:
            m = 0

        if o.ambient_behaviour == 'AROUND':
            r = o.ambient_radius - m
            o.ambient = getObjectOutline(r, o, True)  # in this method we need ambient from silhouete
        else:
            o.ambient = spolygon.Polygon(((o.min.x + m, o.min.y + m), (o.min.x + m, o.max.y - m),
                                          (o.max.x - m, o.max.y - m), (o.max.x - m, o.min.y + m)))

        if o.use_limit_curve:
            if o.limit_curve != '':
                limit_curve = bpy.data.objects[o.limit_curve]
                polys = curveToShapely(limit_curve)
                o.limit_poly = shapely.ops.unary_union(polys)

                if o.ambient_cutter_restrict:
                    o.limit_poly = o.limit_poly.buffer(o.cutter_diameter / 2, resolution=o.circle_detail)
            o.ambient = o.ambient.intersection(o.limit_poly)
    o.update_ambient_tag = False


def getObjectOutline(radius, o, Offset):  # FIXME: make this one operation independent
    # circle detail, optimize, optimize thresold.

    polygons = getOperationSilhouete(o)

    i = 0
    # print('offseting polygons')

    if Offset:
        offset = 1
    else:
        offset = -1

    outlines = []
    i = 0
    if o.straight:
        join = 2
    else:
        join = 1

    if isinstance(polygons, list):
        polygon_list = polygons
    else:
        polygon_list = polygons.geoms

    for p1 in polygon_list:  # sort by size before this???
        # print(p1.type, len(polygons))
        i += 1
        if radius > 0:
            p1 = p1.buffer(radius * offset, resolution=o.circle_detail, join_style=join, mitre_limit=2)
        outlines.append(p1)

    # print(outlines)
    if o.dont_merge:
        outline = sgeometry.MultiPolygon(outlines)
    else:
        outline = shapely.ops.unary_union(outlines)
    return outline


def addOrientationObject(o):
    """the orientation object should be used to set up orientations of the object for 4 and 5 axis milling."""
    name = o.name + ' orientation'
    s = bpy.context.scene
    if s.objects.find(name) == -1:
        bpy.ops.object.empty_add(type='ARROWS', align='WORLD', location=(0, 0, 0))

        ob = bpy.context.active_object
        ob.empty_draw_size = 0.05
        ob.show_name = True
        ob.name = name
    ob = s.objects[name]
    if o.machine_axes == '4':

        if o.rotary_axis_1 == 'X':
            ob.lock_rotation = [False, True, True]
            ob.rotation_euler[1] = 0
            ob.rotation_euler[2] = 0
        if o.rotary_axis_1 == 'Y':
            ob.lock_rotation = [True, False, True]
            ob.rotation_euler[0] = 0
            ob.rotation_euler[2] = 0
        if o.rotary_axis_1 == 'Z':
            ob.lock_rotation = [True, True, False]
            ob.rotation_euler[0] = 0
            ob.rotation_euler[1] = 0
    elif o.machine_axes == '5':
        ob.lock_rotation = [False, False, True]

        ob.rotation_euler[2] = 0  # this will be a bit hard to rotate.....


# def addCutterOrientationObject(o):


def removeOrientationObject(o):  # not working
    name = o.name + ' orientation'
    if bpy.context.scene.objects.find(name) > -1:
        ob = bpy.context.scene.objects[name]
        delob(ob)


def addTranspMat(ob, mname, color, alpha):
    if mname in bpy.data.materials:
        mat = bpy.data.materials[mname]
    else:
        mat = bpy.data.materials.new(name=mname)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]

        # Assign it to object
        if ob.data.materials:
            ob.data.materials[0] = mat
        else:
            ob.data.materials.append(mat)


def addMachineAreaObject():
    s = bpy.context.scene
    ao = bpy.context.active_object
    if s.objects.get('CAM_machine') is not None:
        o = s.objects['CAM_machine']
    else:
        oldunits = s.unit_settings.system
        # need to be in metric units when adding machine mesh object
        # in order for location to work properly
        s.unit_settings.system = 'METRIC'
        bpy.ops.mesh.primitive_cube_add(align='WORLD', enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
        o = bpy.context.active_object
        o.name = 'CAM_machine'
        o.data.name = 'CAM_machine'
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        # o.type = 'SOLID'
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.subdivide(number_cuts=32, smoothness=0, quadcorner='STRAIGHT_CUT', fractal=0,
                               fractal_along_normal=0, seed=0)
        bpy.ops.mesh.select_nth(nth=2, offset=0)
        bpy.ops.mesh.delete(type='EDGE')
        bpy.ops.mesh.primitive_cube_add(align='WORLD', enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))

        bpy.ops.object.editmode_toggle()
        # addTranspMat(o, "violet_transparent", (0.800000, 0.530886, 0.725165), 0.1)
        o.display_type = 'BOUNDS'
        o.hide_render = True
        o.hide_select = True
        # o.select = False
        s.unit_settings.system = oldunits

    # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    o.dimensions = bpy.context.scene.cam_machine.working_area
    if ao is not None:
        ao.select_set(True)
    # else:
    #     bpy.context.scene.objects.active = None


def addMaterialAreaObject():
    s = bpy.context.scene
    operation = s.cam_operations[s.cam_active_operation]
    getOperationSources(operation)
    getBounds(operation)

    ao = bpy.context.active_object
    if s.objects.get('CAM_material') is not None:
        o = s.objects['CAM_material']
    else:
        bpy.ops.mesh.primitive_cube_add(align='WORLD', enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
        o = bpy.context.active_object
        o.name = 'CAM_material'
        o.data.name = 'CAM_material'
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        # addTranspMat(o, 'blue_transparent', (0.458695, 0.794658, 0.8), 0.1)
        o.display_type = 'BOUNDS'
        o.hide_render = True
        o.hide_select = True
        o.select_set(state=True, view_layer=None)
    # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    o.dimensions = bpy.context.scene.cam_machine.working_area

    o.dimensions = (
        operation.max.x - operation.min.x, operation.max.y - operation.min.y, operation.max.z - operation.min.z)
    o.location = (operation.min.x, operation.min.y, operation.max.z)
    if ao is not None:
        ao.select_set(True)
    # else:
    #     bpy.context.scene.objects.active = None


def getContainer():
    s = bpy.context.scene
    if s.objects.get('CAM_OBJECTS') is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD')
        container = bpy.context.active_object
        container.name = 'CAM_OBJECTS'
        container.location = [0, 0, 0]
        container.hide = True
    else:
        container = s.objects['CAM_OBJECTS']

    return container


# progress('finished')

# tools for voroni graphs all copied from the delaunayVoronoi addon:
class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def unique(L):
    """Return a list of unhashable elements in s, but without duplicates.
    [[1, 2], [2, 3], [1, 2]] >>> [[1, 2], [2, 3]]"""
    # For unhashable objects, you can sort the sequence and then scan from the end of the list,
    # deleting duplicates as you go
    nDupli = 0
    nZcolinear = 0
    L.sort()  # sort() brings the equal elements together; then duplicates are easy to weed out in a single pass.
    last = L[-1]
    for i in range(len(L) - 2, -1, -1):
        if last[:2] == L[i][:2]:  # XY coordinates compararison
            if last[2] == L[i][2]:  # Z coordinates compararison
                nDupli += 1  # duplicates vertices
            else:  # Z colinear
                nZcolinear += 1
            del L[i]
        else:
            last = L[i]
    return (nDupli,
            nZcolinear)  # list data type is mutable,
    # input list will automatically update and doesn't need to be returned


def checkEqual(lst):
    return lst[1:] == lst[:-1]


def prepareIndexed(o):
    s = bpy.context.scene
    # first store objects positions/rotations
    o.matrices = []
    o.parents = []
    for ob in o.objects:
        o.matrices.append(ob.matrix_world.copy())
        o.parents.append(ob.parent)

    # then rotate them
    for ob in o.objects:
        ob.select = True
    s.objects.active = ob
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    s.cursor.location = (0, 0, 0)
    oriname = o.name + ' orientation'
    ori = s.objects[oriname]
    o.orientation_matrix = ori.matrix_world.copy()
    o.rotationaxes = rotTo2axes(ori.rotation_euler, 'CA')
    ori.select = True
    s.objects.active = ori
    # we parent all objects to the orientation object
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    for ob in o.objects:
        ob.select = False
    # then we move the orientation object to 0,0
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    ori.select = False
    for ob in o.objects:
        activate(ob)

        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    # rot=ori.matrix_world.inverted()
    # #rot.x=-rot.x
    # #rot.y=-rot.y
    # #rot.z=-rot.z
    # rotationaxes = rotTo2axes(ori.rotation_euler,'CA')
    #
    # #bpy.context.space_data.pivot_point = 'CURSOR'
    # #bpy.context.space_data.pivot_point = 'CURSOR'
    #
    # for ob in o.objects:
    #     ob.rotation_euler.rotate(rot)


def cleanupIndexed(operation):
    s = bpy.context.scene
    oriname = operation.name + 'orientation'

    ori = s.objects[oriname]
    path = s.objects["cam_path_{}{}".format(operation.name)]

    ori.matrix_world = operation.orientation_matrix
    # set correct path location
    path.location = ori.location
    path.rotation_euler = ori.rotation_euler

    print(ori.matrix_world, operation.orientation_matrix)
    for i, ob in enumerate(operation.objects):  # TODO: fix this here wrong order can cause objects out of place
        ob.parent = operation.parents[i]
    for i, ob in enumerate(operation.objects):
        ob.matrix_world = operation.matrices[i]


def rotTo2axes(e, axescombination):
    """converts an orientation object rotation to rotation defined by 2 rotational axes on the machine -
    for indexed machining.
    attempting to do this for all axes combinations.
    """
    v = Vector((0, 0, 1))
    v.rotate(e)
    # if axes
    if axescombination == 'CA':
        v2d = Vector((v.x, v.y))
        a1base = Vector((0, -1))  # ?is this right?It should be vector defining 0 rotation
        if v2d.length > 0:
            cangle = a1base.angle_signed(v2d)
        else:
            return (0, 0)
        v2d = Vector((v2d.length, v.z))
        a2base = Vector((0, 1))
        aangle = a2base.angle_signed(v2d)
        print('angles', cangle, aangle)
        return (cangle, aangle)

    elif axescombination == 'CB':
        v2d = Vector((v.x, v.y))
        a1base = Vector((1, 0))  # ?is this right?It should be vector defining 0 rotation
        if v2d.length > 0:
            cangle = a1base.angle_signed(v2d)
        else:
            return (0, 0)
        v2d = Vector((v2d.length, v.z))
        a2base = Vector((0, 1))

        bangle = a2base.angle_signed(v2d)

        print('angles', cangle, bangle)

        return (cangle, bangle)

    # v2d=((v[a[0]],v[a[1]]))
    # angle1=a1base.angle(v2d)#C for ca
    # print(angle1)
    # if axescombination[0]=='C':
    #     e1=Vector((0,0,-angle1))
    # elif axescombination[0]=='A':#TODO: finish this after prototyping stage
    #     pass;
    # v.rotate(e1)
    # vbase=Vector(0,1,0)
    # bangle=v.angle(vzbase)
    # print(v)
    # print(bangle)

    return (angle1, angle2)


def reload_pathss(o):
    oname = "cam_path_" + o.name
    s = bpy.context.scene
    # for o in s.objects:
    ob = None
    old_pathmesh = None
    if oname in s.objects:
        old_pathmesh = s.objects[oname].data
        ob = s.objects[oname]

    picklepath = getCachePath(o) + '.pickle'
    f = open(picklepath, 'rb')
    d = pickle.load(f)
    f.close()

    # passed=False
    # while not passed:
    #     try:
    #         f=open(picklepath,'rb')
    #         d=pickle.load(f)
    #         f.close()
    #         passed=True
    #     except:
    #         print('sleep')
    #         time.sleep(1)

    o.warnings = d['warnings']
    o.duration = d['duration']
    verts = d['path']

    edges = []
    for a in range(0, len(verts) - 1):
        edges.append((a, a + 1))

    oname = "cam_path_" + o.name
    mesh = bpy.data.meshes.new(oname)
    mesh.name = oname
    mesh.from_pydata(verts, edges, [])

    if oname in s.objects:
        s.objects[oname].data = mesh
    else:
        object_utils.object_data_add(bpy.context, mesh, operator=None)
        ob = bpy.context.active_object
        ob.name = oname
    ob = s.objects[oname]
    ob.location = (0, 0, 0)
    o.path_object_name = oname
    o.changed = False

    if old_pathmesh is not None:
        bpy.data.meshes.remove(old_pathmesh)
