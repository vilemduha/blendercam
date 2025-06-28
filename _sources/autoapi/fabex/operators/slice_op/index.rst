fabex.operators.slice_op
========================

.. py:module:: fabex.operators.slice_op

.. autoapi-nested-parse::

   Fabex 'slice_op.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.slice_op.CamSliceObjects


Module Contents
---------------

.. py:class:: CamSliceObjects

   Bases: :py:obj:`bpy.types.Operator`


   Slice a Mesh Object Horizontally


   .. py:attribute:: bl_idname
      :value: 'object.cam_slice_objects'



   .. py:attribute:: bl_label
      :value: 'Slice Object - Useful for Lasercut Puzzles etc'



   .. py:attribute:: bl_options


   .. py:attribute:: slice_distance
      :type:  FloatProperty(name='Slicing Distance', description='Slices distance in z, should be most often thickness of plywood sheet.', min=0.001, max=10, default=0.005, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: slice_above_0
      :type:  BoolProperty(name='Slice Above 0', description='only slice model above 0', default=False)


   .. py:attribute:: slice_3d
      :type:  BoolProperty(name='3D Slice', description='For 3D carving', default=False)


   .. py:attribute:: indexes
      :type:  BoolProperty(name='Add Indexes', description='Adds index text of layer + index', default=True)


   .. py:method:: invoke(context, event)


   .. py:method:: execute(context)

      Slice a 3D object into layers based on a specified thickness.

      This function takes a 3D object and slices it into multiple layers
      according to the specified thickness. It creates a new collection for
      the slices and optionally creates text labels for each slice if the
      indexes parameter is set. The slicing can be done in either 2D or 3D
      based on the user's selection. The function also handles the positioning
      of the slices based on the object's bounding box.

      :param ob: The 3D object to be sliced.
      :type ob: bpy.types.Object



   .. py:method:: draw(context)


