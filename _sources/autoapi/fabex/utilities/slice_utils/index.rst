fabex.utilities.slice_utils
===========================

.. py:module:: fabex.utilities.slice_utils

.. autoapi-nested-parse::

   Fabex 'slice.py' © 2021 Alain Pelletier

   Very simple slicing for 3D meshes, useful for plywood cutting.
   Completely rewritten April 2021.



Functions
---------

.. autoapisummary::

   fabex.utilities.slice_utils.slicing_2d
   fabex.utilities.slice_utils.slicing_3d


Module Contents
---------------

.. py:function:: slicing_2d(ob, height)

   Slice a 3D object at a specified height and convert it to a curve.

   This function applies transformations to the given object, switches to
   edit mode, selects all vertices, and performs a bisect operation to
   slice the object at the specified height. After slicing, it resets the
   object's location and applies transformations again before converting
   the object to a curve. If the conversion fails (for instance, if the
   mesh was empty), the function deletes the mesh and returns False.
   Otherwise, it returns True.

   :param ob: The Blender object to be sliced and converted.
   :type ob: bpy.types.Object
   :param height: The height at which to slice the object.
   :type height: float

   :returns: True if the conversion to curve was successful, False otherwise.
   :rtype: bool


.. py:function:: slicing_3d(ob, start, end)

   Slice a 3D object along specified planes.

   This function applies transformations to a given object and slices it in
   the Z-axis between two specified values, `start` and `end`. It first
   ensures that the object is in edit mode and selects all vertices before
   performing the slicing operations using the `bisect` method. After
   slicing, it resets the object's location and applies the transformations
   to maintain the changes.

   :param ob: The 3D object to be sliced.
   :type ob: Object
   :param start: The starting Z-coordinate for the slice.
   :type start: float
   :param end: The ending Z-coordinate for the slice.
   :type end: float

   :returns: True if the slicing operation was successful.
   :rtype: bool


