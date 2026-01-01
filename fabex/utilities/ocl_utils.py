"""Fabex 'ocl_utils.py'


Functions used by OpenCAMLib sampling.

"""

from math import radians, tan
import os
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


try:
    from bl_ext.blender_org.stl_format_legacy import blender_utils

except ImportError:
    pass
import mathutils


from ..constants import OCL_SCALE, _PREVIOUS_OCL_MESH

from ..exception import CamException

from .async_utils import progress_async

from ..chunk_builder import CamPathChunk

from .logging_utils import log

from .simple_utils import activate


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

            and a method `set_z()`.

        samples (list): A list of sample objects from which z-values are

            extracted.

    """

    s_index = 0

    for ch in chunks:
        ch_points = ch.count()

        z_vals = np.array([p.z for p in samples[s_index : s_index + ch_points]])

        z_vals /= OCL_SCALE

        ch.set_z(z_vals)

        s_index += ch_points


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

        z_vals = np.array([p.z for p in samples[s_index : s_index + ch_points]])

        z_vals /= OCL_SCALE

        ch.set_z(z_vals)

        s_index += ch_points


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

        bpy.ops.transform.resize(
            value=(OCL_SCALE, OCL_SCALE, OCL_SCALE),
            constraint_axis=(False, False, False),
            orient_type="GLOBAL",
            mirror=False,
            use_proportional_edit=False,
            proportional_edit_falloff="SMOOTH",
            proportional_size=1,
            snap=False,
            snap_target="CLOSEST",
            snap_point=(0, 0, 0),
            snap_align=False,
            snap_normal=(0, 0, 0),
            texture_space=False,
            release_confirm=False,
        )

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.ops.export_mesh.stl(
            check_existing=True,
            filepath=file_name,
            filter_glob="*.stl",
            use_selection=True,
            ascii=False,
            use_mesh_modifiers=True,
            axis_forward="Y",
            axis_up="Z",
            global_scale=1.0,
        )

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


def get_oclSTL(operation):
    """Get the oclSTL representation from the provided operation.


    This function iterates through the objects in the given operation and

    constructs an oclSTL object by extracting triangle data from mesh,

    curve, font, or surface objects. It activates each object and checks its

    type to determine if it can be processed. If no valid objects are found,

    it raises an exception.


    Args:

        operation (Operation): An object containing a collection of objects


    Returns:

        ocl.STLSurf: An oclSTL object containing the triangles derived from

        the valid objects.


    Raises:

        CamException: If no mesh, curve, or equivalent object is found in

    """

    me = None

    oclSTL = ocl.STLSurf()

    found_mesh = False

    for collision_object in operation.objects:
        activate(collision_object)

        if (
            collision_object.type == "MESH"
            or collision_object.type == "CURVE"
            or collision_object.type == "FONT"
            or collision_object.type == "SURFACE"
        ):
            found_mesh = True

            global_matrix = mathutils.Matrix.Identity(4)

            faces = blender_utils.faces_from_mesh(
                collision_object, global_matrix, operation.use_modifiers
            )

            for face in faces:
                t = ocl.Triangle(
                    ocl.Point(
                        face[0][0] * OCL_SCALE,
                        face[0][1] * OCL_SCALE,
                        (face[0][2] + operation.skin) * OCL_SCALE,
                    ),
                    ocl.Point(
                        face[1][0] * OCL_SCALE,
                        face[1][1] * OCL_SCALE,
                        (face[1][2] + operation.skin) * OCL_SCALE,
                    ),
                    ocl.Point(
                        face[2][0] * OCL_SCALE,
                        face[2][1] * OCL_SCALE,
                        (face[2][2] + operation.skin) * OCL_SCALE,
                    ),
                )

                oclSTL.addTriangle(t)

        # FIXME needs to work with collections

    if not found_mesh:
        raise CamException(
            "This Operation Requires a Mesh or Curve Object or Equivalent (e.g. Text, Volume)."
        )

    return oclSTL


async def ocl_sample(operation, chunks, use_cached_mesh=False):
    """Sample points using a specified cutter and operation.


    This function takes an operation and a list of chunks, and samples

    points based on the specified cutter type and its parameters. It

    supports various cutter types such as 'END', 'BALLNOSE', 'VCARVE',

    'CYLCONE', 'BALLCONE', and 'BULLNOSE'. The function can also utilize a

    cached mesh for efficiency. The sampled points are returned after

    processing all chunks.


    Args:

        operation (Operation): An object containing the cutter type, diameter,

            minimum Z value, tip angle, and other relevant parameters.

        chunks (list): A list of chunk objects that contain point data to be
            processed.

        use_cached_mesh (bool): A flag indicating whether to use a cached mesh

            if available. Defaults to False.


    Returns:

        list: A list of sampled CL points generated by the cutter.

    """

    global _PREVIOUS_OCL_MESH

    op_cutter_type = operation.cutter_type

    op_cutter_diameter = operation.cutter_diameter

    op_minz = operation.min_z

    op_cutter_tip_angle = radians(operation.cutter_tip_angle) / 2

    if op_cutter_type == "VCARVE":
        cutter_length = (op_cutter_diameter / tan(op_cutter_tip_angle)) / 2

    else:
        cutter_length = 10

    cutter = None

    if op_cutter_type == "END":
        cutter = ocl.CylCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)

    elif op_cutter_type == "BALLNOSE":
        cutter = ocl.BallCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)

    elif op_cutter_type == "VCARVE":
        cutter = ocl.ConeCutter(
            (op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle, cutter_length
        )

    elif op_cutter_type == "CYLCONE":
        cutter = ocl.CylConeCutter(
            (operation.cylcone_diameter / 2 + operation.skin) * 2000,
            (op_cutter_diameter + operation.skin * 2) * 1000,
            op_cutter_tip_angle,
        )

    elif op_cutter_type == "BALLCONE":
        cutter = ocl.BallConeCutter(
            (operation.ball_radius + operation.skin) * 2000,
            (op_cutter_diameter + operation.skin * 2) * 1000,
            op_cutter_tip_angle,
        )

    elif op_cutter_type == "BULLNOSE":
        cutter = ocl.BullCutter(
            (op_cutter_diameter + operation.skin * 2) * 1000,
            operation.bull_corner_radius * 1000,
            cutter_length,
        )

    else:
        log.info(f"Cutter Unsupported: {op_cutter_type}\n")

        quit()

    bdc = ocl.BatchDropCutter()

    if use_cached_mesh and _PREVIOUS_OCL_MESH is not None:
        oclSTL = _PREVIOUS_OCL_MESH

    else:
        oclSTL = get_oclSTL(operation)

        _PREVIOUS_OCL_MESH = oclSTL

    bdc.setSTL(oclSTL)

    bdc.setCutter(cutter)

    for chunk in chunks:
        for coord in chunk.get_points_np():
            bdc.appendPoint(ocl.CLPoint(coord[0] * 1000, coord[1] * 1000, op_minz * 1000))

    await progress_async("OpenCAMLib Sampling")

    bdc.run()

    cl_points = bdc.getCLPoints()

    return cl_points


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

    tmp_chunks.append(CamPathChunk(inpoints=[]))

    for chunk, i_start, i_length in chunks_to_resample:
        tmp_chunks[0].extend(chunk.get_points_np()[i_start : i_start + i_length])

        log.info(f"{i_start}, {i_length}, {len(tmp_chunks[0].points)}")

    samples = await ocl_sample(operation, tmp_chunks, use_cached_mesh=use_cached_mesh)

    sample_index = 0

    for chunk, i_start, i_length in chunks_to_resample:
        z = np.array([p.z for p in samples[sample_index : sample_index + i_length]]) / OCL_SCALE

        pts = chunk.get_points_np()

        pt_z = pts[i_start : i_start + i_length, 2]

        pt_z = np.where(z > pt_z, z, pt_z)

        sample_index += i_length
