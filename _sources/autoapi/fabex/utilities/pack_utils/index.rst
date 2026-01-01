fabex.utilities.pack_utils
==========================

.. py:module:: fabex.utilities.pack_utils

.. autoapi-nested-parse::

   Fabex 'pack.py' © 2012 Vilem Novak

   Takes all selected curves, converts them to polygons, offsets them by the pre-set margin
   then chooses a starting location possibly inside the already occupied area and moves and rotates the
   polygon out of the occupied area if one or more positions are found where the poly doesn't overlap,
   it is placed and added to the occupied area - allpoly
   Very slow and STUPID, a collision algorithm would be much much faster...



Functions
---------

.. autoapisummary::

   fabex.utilities.pack_utils.s_rotate
   fabex.utilities.pack_utils.pack_curves


Module Contents
---------------

.. py:function:: s_rotate(s, r, x, y)

   Rotate a polygon's coordinates around a specified point.

   This function takes a polygon and rotates its exterior coordinates
   around a given point (x, y) by a specified angle (r) in radians. It uses
   the Euler rotation to compute the new coordinates for each point in the
   polygon's exterior. The resulting coordinates are then used to create a
   new polygon.

   :param s: The polygon to be rotated.
   :type s: shapely.geometry.Polygon
   :param r: The angle of rotation in radians.
   :type r: float
   :param x: The x-coordinate of the point around which to rotate.
   :type x: float
   :param y: The y-coordinate of the point around which to rotate.
   :type y: float

   :returns: A new polygon with the rotated coordinates.
   :rtype: shapely.geometry.Polygon


.. py:function:: pack_curves()

   Pack selected curves into a defined area based on specified settings.

   This function organizes selected curve objects in Blender by packing
   them into a specified area defined by the CAM pack settings. It
   calculates the optimal positions for each curve while considering
   parameters such as sheet size, fill direction, distance, tolerance, and
   rotation. The function utilizes geometric operations to ensure that the
   curves do not overlap and fit within the defined boundaries. The packed
   curves are then transformed and their properties are updated
   accordingly.  The function performs the following steps: 1. Activates
   speedup features if available. 2. Retrieves packing settings from the
   current scene. 3. Processes each selected object to create polygons from
   curves. 4. Attempts to place each polygon within the defined area while
   avoiding    overlaps and respecting the specified fill direction. 5.
   Outputs the final arrangement of polygons.


