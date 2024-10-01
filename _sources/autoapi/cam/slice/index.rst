cam.slice
=========

.. py:module:: cam.slice

.. autoapi-nested-parse::

   BlenderCAM 'slice.py' © 2021 Alain Pelletier

   Very simple slicing for 3D meshes, useful for plywood cutting.
   Completely rewritten April 2021.



Classes
-------

.. autoapisummary::

   cam.slice.SliceObjectsSettings


Functions
---------

.. autoapisummary::

   cam.slice.slicing2d
   cam.slice.slicing3d
   cam.slice.sliceObject


Module Contents
---------------

.. py:function:: slicing2d(ob, height)

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


.. py:function:: slicing3d(ob, start, end)

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


.. py:function:: sliceObject(ob)

   Slice a 3D object into layers based on a specified thickness.

   This function takes a 3D object and slices it into multiple layers
   according to the specified thickness. It creates a new collection for
   the slices and optionally creates text labels for each slice if the
   indexes parameter is set. The slicing can be done in either 2D or 3D
   based on the user's selection. The function also handles the positioning
   of the slices based on the object's bounding box.

   :param ob: The 3D object to be sliced.
   :type ob: bpy.types.Object


.. py:class:: SliceObjectsSettings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   Stores All Data for Machines


   .. py:attribute:: slice_distance
      :type:  FloatProperty(name='Slicing Distance', description='Slices distance in z, should be most often thickness of plywood sheet.', min=0.001, max=10, default=0.005, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: slice_above0
      :type:  BoolProperty(name='Slice Above 0', description='only slice model above 0', default=False)


   .. py:attribute:: slice_3d
      :type:  BoolProperty(name='3D Slice', description='For 3D carving', default=False)


   .. py:attribute:: indexes
      :type:  BoolProperty(name='Add Indexes', description='Adds index text of layer + index', default=True)


