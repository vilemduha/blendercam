fabex.utilities.stroke_utils
============================

.. py:module:: fabex.utilities.stroke_utils


Functions
---------

.. autoapisummary::

   fabex.utilities.stroke_utils.crazy_stroke_image
   fabex.utilities.stroke_utils.crazy_stroke_image_binary
   fabex.utilities.stroke_utils.crazy_path
   fabex.utilities.stroke_utils.build_stroke
   fabex.utilities.stroke_utils.test_stroke
   fabex.utilities.stroke_utils.apply_stroke
   fabex.utilities.stroke_utils.test_stroke_binary


Module Contents
---------------

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


.. py:function:: crazy_path(o)
   :async:


   Execute a greedy adaptive algorithm for path planning.

   This function prepares an area based on the provided object `o`,
   calculates the dimensions of the area, and initializes a mill image and
   cutter array. The dimensions are determined by the maximum and minimum
   coordinates of the object, adjusted by the simulation detail and border
   width. The function is currently a stub and requires further
   implementation.

   :param o: An object containing properties such as max, min, optimisation, and
             borderwidth.
   :type o: object

   :returns: This function does not return a value.
   :rtype: None


.. py:function:: build_stroke(start, end, cutterArray)

   Build a stroke array based on start and end points.

   This function generates a 2D stroke array that represents a stroke from
   a starting point to an ending point. It calculates the length of the
   stroke and creates a grid that is filled based on the positions defined
   by the start and end coordinates. The function uses a cutter array to
   determine how the stroke interacts with the grid.

   :param start: A tuple representing the starting coordinates (x, y, z).
   :type start: tuple
   :param end: A tuple representing the ending coordinates (x, y, z).
   :type end: tuple
   :param cutterArray: An object that contains size information used to modify
                       the stroke array.

   :returns:

             A 2D array representing the stroke, filled with
                 calculated values based on the input parameters.
   :rtype: numpy.ndarray


.. py:function:: test_stroke()

.. py:function:: apply_stroke()

.. py:function:: test_stroke_binary(img, stroke)

