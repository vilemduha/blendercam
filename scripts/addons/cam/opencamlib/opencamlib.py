# used by OpenCAMLib sampling

import bpy
import ocl
import os
import tempfile
from subprocess import call
from cam.collision import BULLET_SCALE
from cam import simple
from cam.chunk import camPathChunk
from cam.simple import *
from shapely import geometry as sgeometry
from .oclSample import get_oclSTL

from cam.opencamlib.oclSample import ocl_sample

OCL_SCALE = 1000.0

PYTHON_BIN = None

#
# def operationSettingsToCSV(operation):
#     with open(os.path.join(tempfile.gettempdir(), 'ocl_settings.txt'), 'w') as csv_file:
#         csv_file.write("{}\n".format(operation.cutter_type))
#         csv_file.write("{}\n".format(operation.cutter_diameter))
#         if operation.cutter_type == "VCARVE":
#             csv_file.write("{}\n".format(operation.cutter_tip_angle))
#         csv_file.write("{}\n".format(operation.minz))

#
# def pointsToCSV(operation, points):
#     with open(os.path.join(tempfile.gettempdir(), 'ocl_chunks.txt'), 'w') as csv_file:
#         for point in points:
#             csv_file.write("{} {}\n".format(point[0], point[1]))


def pointSamplesFromCSV(points, samples):
    for index, point in enumerate(points):
        point[2] = samples[index].z / OCL_SCALE
    # print(str(point[2]))

#
# def chunkPointsToCSV(operation, chunks):
#     with open(os.path.join(tempfile.gettempdir(), 'ocl_chunks.txt'), 'w')as csv_file:
#         for ch in chunks:
#             p_index = 0
#             for point in ch.points:
#                 if operation.ambient.contains(sgeometry.Point(point[0], point[1])):
#                     csv_file.write("{} {}\n".format(point[0], point[1]))
#                 else:
#                     ch.points[p_index] = (point[0], point[1], 2)
#                 p_index += 1


def chunkPointSamplesFromCSV(chunks, samples):

    s_index = 0
    for ch in chunks:
        p_index = 0
        for point in ch.points:
            if len(point) == 2 or point[2] != 2:
                z_sample = samples[s_index].z / OCL_SCALE
                ch.points[p_index] = (point[0], point[1], z_sample)
            # print(str(point[2]))
            else:
                ch.points[p_index] = (point[0], point[1], 1)
            p_index += 1
            s_index += 1

#
# def resampleChunkPointsToCSV(operation, chunks_to_resample):
#     with open(os.path.join(tempfile.gettempdir(), 'ocl_chunks.txt'), 'w') as csv_file:
#         for chunk, i_start, i_length in chunks_to_resample:
#             for p_index in range(i_start, i_start + i_length):
#                 csv_file.write("{} {}\n".format(chunk.points[p_index][0], chunk.points[p_index][1]))


def chunkPointsResampleFromCSV(chunks, samples):

    s_index = 0
    for ch in chunks:
        p_index = 0
        for point in ch.points:
            if len(point) == 2 or point[2] != 2:
                z_sample = samples[s_index].z / OCL_SCALE
                ch.points[p_index] = (point[0], point[1], z_sample)
            # print(str(point[2]))
            else:
                ch.points[p_index] = (point[0], point[1], 1)
            p_index += 1
            s_index += 1


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


def oclSamplePoints(operation, points):

    #exportModelsToSTL(operation)

    samples = ocl_sample(operation, points)
    pointSamplesFromCSV(points, samples)


def oclSample(operation, chunks):

    #exportModelsToSTL(operation)

    samples = ocl_sample(operation, chunks)
    chunkPointSamplesFromCSV(chunks, samples)


def oclResampleChunks(operation, chunks_to_resample):
    #tmp_chunks = list()
    #tmp_chunks.append(camPathChunk(list()))

    #for chunk, i_start, i_length in chunks_to_resample:
        #for p_index in range(i_start, i_start + i_length):
            #tmp_chunks[0].append(Vector((chunk.points[p_index][0], chunk.points[p_index][1], chunk.points[p_index][2])))
    
    #samples = ocl_sample(operation, tmp_chunks)
    
    #sample_index = 0
    #for chunk, i_start, i_length in chunks_to_resample:
        #for p_index in range(i_start, i_start + i_length):
            #z = samples[sample_index].z
            #if z > chunk.points[p_index][2]:
                #chunk.points[p_index][2] = z / OCL_SCALE

    chunks = list()
    for chunks_data in chunks_to_resample:
        chunks.append(chunks_data[0])

    samples = ocl_sample(operation, chunks)
    chunkPointsResampleFromCSV(chunks, samples)


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



def waterlineChunksFromCSV(operation, chunks):
    layers = oclWaterlineLayerHeights(operation)
    wl_index = 0
    for layer in layers:
        csv_file = open(os.path.join(tempfile.gettempdir(), 'oclWaterline') + str(wl_index) + '.txt', 'r')
        print(str(wl_index) + "\n")
        for line in csv_file:
            if line[0] == 'l':
                chunks.append(camPathChunk(inpoints=[]))
            else:
                point = [float(coord) / OCL_SCALE for coord in line.split()]
                chunks[-1].points.append((point[0], point[1], point[2]))
        wl_index += 1
        csv_file.close()
    chunks.append(camPathChunk(inpoints=[]))


def oclGetMedialAxis(operation, chunks):
    oclWaterlineHeightsToCSV(operation)
    operationSettingsToCSV(operation)
    curvesToCSV(operation)
    call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "ocl.py")])
    waterlineChunksFromCSV(operation, chunks)


def oclGetWaterline(operation, chunks):
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
        cutter = ocl.CylCutter(op_cutter_diameter * 1000, cutter_length)
    elif op_cutter_type == 'BALLNOSE':
        cutter = ocl.BallCutter(op_cutter_diameter * 1000, cutter_length)
    elif op_cutter_type == 'VCARVE':
        cutter = ocl.ConeCutter(op_cutter_diameter * 1000, op_cutter_tip_angle, cutter_length)
    else:
        print("Cutter unsupported: {0}\n".format(op_cutter_type))
        quit()


    waterline = ocl.Waterline()
    waterline.setSTL(oclSTL)
    waterline.setCutter(cutter)
    waterline.setSampling(0.1)#TODO: add sampling setting to UI
    for height in layers:
        print(str(height) + '\n')
        waterline.reset()
        waterline.setZ(height * OCL_SCALE)
        waterline.run2()
        wl_loops = waterline.getLoops()
        for l in wl_loops:
            chunks.append(camPathChunk(inpoints=[]))
            for p in l:
                chunks[-1].points.append((p.x / OCL_SCALE, p.y / OCL_SCALE, p.z / OCL_SCALE))
            chunks[-1].points.append(chunks[-1].points[0])
            chunks[-1].closed = True
            chunks[-1].poly = sgeometry.Polygon(chunks[-1].points)

# def oclFillMedialAxis(operation):
