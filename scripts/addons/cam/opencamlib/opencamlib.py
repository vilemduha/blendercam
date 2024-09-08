"""BlenderCAM 'oclSample.py'

Functions used by OpenCAMLib sampling.
"""

import os
from subprocess import call
import tempfile

import numpy as np
try:
    import ocl
except ImportError:
    try:
        import opencamlib as ocl
    except ImportError:
        pass

import bpy

from ..constants import BULLET_SCALE
from ..simple import activate
from .. import utils
from ..cam_chunk import camPathChunk
from ..async_op import progress_async
from .oclSample import (
    get_oclSTL,
    ocl_sample
)

OCL_SCALE = 1000.0

PYTHON_BIN = None


def pointSamplesFromOCL(points, samples):
    """Update the z-coordinate of points based on corresponding sample values.

    This function iterates over a list of points and updates the
    z-coordinate of each point using the z value from the corresponding
    sample. The z value is scaled by a predefined constant, OCL_SCALE. It is
    assumed that the length of the points list matches the length of the
    samples list.

    Args:
        points (list): A list of points, where each point is expected to be
            a list or array with at least three elements.
        samples (list): A list of sample objects, where each sample is
            expected to have a z attribute.
    """
    for index, point in enumerate(points):
        point[2] = samples[index].z / OCL_SCALE


def chunkPointSamplesFromOCL(chunks, samples):
    """Chunk point samples from OCL.

    This function processes a list of chunks and corresponding samples,
    extracting the z-values from the samples and scaling them according to a
    predefined constant (OCL_SCALE). It sets the scaled z-values for each
    chunk based on the number of points in that chunk.

    Args:
        chunks (list): A list of chunk objects that have a method `count()`
            and a method `setZ()`.
        samples (list): A list of sample objects from which z-values are
            extracted.
    """
    s_index = 0
    for ch in chunks:
        ch_points = ch.count()
        z_vals = np.array([p.z for p in samples[s_index:s_index+ch_points]])
        z_vals /= OCL_SCALE
        ch.setZ(z_vals)
        s_index += ch_points
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
    """Resample the Z values of points in chunks based on provided samples.

    This function iterates through a list of chunks and resamples the Z
    values of the points in each chunk using the corresponding samples. It
    first counts the number of points in each chunk, then extracts the Z
    values from the samples, scales them by a predefined constant
    (OCL_SCALE), and sets the resampled Z values back to the chunk.

    Args:
        chunks (list): A list of chunk objects, each containing points that need
            to be resampled.
        samples (list): A list of sample objects from which Z values are extracted.
    """
    s_index = 0
    for ch in chunks:
        ch_points = ch.count()
        z_vals = np.array([p.z for p in samples[s_index:s_index+ch_points]])
        z_vals /= OCL_SCALE
        ch.setZ(z_vals)
        s_index += ch_points

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
    """Export models to STL format.

    This function takes an operation containing a collection of collision
    objects and exports each object as an STL file. It duplicates each
    object, applies transformations, and resizes them according to a
    predefined scale before exporting them to the temporary directory. The
    exported files are named sequentially as "model0.stl", "model1.stl",
    etc. After exporting, the function deletes the duplicated objects to
    clean up the scene.

    Args:
        operation: An object containing a collection of collision objects to be exported.
    """
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
    """Sample points using an operation and process the results.

    This asynchronous function takes an operation and a set of points,
    samples the points using the specified operation, and then processes the
    sampled points. The function relies on an external sampling function and
    a processing function to handle the sampling and post-processing of the
    data.

    Args:
        operation (str): The operation to be performed on the points.
        points (list): A list of points to be sampled.
    """

    samples = await ocl_sample(operation, points)
    pointSamplesFromOCL(points, samples)


async def oclSample(operation, chunks):
    """Perform an operation on a set of chunks and process the resulting
    samples.

    This asynchronous function calls the `ocl_sample` function to obtain
    samples based on the provided operation and chunks. After retrieving the
    samples, it processes them using the `chunkPointSamplesFromOCL`
    function. This is useful for handling large datasets in a chunked
    manner, allowing for efficient sampling and processing.

    Args:
        operation (str): The operation to be performed on the chunks.
        chunks (list): A list of data chunks to be processed.

    Returns:
        None: This function does not return a value.
    """

    samples = await ocl_sample(operation, chunks)
    chunkPointSamplesFromOCL(chunks, samples)


async def oclResampleChunks(operation, chunks_to_resample, use_cached_mesh):
    """Resample chunks of data using OpenCL operations.

    This function takes a list of chunks to resample and performs an OpenCL
    sampling operation on them. It first prepares a temporary chunk that
    collects points from the specified chunks. Then, it calls the
    `ocl_sample` function to perform the sampling operation. After obtaining
    the samples, it updates the z-coordinates of the points in each chunk
    based on the sampled values.

    Args:
        operation (OperationType): The OpenCL operation to be performed.
        chunks_to_resample (list): A list of tuples, where each tuple contains
            a chunk object and its corresponding start index and length for
            resampling.
        use_cached_mesh (bool): A flag indicating whether to use cached mesh
            data during the sampling process.

    Returns:
        None: This function does not return a value but modifies the input
            chunks in place.
    """

    tmp_chunks = list()
    tmp_chunks.append(camPathChunk(inpoints=[]))
    for chunk, i_start, i_length in chunks_to_resample:
        tmp_chunks[0].extend(chunk.get_points_np()[i_start:i_start+i_length])
        print(i_start, i_length, len(tmp_chunks[0].points))

    samples = await ocl_sample(operation, tmp_chunks, use_cached_mesh=use_cached_mesh)

    sample_index = 0
    for chunk, i_start, i_length in chunks_to_resample:
        z = np.array([p.z for p in samples[sample_index:sample_index+i_length]]) / OCL_SCALE
        pts = chunk.get_points_np()
        pt_z = pts[i_start:i_start+i_length, 2]
        pt_z = np.where(z > pt_z, z, pt_z)

        sample_index += i_length
        # for p_index in range(i_start, i_start + i_length):
        #     z = samples[sample_index].z / OCL_SCALE
        #     sample_index += 1
        #     if z > chunk.points[p_index][2]:
        #         chunk.points[p_index][2] = z


def oclWaterlineLayerHeights(operation):
    """Generate a list of waterline layer heights for a given operation.

    This function calculates the heights of waterline layers based on the
    specified parameters of the operation. It starts from the maximum height
    and decrements by a specified step until it reaches the minimum height.
    The resulting list of heights can be used for further processing in
    operations that require layered depth information.

    Args:
        operation (object): An object containing the properties `minz`,
            `maxz`, and `stepdown` which define the
            minimum height, maximum height, and step size
            for layer generation, respectively.

    Returns:
        list: A list of waterline layer heights from maximum to minimum.
    """
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


# def oclGetMedialAxis(operation, chunks):
#     oclWaterlineHeightsToOCL(operation)
#     operationSettingsToOCL(operation)
#     curvesToOCL(operation)
#     call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "ocl.py")])
#     waterlineChunksFromOCL(operation, chunks)


async def oclGetWaterline(operation, chunks):
    """Generate waterline paths for a given machining operation.

    This function calculates the waterline paths based on the provided
    machining operation and its parameters. It determines the appropriate
    cutter type and dimensions, sets up the waterline object with the
    corresponding STL file, and processes each layer to generate the
    machining paths. The resulting paths are stored in the provided chunks
    list. The function also handles different cutter types, including end
    mills, ball nose cutters, and V-carve cutters.

    Args:
        operation (Operation): An object representing the machining operation,
            containing details such as cutter type, diameter, and minimum Z height.
        chunks (list): A list that will be populated with the generated
            machining path chunks.
    """

    layers = oclWaterlineLayerHeights(operation)
    oclSTL = get_oclSTL(operation)

    op_cutter_type = operation.cutter_type
    op_cutter_diameter = operation.cutter_diameter
    op_minz = operation.minz
    if op_cutter_type == "VCARVE":
        op_cutter_tip_angle = operation['cutter_tip_angle']

    cutter = None
    # TODO: automatically determine necessary cutter length depending on object size
    cutter_length = 150

    if op_cutter_type == 'END':
        cutter = ocl.CylCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == 'BALLNOSE':
        cutter = ocl.BallCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == 'VCARVE':
        cutter = ocl.ConeCutter((op_cutter_diameter + operation.skin * 2)
                                * 1000, op_cutter_tip_angle, cutter_length)
    else:
        print("Cutter unsupported: {0}\n".format(op_cutter_type))
        quit()

    waterline = ocl.Waterline()
    waterline.setSTL(oclSTL)
    waterline.setCutter(cutter)
    waterline.setSampling(0.1)  # TODO: add sampling setting to UI
    last_pos = [0, 0, 0]
    for count, height in enumerate(layers):
        layer_chunks = []
        await progress_async("Waterline", int((100*count)/len(layers)))
        waterline.reset()
        waterline.setZ(height * OCL_SCALE)
        waterline.run2()
        wl_loops = waterline.getLoops()
        for l in wl_loops:
            inpoints = []
            for p in l:
                inpoints.append((p.x / OCL_SCALE, p.y / OCL_SCALE, p.z / OCL_SCALE))
            inpoints.append(inpoints[0])
            chunk = camPathChunk(inpoints=inpoints)
            chunk.closed = True
            layer_chunks.append(chunk)
        # sort chunks so that ordering is stable
        chunks.extend(await utils.sortChunks(layer_chunks, operation, last_pos=last_pos))
        if len(chunks) > 0:
            last_pos = chunks[-1].get_point(-1)

# def oclFillMedialAxis(operation):
