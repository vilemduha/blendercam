fabex.utilities.chunk_utils
===========================

.. py:module:: fabex.utilities.chunk_utils

.. autoapi-nested-parse::

   Fabex 'chunk_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.chunk_utils.chunks_refine
   fabex.utilities.chunk_utils.chunks_refine_threshold
   fabex.utilities.chunk_utils.chunk_to_shapely
   fabex.utilities.chunk_utils.set_chunks_z
   fabex.utilities.chunk_utils.optimize_chunk
   fabex.utilities.chunk_utils.extend_chunks_5_axis
   fabex.utilities.chunk_utils.get_closest_chunk
   fabex.utilities.chunk_utils.chunks_coherency
   fabex.utilities.chunk_utils.limit_chunks
   fabex.utilities.chunk_utils.sample_chunks_n_axis
   fabex.utilities.chunk_utils.sample_path_low
   fabex.utilities.chunk_utils.sample_chunks
   fabex.utilities.chunk_utils.connect_chunks_low
   fabex.utilities.chunk_utils.sort_chunks
   fabex.utilities.chunk_utils.chunks_to_mesh


Module Contents
---------------

.. py:function:: chunks_refine(chunks, o)

   Add Extra Points in Between for Chunks


.. py:function:: chunks_refine_threshold(chunks, distance, limitdistance)

   Add Extra Points in Between for Chunks. for Medial Axis Strategy only!


.. py:function:: chunk_to_shapely(chunk)

   Converts CAM path chunks into Shapely Polygon

   This function takes a CAM path chunk, uses the chunk points
   to create a Shapely Polygon, and returns the Polygon.


.. py:function:: set_chunks_z(chunks, z)

   Sets the Depth of CAM path chunks

   This function takes a group of CAM path chunks, and a depth
   setting, creates copies of the chunks, assigns the depth
   value and then returns the copied chunks as a new list.


.. py:function:: optimize_chunk(chunk, operation)

.. py:function:: extend_chunks_5_axis(chunks, o)

   Extend chunks with 5-axis cutter start and end points.

   This function modifies the provided chunks by appending calculated start
   and end points for a cutter based on the specified orientation and
   movement parameters. It determines the starting position of the cutter
   based on the machine's settings and the object's movement constraints.
   The function iterates through each point in the chunks and updates their
   start and end points accordingly.

   :param chunks: A list of chunk objects that will be modified.
   :type chunks: list
   :param o: An object containing movement and orientation data.
   :type o: object


.. py:function:: get_closest_chunk(o, pos, chunks)

   Find the closest chunk to a given position.

   This function iterates through a list of chunks and determines which
   chunk is closest to the specified position. It checks if each chunk's
   children are sorted before calculating the distance. The chunk with the
   minimum distance to the given position is returned.

   :param o: An object representing the origin point.
   :param pos: A position to which the closest chunk is calculated.
   :param chunks: A list of chunk objects to evaluate.
   :type chunks: list

   :returns:

             The closest chunk object to the specified position, or None if no valid
                 chunk is found.
   :rtype: Chunk


.. py:function:: chunks_coherency(chunks)

   Checks CAM path chunks for Stability for Pencil path

   This function checks if the vectors direction doesn't change too quickly,
   if this happens it splits the chunk at that point, and if the change is too great
   the chunk will be deleted. This prevents the router/spindle from slowing down too
   much, but also means that some parts detected by cavity algorithm won't be milled.


.. py:function:: limit_chunks(chunks, o, force=False)

   Prevent excluded CAM path chunks from being Processed

   This function checks if there are limitations on the area to be
   milled, like limit curves, and rebuilds the chunk list without the
   excluded chunks.


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


.. py:function:: chunks_to_mesh(chunks, o)

   Convert sampled chunks into a mesh path for a given optimization object.

   This function takes a list of sampled chunks and converts them into a
   mesh path based on the specified optimization parameters. It handles
   different machine axes configurations and applies optimizations as
   needed. The resulting mesh is created in the Blender context, and the
   function also manages the lifting and dropping of the cutter based on
   the chunk positions.

   :param chunks: A list of chunk objects to be converted into a mesh.
   :type chunks: list
   :param o: An object containing optimization parameters and settings.
   :type o: object

   :returns:

             The function creates a mesh in the Blender context but does not return a
                 value.
   :rtype: None


