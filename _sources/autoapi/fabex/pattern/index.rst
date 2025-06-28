fabex.pattern
=============

.. py:module:: fabex.pattern

.. autoapi-nested-parse::

   Fabex 'pattern.py' © 2012 Vilem Novak

   Functions to read CAM path patterns and return CAM path chunks.



Functions
---------

.. autoapisummary::

   fabex.pattern.get_path_pattern_parallel
   fabex.pattern.get_path_pattern
   fabex.pattern.get_path_pattern_4_axis


Module Contents
---------------

.. py:function:: get_path_pattern_parallel(o, angle)

   Generate path chunks for parallel movement based on object dimensions
   and angle.

   This function calculates a series of path chunks for a given object,
   taking into account its dimensions and the specified angle. It utilizes
   both a traditional method and an alternative algorithm (currently
   disabled) to generate these paths. The paths are constructed by
   iterating over calculated vectors and applying transformations based on
   the object's properties. The resulting path chunks can be used for
   various movement types, including conventional and climb movements.

   :param o: An object containing properties such as dimensions and movement type.
   :type o: object
   :param angle: The angle to rotate the path generation.
   :type angle: float

   :returns:

             A list of path chunks generated based on the object's dimensions and
                 angle.
   :rtype: list


.. py:function:: get_path_pattern(operation)

   Generate a path pattern based on the specified operation strategy.

   This function constructs a path pattern for a given operation by
   analyzing its parameters and applying different strategies such as
   'PARALLEL', 'CROSS', 'BLOCK', 'SPIRAL', 'CIRCLES', and 'OUTLINEFILL'.
   Each strategy dictates how the path is built, utilizing various
   geometric calculations and conditions to ensure the path adheres to the
   specified operational constraints. The function also handles the
   orientation and direction of the path based on the movement settings
   provided in the operation.

   :param operation: An object containing parameters for path generation,
                     including strategy, movement type, and geometric bounds.
   :type operation: object

   :returns: A list of path chunks representing the generated path pattern.
   :rtype: list


.. py:function:: get_path_pattern_4_axis(operation)

   Generate path patterns for a specified operation along a rotary axis.

   This function constructs a series of path chunks based on the provided
   operation's parameters, including the rotary axis, strategy, and
   dimensions. It calculates the necessary angles and positions for the
   cutter based on the specified strategy (PARALLELR, PARALLEL, or HELIX)
   and generates the corresponding path chunks for machining operations.

   :param operation: An object containing parameters for the machining operation,
                     including min and max coordinates, rotary axis configuration,
                     distance settings, and movement strategy.
   :type operation: object

   :returns: A list of path chunks generated for the specified operation.
   :rtype: list


