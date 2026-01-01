fabex.operators.pack_op
=======================

.. py:module:: fabex.operators.pack_op

.. autoapi-nested-parse::

   Fabex 'ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.pack_op.CamPackObjects


Module Contents
---------------

.. py:class:: CamPackObjects

   Bases: :py:obj:`bpy.types.Operator`


   Calculate All CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.cam_pack_objects'



   .. py:attribute:: bl_label
      :value: 'Pack Curves on Sheet'



   .. py:attribute:: bl_options


   .. py:attribute:: sheet_fill_direction
      :type:  EnumProperty(name='Fill Direction', items=(('X', 'X', 'Fills sheet in X axis direction'), ('Y', 'Y', 'Fills sheet in Y axis direction')), description='Fill direction of the packer algorithm', default='Y')


   .. py:attribute:: sheet_x
      :type:  FloatProperty(name='X Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: sheet_y
      :type:  FloatProperty(name='Y Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: distance
      :type:  FloatProperty(name='Minimum Distance', description='Minimum distance between objects(should be at least cutter diameter!)', min=0.001, max=10, default=0.01, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: tolerance
      :type:  FloatProperty(name='Placement Tolerance', description='Tolerance for placement: smaller value slower placemant', min=0.001, max=0.02, default=0.005, precision=PRECISION, unit='LENGTH')


   .. py:attribute:: rotate
      :type:  BoolProperty(name='Enable Rotation', description='Enable rotation of elements', default=True)


   .. py:attribute:: rotate_angle
      :type:  FloatProperty(name='Placement Angle Rotation Step', description='Bigger rotation angle, faster placemant', default=0.19635 * 4, min=pi / 180, max=pi, precision=5, step=500, subtype='ANGLE', unit='ROTATION')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: invoke(context, event)


   .. py:method:: execute(context)

      Execute the operation in the given context.

      This function sets the Blender object mode to 'OBJECT', retrieves the
      currently selected objects, and calls the `pack_curves` function from the
      `pack` module. It is typically used to finalize operations on selected
      objects in Blender.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



   .. py:method:: draw(context)


