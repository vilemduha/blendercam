fabex.utilities.ocl_utils
=========================

.. py:module:: fabex.utilities.ocl_utils

.. autoapi-nested-parse::

   Fabex 'ocl_utils.py'


   Functions used by OpenCAMLib sampling.



Functions
---------

.. autoapisummary::

   fabex.utilities.ocl_utils.pointSamplesFromOCL
   fabex.utilities.ocl_utils.chunkPointSamplesFromOCL
   fabex.utilities.ocl_utils.chunkPointsResampleFromOCL
   fabex.utilities.ocl_utils.exportModelsToSTL
   fabex.utilities.ocl_utils.oclSamplePoints
   fabex.utilities.ocl_utils.oclSample
   fabex.utilities.ocl_utils.get_oclSTL
   fabex.utilities.ocl_utils.ocl_sample
   fabex.utilities.ocl_utils.oclResampleChunks


Module Contents
---------------

.. py:function:: pointSamplesFromOCL(points, samples)

   Update the z-coordinate of points based on corresponding sample values.


   This function iterates over a list of points and updates the

   z-coordinate of each point using the z value from the corresponding

   sample. The z value is scaled by a predefined constant, OCL_SCALE. It is

   assumed that the length of the points list matches the length of the
   samples list.


   :param points: A list of points, where each point is expected to be

                  a list or array with at least three elements.
   :type points: list
   :param samples: A list of sample objects, where each sample is

                   expected to have a z attribute.
   :type samples: list


.. py:function:: chunkPointSamplesFromOCL(chunks, samples)

   Chunk point samples from OCL.


   This function processes a list of chunks and corresponding samples,

   extracting the z-values from the samples and scaling them according to a

   predefined constant (OCL_SCALE). It sets the scaled z-values for each

   chunk based on the number of points in that chunk.


   :param chunks: A list of chunk objects that have a method `count()`

                  and a method `set_z()`.
   :type chunks: list
   :param samples: A list of sample objects from which z-values are

                   extracted.
   :type samples: list


.. py:function:: chunkPointsResampleFromOCL(chunks, samples)

   Resample the Z values of points in chunks based on provided samples.


   This function iterates through a list of chunks and resamples the Z

   values of the points in each chunk using the corresponding samples. It

   first counts the number of points in each chunk, then extracts the Z

   values from the samples, scales them by a predefined constant

   (OCL_SCALE), and sets the resampled Z values back to the chunk.


   :param chunks: A list of chunk objects, each containing points that need

                  to be resampled.
   :type chunks: list
   :param samples: A list of sample objects from which Z values are extracted.
   :type samples: list


.. py:function:: exportModelsToSTL(operation)

   Export models to STL format.


   This function takes an operation containing a collection of collision

   objects and exports each object as an STL file. It duplicates each

   object, applies transformations, and resizes them according to a

   predefined scale before exporting them to the temporary directory. The

   exported files are named sequentially as "model0.stl", "model1.stl",

   etc. After exporting, the function deletes the duplicated objects to
   clean up the scene.


   :param operation: An object containing a collection of collision objects to be exported.


.. py:function:: oclSamplePoints(operation, points)
   :async:


   Sample points using an operation and process the results.


   This asynchronous function takes an operation and a set of points,

   samples the points using the specified operation, and then processes the

   sampled points. The function relies on an external sampling function and

   a processing function to handle the sampling and post-processing of the
   data.


   :param operation: The operation to be performed on the points.
   :type operation: str
   :param points: A list of points to be sampled.
   :type points: list


.. py:function:: oclSample(operation, chunks)
   :async:


   Perform an operation on a set of chunks and process the resulting
   samples.


   This asynchronous function calls the `ocl_sample` function to obtain

   samples based on the provided operation and chunks. After retrieving the

   samples, it processes them using the `chunkPointSamplesFromOCL`

   function. This is useful for handling large datasets in a chunked

   manner, allowing for efficient sampling and processing.


   :param operation: The operation to be performed on the chunks.
   :type operation: str
   :param chunks: A list of data chunks to be processed.
   :type chunks: list

   :returns: This function does not return a value.
   :rtype: None


.. py:function:: get_oclSTL(operation)

   Get the oclSTL representation from the provided operation.


   This function iterates through the objects in the given operation and

   constructs an oclSTL object by extracting triangle data from mesh,

   curve, font, or surface objects. It activates each object and checks its

   type to determine if it can be processed. If no valid objects are found,

   it raises an exception.


   :param operation: An object containing a collection of objects
   :type operation: Operation

   :returns: An oclSTL object containing the triangles derived from

             the valid objects.
   :rtype: ocl.STLSurf

   :raises CamException: If no mesh, curve, or equivalent object is found in


.. py:function:: ocl_sample(operation, chunks, use_cached_mesh=False)
   :async:


   Sample points using a specified cutter and operation.


   This function takes an operation and a list of chunks, and samples

   points based on the specified cutter type and its parameters. It

   supports various cutter types such as 'END', 'BALLNOSE', 'VCARVE',

   'CYLCONE', 'BALLCONE', and 'BULLNOSE'. The function can also utilize a

   cached mesh for efficiency. The sampled points are returned after

   processing all chunks.


   :param operation: An object containing the cutter type, diameter,

                     minimum Z value, tip angle, and other relevant parameters.
   :type operation: Operation
   :param chunks: A list of chunk objects that contain point data to be
                  processed.
   :type chunks: list
   :param use_cached_mesh: A flag indicating whether to use a cached mesh

                           if available. Defaults to False.
   :type use_cached_mesh: bool

   :returns: A list of sampled CL points generated by the cutter.
   :rtype: list


.. py:function:: oclResampleChunks(operation, chunks_to_resample, use_cached_mesh)
   :async:


   Resample chunks of data using OpenCL operations.


   This function takes a list of chunks to resample and performs an OpenCL

   sampling operation on them. It first prepares a temporary chunk that

   collects points from the specified chunks. Then, it calls the

   `ocl_sample` function to perform the sampling operation. After obtaining

   the samples, it updates the z-coordinates of the points in each chunk

   based on the sampled values.


   :param operation: The OpenCL operation to be performed.
   :type operation: OperationType
   :param chunks_to_resample: A list of tuples, where each tuple contains

                              a chunk object and its corresponding start index and length for

                              resampling.
   :type chunks_to_resample: list
   :param use_cached_mesh: A flag indicating whether to use cached mesh

                           data during the sampling process.
   :type use_cached_mesh: bool

   :returns:

             This function does not return a value but modifies the input

                 chunks in place.
   :rtype: None


