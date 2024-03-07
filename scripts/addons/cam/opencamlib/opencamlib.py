# used by OpenCAMLib sampling

import bpy
try:
    import ocl
except ImportError:
    try:
        import opencamlib as ocl
    except ImportError:
        pass
import os
import tempfile
import numpy as np

from subprocess import call
from cam.collision import BULLET_SCALE
from cam import simple
from cam.chunk import camPathChunk
from cam.simple import *
from cam.async_op import progress_async
from shapely import geometry as sgeometry
from .oclSample import get_oclSTL
from cam import utils

from cam.opencamlib.oclSample import ocl_sample

OCL_SCALE = 1000.0

PYTHON_BIN = None

def pointSamplesFromOCL(points, samples):
    for index, point in enumerate(points):
        point[2] = samples[index].z / OCL_SCALE

def chunkPointSamplesFromOCL(chunks, samples):
    s_index = 0
    for ch in chunks:
        ch_points=ch.count()
        z_vals=np.array([p.z for p in samples[s_index:s_index+ch_points]])
        z_vals /= OCL_SCALE
        ch.setZ(z_vals)
        s_index+=ch_points
        # p_index = 0
        # for point in ch.points:
        #     if len(point) == 2 or point[2] != 2:
        #         z_sample = samples[s_index].z / OCL_SCALE
        #         ch.points[p_index] = (point[0], point[1], z_sample)
        #     # print(str(point[2]))
        #     else:
        #         ch.points[p_index] = (point[0], point[1], 1)
        #     p_index += 1
        #     s_index += 1

def chunkPointsResampleFromOCL(chunks, samples):
    s_index = 0
    for ch in chunks:
        ch_points=ch.count()
        z_vals=np.array([p.z for p in samples[s_index:s_index+ch_points]])
        z_vals /= OCL_SCALE
        ch.setZ(z_vals)
        s_index+=ch_points

    # s_index = 0
    # for ch in chunks:
    #     p_index = 0
    #     for point in ch.points:
    #         if len(point) == 2 or point[2] != 2:
    #             z_sample = samples[s_index].z / OCL_SCALE
    #             ch.points[p_index] = (point[0], point[1], z_sample)
    #         # print(str(point[2]))
    #         else:
    #             ch.points[p_index] = (point[0], point[1], 1)
    #         p_index += 1
    #         s_index += 1


def exportModelsToSTL(operation):
    file_number = 0
    for collision_object in operation.objects:
        activate(collision_object)
        bpy.ops.object.duplicate(linked=False)
        # collision_object = bpy.context.scene.objects.active
        # bpy.context.scene.objects.selected = collision_object
        file_name = os.path.join(tempfile.gettempdir(), "model{0}.stl".format(str(file_number)))
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.transform.resize(value=(OCL_SCALE, OCL_SCALE, OCL_SCALE), constraint_axis=(False, False, False),
                                 orient_type='GLOBAL', mirror=False, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False,
                                 snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0),
                                 texture_space=False, release_confirm=False)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.export_mesh.stl(check_existing=True, filepath=file_name, filter_glob="*.stl", use_selection=True,
                                ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1.0)
        bpy.ops.object.delete()
        file_number += 1


async def oclSamplePoints(operation, points):
    samples = await ocl_sample(operation, points)
    pointSamplesFromOCL(points, samples)


async def oclSample(operation, chunks):
    samples = await ocl_sample(operation, chunks)
    chunkPointSamplesFromOCL(chunks, samples)


async def oclResampleChunks(operation, chunks_to_resample,use_cached_mesh):
    tmp_chunks = list()
    tmp_chunks.append(camPathChunk(inpoints=[]))
    for chunk, i_start, i_length in chunks_to_resample:
        tmp_chunks[0].extend(chunk.get_points_np()[i_start:i_start+i_length])
        print(i_start,i_length,len(tmp_chunks[0].points))
 
    samples = await ocl_sample(operation, tmp_chunks,use_cached_mesh=use_cached_mesh)

    sample_index = 0
    for chunk, i_start, i_length in chunks_to_resample:
        z = np.array([p.z for p in samples[sample_index:sample_index+i_length]]) / OCL_SCALE
        pts = chunk.get_points_np()
        pt_z = pts[i_start:i_start+i_length,2]
        pt_z = np.where(z>pt_z,z,pt_z)

        sample_index += i_length
        # for p_index in range(i_start, i_start + i_length):
        #     z = samples[sample_index].z / OCL_SCALE
        #     sample_index += 1
        #     if z > chunk.points[p_index][2]:
        #         chunk.points[p_index][2] = z


def oclWaterlineLayerHeights(operation):
    layers = []
    l_last = operation.minz
    l_step = operation.stepdown
    l_first = operation.maxz - l_step
    l_depth = l_first
    while l_depth > (l_last + 0.0000001):
        layers.append(l_depth)
        l_depth -= l_step
    layers.append(l_last)
    return layers

def oclGetMedialAxis(operation, chunks):
    oclWaterlineHeightsToOCL(operation)
    operationSettingsToOCL(operation)
    curvesToOCL(operation)
    call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "ocl.py")])
    waterlineChunksFromOCL(operation, chunks)


async def oclGetWaterline(operation, chunks):
    layers = oclWaterlineLayerHeights(operation)
    oclSTL = get_oclSTL(operation)

    op_cutter_type = operation.cutter_type
    op_cutter_diameter = operation.cutter_diameter
    op_minz = operation.minz
    if op_cutter_type == "VCARVE":
        op_cutter_tip_angle = operation['cutter_tip_angle']

    cutter = None
    cutter_length = 150 #TODO: automatically determine necessary cutter length depending on object size

    if op_cutter_type == 'END':
        cutter = ocl.CylCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == 'BALLNOSE':
        cutter = ocl.BallCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == 'VCARVE':
        cutter = ocl.ConeCutter((op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle, cutter_length)
    else:
        print("Cutter unsupported: {0}\n".format(op_cutter_type))
        quit()


    waterline = ocl.Waterline()
    waterline.setSTL(oclSTL)
    waterline.setCutter(cutter)
    waterline.setSampling(0.1)#TODO: add sampling setting to UI
    last_pos=[0,0,0]
    for count,height in enumerate(layers):
        layer_chunks=[]
        await progress_async("Waterline",int((100*count)/len(layers)))
        waterline.reset()
        waterline.setZ(height * OCL_SCALE)
        waterline.run2()
        wl_loops = waterline.getLoops()
        for l in wl_loops:
            inpoints=[]
            for p in l:
                inpoints.append((p.x / OCL_SCALE, p.y / OCL_SCALE, p.z / OCL_SCALE))
            inpoints.append(inpoints[0])
            chunk=camPathChunk(inpoints=inpoints)
            chunk.closed = True
            layer_chunks.append(chunk)
        # sort chunks so that ordering is stable
        chunks.extend(await utils.sortChunks(layer_chunks,operation,last_pos=last_pos))
        if len(chunks)>0:
            last_pos=chunks[-1].get_point(-1)

# def oclFillMedialAxis(operation):
