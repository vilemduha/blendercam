fabex.operators.orient_op
=========================

.. py:module:: fabex.operators.orient_op

.. autoapi-nested-parse::

   Fabex 'ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.orient_op.CamOrientationAdd


Module Contents
---------------

.. py:class:: CamOrientationAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add Orientation to CAM Operation, for Multiaxis Operations


   .. py:attribute:: bl_idname
      :value: 'scene.cam_orientation_add'



   .. py:attribute:: bl_label
      :value: 'Add Orientation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM orientation operation in Blender.

      This function retrieves the active CAM operation from the current
      scene, creates an empty object to represent the CAM orientation, and
      adds it to a specified group. The empty object is named based on the
      operation's name and the current count of objects in the group. The size
      of the empty object is set to a predefined value for visibility.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    typically {'FINISHED'}.
      :rtype: dict



