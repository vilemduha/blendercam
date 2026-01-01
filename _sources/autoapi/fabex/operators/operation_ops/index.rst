fabex.operators.operation_ops
=============================

.. py:module:: fabex.operators.operation_ops

.. autoapi-nested-parse::

   Fabex 'operation_ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.operation_ops.CamOperationAdd
   fabex.operators.operation_ops.CamOperationCopy
   fabex.operators.operation_ops.CamOperationRemove
   fabex.operators.operation_ops.CamOperationMove


Module Contents
---------------

.. py:class:: CamOperationAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add New CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_add'



   .. py:attribute:: bl_label
      :value: 'Add New CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation based on the active object in the scene.

      This method retrieves the active object from the Blender context and
      performs operations related to CAM settings. It checks if an object
      is selected and retrieves its bounding box dimensions. If no object is
      found, it reports an error and cancels the operation. If an object is
      present, it adds a new CAM operation to the scene, sets its
      properties, and ensures that a machine area object is present.

      :param context: The context in which the operation is executed.



.. py:class:: CamOperationCopy

   Bases: :py:obj:`bpy.types.Operator`


   Copy CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_copy'



   .. py:attribute:: bl_label
      :value: 'Copy Active CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This method handles the execution of CAM operations within the
      Blender scene. It first checks if there are any CAM operations
      available. If not, it returns a cancellation status. If there are
      operations, it copies the active operation, increments the active
      operation index, and updates the name and filename of the new operation.
      The function also ensures that the new operation's name is unique by
      appending a copy suffix or incrementing a numeric suffix.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    either {'CANCELLED'} if no operations are available or
                    {'FINISHED'} if the operation was successfully executed.
      :rtype: dict



.. py:class:: CamOperationRemove

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_remove'



   .. py:attribute:: bl_label
      :value: 'Remove CAM Operation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This function performs the active CAM operation by deleting the
      associated object from the scene. It checks if there are any CAM
      operations available and handles the deletion of the active operation's
      object. If the active operation is removed, it updates the active
      operation index accordingly. Additionally, it manages a dictionary that
      tracks hidden objects.

      :param context: The Blender context containing the scene and operations.
      :type context: bpy.context

      :returns:

                A dictionary indicating the result of the operation, either
                    {'CANCELLED'} if no operations are available or {'FINISHED'} if the
                    operation was successfully executed.
      :rtype: dict



.. py:class:: CamOperationMove

   Bases: :py:obj:`bpy.types.Operator`


   Move CAM Operation


   .. py:attribute:: bl_idname
      :value: 'scene.cam_operation_move'



   .. py:attribute:: bl_label
      :value: 'Move CAM Operation in List'



   .. py:attribute:: bl_options


   .. py:attribute:: direction
      :type:  EnumProperty(name='Direction', items=(('UP', 'Up', ''), ('DOWN', 'Down', '')), description='Direction', default='DOWN')


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute a CAM operation based on the specified direction.

      This method modifies the active CAM operation in the Blender context
      based on the direction specified. If the direction is 'UP', it moves the
      active operation up in the list, provided it is not already at the top.
      Conversely, if the direction is not 'UP', it moves the active operation
      down in the list, as long as it is not at the bottom. The method updates
      the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the operation has finished, with
                the key 'FINISHED'.
      :rtype: dict



