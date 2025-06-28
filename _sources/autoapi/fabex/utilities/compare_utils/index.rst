fabex.utilities.compare_utils
=============================

.. py:module:: fabex.utilities.compare_utils

.. autoapi-nested-parse::

   Fabex 'compare_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.compare_utils.compare_z_level
   fabex.utilities.compare_utils.overlaps
   fabex.utilities.compare_utils.get_vector_right
   fabex.utilities.compare_utils.unique
   fabex.utilities.compare_utils.check_equal


Module Contents
---------------

.. py:function:: compare_z_level(x)

.. py:function:: overlaps(bb1, bb2)

   Determine if one bounding box is a child of another.

   This function checks if the first bounding box (bb1) is completely
   contained within the second bounding box (bb2). It does this by
   comparing the coordinates of both bounding boxes to see if all corners
   of bb1 are within the bounds of bb2.

   :param bb1: A tuple representing the coordinates of the first bounding box
               in the format (x_min, y_min, x_max, y_max).
   :type bb1: tuple
   :param bb2: A tuple representing the coordinates of the second bounding box
               in the format (x_min, y_min, x_max, y_max).
   :type bb2: tuple

   :returns: True if bb1 is a child of bb2, otherwise False.
   :rtype: bool


.. py:function:: get_vector_right(lastv, verts)

   Get the index of the vector that is most to the right based on angle.

   This function calculates the angle between a reference vector (formed by
   the last two vectors in `lastv`) and each vector in the `verts` list. It
   identifies the vector that has the smallest angle with respect to the
   reference vector, indicating that it is the most rightward vector in
   relation to the specified direction.

   :param lastv: A list containing two vectors, where each vector is
                 represented as a tuple or list of coordinates.
   :type lastv: list
   :param verts: A list of vectors represented as tuples or lists of
                 coordinates.
   :type verts: list

   :returns:

             The index of the vector in `verts` that is most to the right
                 based on the calculated angle.
   :rtype: int


.. py:function:: unique(L)

   Return a list of unhashable elements in L, but without duplicates.

   This function processes a list of lists, specifically designed to handle
   unhashable elements. It sorts the input list and removes duplicates by
   comparing the elements based on their coordinates. The function counts
   the number of duplicate vertices and the number of collinear points
   along the Z-axis.

   :param L: A list of lists, where each inner list represents a point
   :type L: list

   :returns:

             A tuple containing two integers:
                 - The first integer represents the count of duplicate vertices.
                 - The second integer represents the count of Z-collinear points.
   :rtype: tuple


.. py:function:: check_equal(lst)

