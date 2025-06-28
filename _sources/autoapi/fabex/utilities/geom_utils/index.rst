fabex.utilities.geom_utils
==========================

.. py:module:: fabex.utilities.geom_utils

.. autoapi-nested-parse::

   Fabex 'geom_utils.py' © 2012 Vilem Novak

   Main functionality of Fabex.
   The functions here are called with operators defined in 'ops.py'



Classes
-------

.. autoapisummary::

   fabex.utilities.geom_utils.Point


Functions
---------

.. autoapisummary::

   fabex.utilities.geom_utils.circle
   fabex.utilities.geom_utils.helix
   fabex.utilities.geom_utils.get_container
   fabex.utilities.geom_utils.triangle
   fabex.utilities.geom_utils.s_sine


Module Contents
---------------

.. py:function:: circle(r, np)

   Generate a circle defined by a given radius and number of points.

   This function creates a polygon representing a circle by generating a
   list of points based on the specified radius and the number of points
   (np). It uses vector rotation to calculate the coordinates of each point
   around the circle. The resulting points are then used to create a
   polygon object.

   :param r: The radius of the circle.
   :type r: float
   :param np: The number of points to generate around the circle.
   :type np: int

   :returns: A polygon object representing the circle.
   :rtype: spolygon.Polygon


.. py:function:: helix(r, np, zstart, pend, rev)

   Generate a helix of points in 3D space.

   This function calculates a series of points that form a helix based on
   the specified parameters. It starts from a given radius and
   z-coordinate, and generates points by rotating around the z-axis while
   moving linearly along the z-axis. The number of points generated is
   determined by the number of turns (revolutions) and the number of points
   per revolution.

   :param r: The radius of the helix.
   :type r: float
   :param np: The number of points per revolution.
   :type np: int
   :param zstart: The starting z-coordinate for the helix.
   :type zstart: float
   :param pend: A tuple containing the x, y, and z coordinates of the endpoint.
   :type pend: tuple
   :param rev: The number of revolutions to complete.
   :type rev: int

   :returns:

             A list of tuples representing the coordinates of the points in the
                 helix.
   :rtype: list


.. py:function:: get_container()

   Get or create a container object for CAM objects.

   This function checks if a container object named 'CAM_OBJECTS' exists in
   the current Blender scene. If it does not exist, the function creates a
   new empty object of type 'PLAIN_AXES', names it 'CAM_OBJECTS', and sets
   its location to the origin (0, 0, 0). The newly created container is
   also hidden. If the container already exists, it simply retrieves and
   returns that object.

   :returns:

             The container object for CAM objects, either newly created or
                 existing.
   :rtype: bpy.types.Object


.. py:class:: Point(x, y, z)

.. py:function:: triangle(i, T, A)

.. py:function:: s_sine(A, T, dc_offset=0, phase_shift=0)

