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
   fabex.utilities.chunk_utils.mesh_from_curve
   fabex.utilities.chunk_utils.make_visible
   fabex.utilities.chunk_utils.restore_visibility
   fabex.utilities.chunk_utils.chunks_to_shapely
   fabex.utilities.chunk_utils.set_chunks_z
   fabex.utilities.chunk_utils.rotate_point_by_point
   fabex.utilities.chunk_utils._internal_x_y_distance_to
   fabex.utilities.chunk_utils._optimize_internal
   fabex.utilities.chunk_utils.optimize_chunk
   fabex.utilities.chunk_utils.parent_child_distance
   fabex.utilities.chunk_utils.parent_child
   fabex.utilities.chunk_utils.parent_child_poly
   fabex.utilities.chunk_utils.extend_chunks_5_axis
   fabex.utilities.chunk_utils.get_closest_chunk


Module Contents
---------------

.. py:function:: chunks_refine(chunks, o)

   Add Extra Points in Between for Chunks


.. py:function:: chunks_refine_threshold(chunks, distance, limitdistance)

   Add Extra Points in Between for Chunks. for Medial Axis Strategy only!


.. py:function:: chunk_to_shapely(chunk)

.. py:function:: mesh_from_curve(o, use_modifiers=False)

.. py:function:: make_visible(o)

.. py:function:: restore_visibility(o, storage)

.. py:function:: chunks_to_shapely(chunks)

.. py:function:: set_chunks_z(chunks, z)

.. py:function:: rotate_point_by_point(originp, p, ang)

.. py:function:: _internal_x_y_distance_to(ourpoints, theirpoints, cutoff)

.. py:function:: _optimize_internal(points, keep_points, e, protect_vertical, protect_vertical_limit)

.. py:function:: optimize_chunk(chunk, operation)

.. py:function:: parent_child_distance(parents, children, o, distance=None)

.. py:function:: parent_child(parents, children, o)

.. py:function:: parent_child_poly(parents, children, o)

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


