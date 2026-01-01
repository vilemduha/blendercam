fabex.operators.chain_ops
=========================

.. py:module:: fabex.operators.chain_ops

.. autoapi-nested-parse::

   Fabex 'ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.chain_ops.CamChainAdd
   fabex.operators.chain_ops.CamChainRemove
   fabex.operators.chain_ops.CamChainOperationAdd
   fabex.operators.chain_ops.CamChainOperationUp
   fabex.operators.chain_ops.CamChainOperationDown
   fabex.operators.chain_ops.CamChainOperationRemove


Module Contents
---------------

.. py:class:: CamChainAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add New CAM Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_add'



   .. py:attribute:: bl_label
      :value: 'Add New CAM Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM chain creation in the given context.

      This function adds a new CAM chain to the current scene in Blender.
      It updates the active CAM chain index and assigns a name and filename
      to the newly created chain. The function is intended to be called within
      a Blender operator context.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    specifically returning {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamChainRemove

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_remove'



   .. py:attribute:: bl_label
      :value: 'Remove CAM Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM chain removal process.

      This function removes the currently active CAM chain from the scene
      and decrements the active CAM chain index if it is greater than zero.
      It modifies the Blender context to reflect these changes.

      :param context: The context in which the function is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    specifically {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamChainOperationAdd

   Bases: :py:obj:`bpy.types.Operator`


   Add Operation to Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_add'



   .. py:attribute:: bl_label
      :value: 'Add Operation to Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute an operation in the active CAM chain.

      This function retrieves the active CAM chain from the current scene
      and adds a new operation to it. It increments the active operation index
      and assigns the name of the currently selected CAM operation to the
      newly added operation. This is typically used in the context of managing
      CAM operations in a 3D environment.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the execution status, typically {'FINISHED'}.
      :rtype: dict



.. py:class:: CamChainOperationUp

   Bases: :py:obj:`bpy.types.Operator`


   Add Operation to Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_up'



   .. py:attribute:: bl_label
      :value: 'Add Operation to Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the operation to move the active CAM operation in the chain.

      This function retrieves the current scene and the active CAM chain.
      If there is an active operation (i.e., its index is greater than 0), it
      moves the operation one step up in the chain by adjusting the indices
      accordingly. After moving the operation, it updates the active operation
      index to reflect the change.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    specifically returning {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamChainOperationDown

   Bases: :py:obj:`bpy.types.Operator`


   Add Operation to Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_down'



   .. py:attribute:: bl_label
      :value: 'Add Operation to Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the operation to move the active CAM operation in the chain.

      This function retrieves the current scene and the active CAM chain.
      It checks if the active operation can be moved down in the list of
      operations. If so, it moves the active operation one position down and
      updates the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    specifically {'FINISHED'} when the operation completes successfully.
      :rtype: dict



.. py:class:: CamChainOperationRemove

   Bases: :py:obj:`bpy.types.Operator`


   Remove Operation from Chain


   .. py:attribute:: bl_idname
      :value: 'scene.cam_chain_operation_remove'



   .. py:attribute:: bl_label
      :value: 'Remove Operation from Chain'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the operation to remove the active operation from the CAM
      chain.

      This method accesses the current scene and retrieves the active CAM
      chain. It then removes the currently active operation from that chain
      and adjusts the index of the active operation accordingly. If the active
      operation index becomes negative, it resets it to zero to ensure it
      remains within valid bounds.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the execution status, typically
                    containing {'FINISHED'} upon successful completion.
      :rtype: dict



