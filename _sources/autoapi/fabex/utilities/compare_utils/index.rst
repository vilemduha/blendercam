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
   fabex.utilities.compare_utils.angle
   fabex.utilities.compare_utils.angle_difference
   fabex.utilities.compare_utils.point_on_line


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

   Checks if First and Last List items are Equal

   :param lst: list of points to check
   :type lst: list


.. py:function:: angle(a, b)

   Returns angle of a vector

   :param a: point a x,y coordinates
   :type a: tuple
   :param b: point b x,y coordinates
   :type b: tuple


.. py:function:: angle_difference(a, b, c)

   Returns the difference between two lines with three points

   :param a: point a x,y coordinates
   :type a: tuple
   :param b: point b x,y coordinates
   :type b: tuple
   :param c: point c x,y coordinates
   :type c: tuple


.. py:function:: point_on_line(a, b, c, tolerance)

   Determine if the angle between two vectors is within a specified
   tolerance.

   This function checks if the angle formed by two vectors, defined by
   points `b` and `c` relative to point `a`, is less than or equal to a
   given tolerance. It converts the points into vectors, calculates the dot
   product, and then computes the angle between them using the arccosine
   function. If the angle exceeds the specified tolerance, the function
   returns False; otherwise, it returns True.

   :param a: The origin point as a vector.
   :type a: np.ndarray
   :param b: The first point as a vector.
   :type b: np.ndarray
   :param c: The second point as a vector.
   :type c: np.ndarray
   :param tolerance: The maximum allowable angle (in degrees) between the vectors.
   :type tolerance: float

   :returns:

             True if the angle between vectors b and c is within the specified
                 tolerance,
                 False otherwise.
   :rtype: bool


