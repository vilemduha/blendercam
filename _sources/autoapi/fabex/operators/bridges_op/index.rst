fabex.operators.bridges_op
==========================

.. py:module:: fabex.operators.bridges_op

.. autoapi-nested-parse::

   Fabex 'bridges_op.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.bridges_op.CamBridgesAdd


Module Contents
---------------

.. py:class:: CamBridgesAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add Bridge Objects to Curve


   .. py:attribute:: bl_idname
      :value: 'scene.cam_bridges_add'



   .. py:attribute:: bl_label
      :value: 'Add Bridges / Tabs'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This function retrieves the active CAM operation from the current
      scene and adds automatic bridges to it. It is typically called within
      the context of a Blender operator to perform specific actions related to
      CAM operations.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the result of the operation, typically
                containing the key 'FINISHED' to signify successful completion.
      :rtype: dict



