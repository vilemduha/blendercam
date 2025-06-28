fabex.cam_chunk
===============

.. py:module:: fabex.cam_chunk

.. autoapi-nested-parse::

   Fabex 'cam_chunk.py' © 2012 Vilem Novak

   Classes and Functions to build, store and optimize CAM path chunks.



Classes
-------

.. autoapisummary::

   fabex.cam_chunk.CamPathChunkBuilder
   fabex.cam_chunk.CamPathChunk


Functions
---------

.. autoapisummary::

   fabex.cam_chunk.chunks_coherency
   fabex.cam_chunk.limit_chunks
   fabex.cam_chunk.mesh_from_curve_to_chunk
   fabex.cam_chunk.curve_to_chunks
   fabex.cam_chunk.shapely_to_chunks
   fabex.cam_chunk.curve_to_shapely
   fabex.cam_chunk.sample_chunks_n_axis
   fabex.cam_chunk.sample_path_low
   fabex.cam_chunk.polygon_boolean
   fabex.cam_chunk.polygon_convex_hull
   fabex.cam_chunk.silhouette_offset
   fabex.cam_chunk.get_object_silhouette
   fabex.cam_chunk.get_operation_silhouette
   fabex.cam_chunk.get_object_outline
   fabex.cam_chunk.get_ambient
   fabex.cam_chunk.sample_chunks
   fabex.cam_chunk.connect_chunks_low
   fabex.cam_chunk.sort_chunks
   fabex.cam_chunk.oclResampleChunks
   fabex.cam_chunk.oclGetWaterline
   fabex.cam_chunk.image_edge_search_on_line
   fabex.cam_chunk.get_offset_image_cavities
   fabex.cam_chunk.crazy_stroke_image
   fabex.cam_chunk.crazy_stroke_image_binary
   fabex.cam_chunk.image_to_chunks
   fabex.cam_chunk.image_to_shapely


Module Contents
---------------

.. py:class:: CamPathChunkBuilder(inpoints=None, startpoints=None, endpoints=None, rotations=None)

   .. py:attribute:: points
      :value: None



   .. py:attribute:: startpoints
      :value: []



   .. py:attribute:: endpoints
      :value: []



   .. py:attribute:: rotations
      :value: []



   .. py:attribute:: depth
      :value: None



   .. py:method:: to_chunk()


.. py:class:: CamPathChunk(inpoints, startpoints=None, endpoints=None, rotations=None)

   .. py:attribute:: poly
      :value: None



   .. py:attribute:: simppoly
      :value: None



   .. py:attribute:: closed
      :value: False



   .. py:attribute:: children
      :value: []



   .. py:attribute:: parents
      :value: []



   .. py:attribute:: sorted
      :value: False



   .. py:attribute:: length
      :value: 0



   .. py:attribute:: zstart
      :value: 0



   .. py:attribute:: zend
      :value: 0



   .. py:method:: update_poly()


   .. py:method:: get_point(n)


   .. py:method:: get_points()


   .. py:method:: get_points_np()


   .. py:method:: set_points(points)


   .. py:method:: count()


   .. py:method:: copy()


   .. py:method:: shift(x, y, z)


   .. py:method:: set_z(z, if_bigger=False)


   .. py:method:: offset_z(z)


   .. py:method:: flip_x(x_centre)


   .. py:method:: is_below_z(z)


   .. py:method:: clamp_z(z)


   .. py:method:: clamp_max_z(z)


   .. py:method:: distance(pos, o)


   .. py:method:: distance_start(pos, o)


   .. py:method:: x_y_distance_within(other, cutoff)


   .. py:method:: x_y_distance_to(other, cutoff=0)


   .. py:method:: adapt_distance(pos, o)


   .. py:method:: get_next_closest(o, pos)


   .. py:method:: get_length()


   .. py:method:: reverse()


   .. py:method:: pop(index)


   .. py:method:: dedupe_points()


   .. py:method:: insert(at_index, point, startpoint=None, endpoint=None, rotation=None)


   .. py:method:: append(point, startpoint=None, endpoint=None, rotation=None, at_index=None)


   .. py:method:: extend(points, startpoints=None, endpoints=None, rotations=None, at_index=None)


   .. py:method:: clip_points(minx, maxx, miny, maxy)

      Remove Any Points Outside This Range



   .. py:method:: ramp_contour(zstart, zend, o)


   .. py:method:: ramp_zig_zag(zstart, zend, o)


   .. py:method:: change_path_start(o)


   .. py:method:: break_path_for_leadin_leadout(o)


   .. py:method:: lead_contour(o)


.. py:function:: chunks_coherency(chunks)

.. py:function:: limit_chunks(chunks, o, force=False)

.. py:function:: mesh_from_curve_to_chunk(object)

.. py:function:: curve_to_chunks(o, use_modifiers=False)

.. py:function:: shapely_to_chunks(p, zlevel)

.. py:function:: curve_to_shapely(cob, use_modifiers=False)

   Convert a curve object to Shapely polygons.

   This function takes a curve object and converts it into a list of
   Shapely polygons. It first breaks the curve into chunks and then
   transforms those chunks into Shapely-compatible polygon representations.
   The `use_modifiers` parameter allows for additional processing of the
   curve before conversion, depending on the specific requirements of the
   application.

   :param cob: The curve object to be converted.
   :param use_modifiers: A flag indicating whether to apply modifiers
                         during the conversion process. Defaults to False.
   :type use_modifiers: bool

   :returns: A list of Shapely polygons created from the curve object.
   :rtype: list


.. py:function:: sample_chunks_n_axis(o, pathSamples, layers)
   :async:


   Sample chunks along a specified axis based on provided paths and layers.

   This function processes a set of path samples and organizes them into
   chunks according to specified layers. It prepares the collision world if
   necessary, updates the cutter's rotation based on the path samples, and
   handles the sampling of points along the paths. The function also
   manages the relationships between the sampled points and their
   respective layers, ensuring that the correct points are added to each
   chunk. The resulting chunks can be used for further processing in a 3D
   environment.

   :param o: An object containing properties such as min/max coordinates,
             cutter shape, and other relevant parameters.
   :type o: object
   :param pathSamples: A list of path samples, each containing start points,
                       end points, and rotations.
   :type pathSamples: list
   :param layers: A list of layer definitions that specify the boundaries
                  for sampling.
   :type layers: list

   :returns: A list of sampled chunks organized by layers.
   :rtype: list


.. py:function:: sample_path_low(o, ch1, ch2, dosample)

   Generate a sample path between two channels.

   This function computes a series of points that form a path between two
   given channels. It calculates the direction vector from the end of the
   first channel to the start of the second channel and generates points
   along this vector up to a specified distance. If sampling is enabled, it
   modifies the z-coordinate of the generated points based on the cutter
   shape or image sampling, ensuring that the path accounts for any
   obstacles or features in the environment.

   :param o: An object containing optimization parameters and properties related to
             the path generation.
   :param ch1: The first channel object, which provides a point for the starting
               location of the path.
   :param ch2: The second channel object, which provides a point for the ending
               location of the path.
   :param dosample: A flag indicating whether to perform sampling along the generated path.
   :type dosample: bool

   :returns: An object representing the generated path points.
   :rtype: CamPathChunk


.. py:function:: polygon_boolean(context, boolean_type)

   Perform a boolean operation on selected polygons.

   This function takes the active object and applies a specified boolean
   operation (UNION, DIFFERENCE, or INTERSECT) with respect to other
   selected objects in the Blender context. It first converts the polygons
   of the active object and the selected objects into a Shapely
   MultiPolygon. Depending on the boolean type specified, it performs the
   corresponding boolean operation and then converts the result back into a
   Blender curve.

   :param context: The Blender context containing scene and object data.
   :type context: bpy.context
   :param boolean_type: The type of boolean operation to perform.
                        Must be one of 'UNION', 'DIFFERENCE', or 'INTERSECT'.
   :type boolean_type: str

   :returns: A dictionary indicating the operation result, typically {'FINISHED'}.
   :rtype: dict


.. py:function:: polygon_convex_hull(context)

   Generate the convex hull of a polygon from the given context.

   This function duplicates the current object, joins it, and converts it
   into a 3D mesh. It then extracts the X and Y coordinates of the vertices
   to create a MultiPoint data structure using Shapely. Finally, it
   computes the convex hull of these points and converts the result back
   into a curve named 'ConvexHull'. Temporary objects created during this
   process are deleted to maintain a clean workspace.

   :param context: The context in which the operation is performed, typically
                   related to Blender's current state.

   :returns: A dictionary indicating the operation's completion status.
   :rtype: dict


.. py:function:: silhouette_offset(context, offset, style=1, mitrelimit=1.0)

   Offset the silhouette of a curve or font object in Blender.

   This function takes an active curve or font object in Blender and
   creates an offset silhouette based on the specified parameters. It first
   retrieves the silhouette of the object and then applies a buffer
   operation to create the offset shape. The resulting shape is then
   converted back into a curve object in the Blender scene.

   :param context: The current Blender context.
   :type context: bpy.context
   :param offset: The distance to offset the silhouette.
   :type offset: float
   :param style: The join style for the offset. Defaults to 1.
   :type style: int?
   :param mitrelimit: The mitre limit for the offset. Defaults to 1.0.
   :type mitrelimit: float?

   :returns: A dictionary indicating the operation is finished.
   :rtype: dict


.. py:function:: get_object_silhouette(stype, objects=None, use_modifiers=False)

   Get the silhouette of objects based on the specified type.

   This function computes the silhouette of a given set of objects in
   Blender based on the specified type. It can handle both curves and mesh
   objects, converting curves to polygon format and calculating the
   silhouette for mesh objects. The function also considers the use of
   modifiers if specified. The silhouette is generated by processing the
   geometry of the objects and returning a Shapely representation of the
   silhouette.

   :param stype: The type of silhouette to generate ('CURVES' or 'OBJECTS').
   :type stype: str
   :param objects: A list of Blender objects to process. Defaults to None.
   :type objects: list?
   :param use_modifiers: Whether to apply modifiers to the objects. Defaults to False.
   :type use_modifiers: bool?

   :returns: The computed silhouette as a Shapely MultiPolygon.
   :rtype: shapely.geometry.MultiPolygon


.. py:function:: get_operation_silhouette(operation)

   Gets the silhouette for the given operation.

   This function determines the silhouette of an operation using image
   thresholding techniques. It handles different geometry sources, such as
   objects or images, and applies specific methods based on the type of
   geometry. If the geometry source is 'OBJECT' or 'COLLECTION', it checks
   whether to process curves or not. The function also considers the number
   of faces in mesh objects to decide on the appropriate method for
   silhouette extraction.

   :param operation: An object containing the necessary data
   :type operation: Operation

   :returns: The computed silhouette for the operation.
   :rtype: Silhouette


.. py:function:: get_object_outline(radius, o, Offset)

   Get the outline of a geometric object based on specified parameters.

   This function generates an outline for a given geometric object by
   applying a buffer operation to its polygons. The buffer radius can be
   adjusted based on the `radius` parameter, and the operation can be
   offset based on the `Offset` flag. The function also considers whether
   the polygons should be merged or not, depending on the properties of the
   object `o`.

   :param radius: The radius for the buffer operation.
   :type radius: float
   :param o: An object containing properties that influence the outline generation.
   :type o: object
   :param Offset: A flag indicating whether to apply a positive or negative offset.
   :type Offset: bool

   :returns: The resulting outline of the geometric object as a MultiPolygon.
   :rtype: MultiPolygon


.. py:function:: get_ambient(o)

   Calculate and update the ambient geometry based on the provided object.

   This function computes the ambient shape for a given object based on its
   properties, such as cutter restrictions and ambient behavior. It
   determines the appropriate radius and creates the ambient geometry
   either from the silhouette or as a polygon defined by the object's
   minimum and maximum coordinates. If a limit curve is specified, it will
   also intersect the ambient shape with the limit polygon.

   :param o: An object containing properties that define the ambient behavior,
             cutter restrictions, and limit curve.
   :type o: object

   :returns: The function updates the ambient property of the object in place.
   :rtype: None


.. py:function:: sample_chunks(o, pathSamples, layers)
   :async:


   Sample chunks of paths based on the provided parameters.

   This function processes the given path samples and layers to generate
   chunks of points that represent the sampled paths. It takes into account
   various optimization settings and strategies to determine how the points
   are sampled and organized into layers. The function handles different
   scenarios based on the object's properties and the specified layers,
   ensuring that the resulting chunks are correctly structured for further
   processing.

   :param o: An object containing various properties and settings
             related to the sampling process.
   :type o: object
   :param pathSamples: A list of path samples to be processed.
   :type pathSamples: list
   :param layers: A list of layers defining the z-coordinate ranges
                  for sampling.
   :type layers: list

   :returns:

             A list of sampled chunks, each containing points that represent
                 the sampled paths.
   :rtype: list


.. py:function:: connect_chunks_low(chunks, o)
   :async:


   Connects chunks that are close to each other without lifting, sampling
   them 'low'.

   This function processes a list of chunks and connects those that are
   within a specified distance based on the provided options. It takes into
   account various strategies for connecting the chunks, including 'CARVE',
   'PENCIL', and 'MEDIAL_AXIS', and adjusts the merging distance
   accordingly. The function also handles specific movement settings, such
   as whether to stay low or to merge distances, and may resample chunks if
   certain optimization conditions are met.

   :param chunks: A list of chunk objects to be connected.
   :type chunks: list
   :param o: An options object containing movement and strategy parameters.
   :type o: object

   :returns: A list of connected chunk objects.
   :rtype: list


.. py:function:: sort_chunks(chunks, o, last_pos=None)
   :async:


   Sort a list of chunks based on a specified strategy.

   This function sorts a list of chunks according to the provided options
   and the current position. It utilizes a recursive approach to find the
   closest chunk to the current position and adapts its distance if it has
   not been sorted before. The function also handles progress updates
   asynchronously and adjusts the recursion limit to accommodate deep
   recursion scenarios.

   :param chunks: A list of chunk objects to be sorted.
   :type chunks: list
   :param o: An options object that contains sorting strategy and other parameters.
   :type o: object
   :param last_pos: The last known position as a tuple of coordinates.
                    Defaults to None, which initializes the position to (0, 0, 0).
   :type last_pos: tuple?

   :returns: A sorted list of chunk objects.
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


.. py:function:: oclGetWaterline(operation, chunks)
   :async:


   Generate waterline paths for a given machining operation.

   This function calculates the waterline paths based on the provided
   machining operation and its parameters. It determines the appropriate
   cutter type and dimensions, sets up the waterline object with the
   corresponding STL file, and processes each layer to generate the
   machining paths. The resulting paths are stored in the provided chunks
   list. The function also handles different cutter types, including end
   mills, ball nose cutters, and V-carve cutters.

   :param operation: An object representing the machining operation,
                     containing details such as cutter type, diameter, and minimum Z height.
   :type operation: Operation
   :param chunks: A list that will be populated with the generated
                  machining path chunks.
   :type chunks: list


.. py:function:: image_edge_search_on_line(o, ar, zimage)

   Search for edges in an image using a pencil strategy.

   This function implements an edge detection algorithm that simulates a
   pencil-like movement across the image represented by a 2D array. It
   identifies white pixels and builds chunks of points based on the
   detected edges. The algorithm iteratively explores possible directions
   to find and track the edges until a specified condition is met, such as
   exhausting the available white pixels or reaching a maximum number of
   tests.

   :param o: An object containing parameters such as min, max coordinates, cutter
             diameter,
             border width, and optimisation settings.
   :type o: object
   :param ar: A 2D array representing the image where edge detection is to be
              performed.
   :type ar: np.ndarray
   :param zimage: A 2D array representing the z-coordinates corresponding to the image.
   :type zimage: np.ndarray

   :returns: A list of chunks representing the detected edges in the image.
   :rtype: list


.. py:function:: get_offset_image_cavities(o, i)

   Detects areas in the offset image which are 'cavities' due to curvature
   changes.

   This function analyzes the input image to identify regions where the
   curvature changes, indicating the presence of cavities. It computes
   vertical and horizontal differences in pixel values to detect edges and
   applies a threshold to filter out insignificant changes. The resulting
   areas are then processed to remove any chunks that do not meet the
   minimum criteria for cavity detection. The function returns a list of
   valid chunks that represent the detected cavities.

   :param o: An object containing parameters and thresholds for the detection
             process.
   :param i: A 2D array representing the image data to be analyzed.
   :type i: np.ndarray

   :returns: A list of detected chunks representing the cavities in the image.
   :rtype: list


.. py:function:: crazy_stroke_image(o)

   Generate a toolpath for a milling operation using a crazy stroke
   strategy.

   This function computes a path for a milling cutter based on the provided
   parameters and the offset image. It utilizes a circular cutter
   representation and evaluates potential cutting positions based on
   various thresholds. The algorithm iteratively tests different angles and
   lengths for the cutter's movement until the desired cutting area is
   achieved or the maximum number of tests is reached.

   :param o: An object containing parameters such as cutter diameter,
             optimization settings, movement type, and thresholds for
             determining cutting effectiveness.
   :type o: object

   :returns:

             A list of chunks representing the computed toolpath for the milling
                 operation.
   :rtype: list


.. py:function:: crazy_stroke_image_binary(o, ar, avoidar)

   Perform a milling operation using a binary image representation.

   This function implements a strategy for milling by navigating through a
   binary image. It starts from a defined point and attempts to move in
   various directions, evaluating the cutter load to determine the
   appropriate path. The algorithm continues until it either exhausts the
   available pixels to cut or reaches a predefined limit on the number of
   tests. The function modifies the input array to represent the areas that
   have been milled and returns the generated path as a list of chunks.

   :param o: An object containing parameters for the milling operation, including
             cutter diameter, thresholds, and movement type.
   :type o: object
   :param ar: A 2D binary array representing the image to be milled.
   :type ar: np.ndarray
   :param avoidar: A 2D binary array indicating areas to avoid during milling.
   :type avoidar: np.ndarray

   :returns:

             A list of chunks representing the path taken during the milling
                 operation.
   :rtype: list


.. py:function:: image_to_chunks(o, image, with_border=False)

   Convert an image into chunks based on detected edges.

   This function processes a given image to identify edges and convert them
   into polychunks, which are essentially collections of connected edge
   segments. It utilizes the properties of the input object `o` to
   determine the boundaries and size of the chunks. The function can
   optionally include borders in the edge detection process. The output is
   a list of chunks that represent the detected polygons in the image.

   :param o: An object containing properties such as min, max, borderwidth,
             and optimisation settings.
   :type o: object
   :param image: A 2D array representing the image to be processed,
                 expected to be in a format compatible with uint8.
   :type image: np.ndarray
   :param with_border: A flag indicating whether to include borders
                       in the edge detection. Defaults to False.
   :type with_border: bool?

   :returns:

             A list of chunks, where each chunk is represented as a collection of
                 points that outline the detected edges in the image.
   :rtype: list


.. py:function:: image_to_shapely(o, i, with_border=False)

   Convert an image to Shapely polygons.

   This function takes an image and converts it into a series of Shapely
   polygon objects. It first processes the image into chunks and then
   transforms those chunks into polygon geometries. The `with_border`
   parameter allows for the inclusion of borders in the resulting polygons.

   :param o: The input image to be processed.
   :param i: Additional input parameters for processing the image.
   :param with_border: A flag indicating whether to include
                       borders in the resulting polygons. Defaults to False.
   :type with_border: bool

   :returns:

             A list of Shapely polygon objects created from the
                 image chunks.
   :rtype: list


