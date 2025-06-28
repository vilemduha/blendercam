fabex.operators.simulation_ops
==============================

.. py:module:: fabex.operators.simulation_ops

.. autoapi-nested-parse::

   Fabex 'simulation_ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.simulation_ops.CAMSimulate
   fabex.operators.simulation_ops.CAMSimulateChain


Module Contents
---------------

.. py:class:: CAMSimulate(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Simulate CAM Operation
   This Is Performed by: Creating an Image, Painting Z Depth of the Brush Subtractively.
   Works only for Some Operations, Can Not Be Used for 4-5 Axis.


   .. py:attribute:: bl_idname
      :value: 'object.cam_simulate'



   .. py:attribute:: bl_label
      :value: 'CAM Simulation'



   .. py:attribute:: bl_options


   .. py:attribute:: operation
      :type:  StringProperty(name='Operation', description='Specify the operation to calculate', default='Operation')


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous simulation operation based on the active CAM
      operation.

      This method retrieves the current scene and the active CAM operation.
      It constructs the operation name and checks if the corresponding object
      exists in the Blender data. If it does, it attempts to run the
      simulation asynchronously. If the simulation is cancelled, it returns a
      cancellation status. If the object does not exist, it reports an error
      and returns a finished status.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the status of the operation, either
                    {'CANCELLED'} or {'FINISHED'}.
      :rtype: dict



   .. py:method:: draw(context)

      Draws the user interface for selecting CAM operations.

      This method creates a layout element in the user interface that allows
      users to search and select a specific CAM operation from a list of
      available operations defined in the current scene. It utilizes the
      Blender Python API to integrate with the UI.

      :param context: The context in which the drawing occurs, typically
                      provided by Blender's UI system.



.. py:class:: CAMSimulateChain(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Simulate CAM Chain, Compared to Single Op Simulation Just Writes Into One Image and Thus Enables
   to See how Ops Work Together.


   .. py:attribute:: bl_idname
      :value: 'object.cam_simulate_chain'



   .. py:attribute:: bl_label
      :value: 'CAM Simulation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active CAM chain in the scene.

      This method retrieves the currently active CAM chain from the scene's
      CAM chains and checks its validity using the `isChainValid` function.
      It returns a boolean indicating whether the active CAM chain is
      valid.

      :param context: The context containing the scene and its properties.
      :type context: object

      :returns: True if the active CAM chain is valid, False otherwise.
      :rtype: bool



   .. py:attribute:: operation
      :type:  StringProperty(name='Operation', description='Specify the operation to calculate', default='Operation')


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous simulation for a specified CAM chain.

      This method retrieves the active CAM chain from the current Blender
      scene and determines the operations associated with that chain. It
      checks if all operations are valid and can be simulated. If valid, it
      proceeds to execute the simulation asynchronously. If any operation is
      invalid, it logs a message and returns a finished status without
      performing the

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the status of the operation, either
                operation completed successfully.
      :rtype: dict



   .. py:method:: draw(context)

      Draw the user interface for selecting CAM operations.

      This function creates a user interface element that allows the user to
      search and select a specific CAM operation from a list of available
      operations in the current scene. It utilizes the Blender Python API to
      create a property search layout.

      :param context: The context in which the drawing occurs, typically containing
                      information about the current scene and UI elements.



