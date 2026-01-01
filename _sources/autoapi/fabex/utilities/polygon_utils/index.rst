fabex.utilities.polygon_utils
=============================

.. py:module:: fabex.utilities.polygon_utils


Functions
---------

.. autoapisummary::

   fabex.utilities.polygon_utils.polygon_boolean
   fabex.utilities.polygon_utils.polygon_convex_hull


Module Contents
---------------

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


