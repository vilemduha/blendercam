fabex.operators.path_ops
========================

.. py:module:: fabex.operators.path_ops

.. autoapi-nested-parse::

   Fabex 'ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.operators.path_ops.PathsBackground
   fabex.operators.path_ops.KillPathsBackground
   fabex.operators.path_ops.CalculatePath
   fabex.operators.path_ops.PathsAll
   fabex.operators.path_ops.PathsChain
   fabex.operators.path_ops.PathExportChain
   fabex.operators.path_ops.PathExport


Functions
---------

.. autoapisummary::

   fabex.operators.path_ops._calc_path


Module Contents
---------------

.. py:class:: PathsBackground

   Bases: :py:obj:`bpy.types.Operator`


   Calculate CAM Paths in Background. File Has to Be Saved Before.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_background'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Background'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the CAM operation in the background.

      This method initiates a background process to perform CAM operations
      based on the current scene and active CAM operation. It sets up the
      necessary paths for the script and starts a subprocess to handle the
      CAM computations. Additionally, it manages threading to ensure that
      the main thread remains responsive while the background operation is
      executed.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



.. py:class:: KillPathsBackground

   Bases: :py:obj:`bpy.types.Operator`


   Remove CAM Path Processes in Background.


   .. py:attribute:: bl_idname
      :value: 'object.kill_calculate_cam_paths_background'



   .. py:attribute:: bl_label
      :value: 'Kill Background Computation of an Operation'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the CAM operation in the given context.

      This method retrieves the active CAM operation from the scene and
      checks if there are any ongoing processes related to CAM path
      calculations. If such processes exist and match the current operation,
      they are terminated. The method then marks the operation as not
      computing and returns a status indicating that the execution has
      finished.

      :param context: The context in which the operation is executed.

      :returns: A dictionary with a status key indicating the result of the execution.
      :rtype: dict



.. py:function:: _calc_path(operator, context)
   :async:


   Calculate the path for a given operator and context.

   This function processes the current scene's CAM operations based on
   the specified operator and context. It handles different geometry
   sources, checks for valid operation parameters, and manages the
   visibility of objects and collections. The function also retrieves the
   path using an asynchronous operation and handles any exceptions that may
   arise during this process. If the operation is invalid or if certain
   conditions are not met, appropriate error messages are reported to the
   operator.

   :param operator: The operator that initiated the path calculation.
   :type operator: bpy.types.Operator
   :param context: The context in which the operation is executed.
   :type context: bpy.types.Context

   :returns:

             A tuple indicating the status of the operation.
                 Returns {'FINISHED', True} if successful,
                 {'FINISHED', False} if there was an error,
                 or {'CANCELLED', False} if the operation was cancelled.
   :rtype: tuple


.. py:class:: CalculatePath(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Calculate CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_path'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check if the current CAM operation is valid.

      This method checks the active CAM operation in the given context and
      determines if it is valid. It retrieves the active operation from the
      scene's CAM operations and validates it using the `isValid` function.
      If the operation is valid, it returns True; otherwise, it returns False.

      :param context: The context containing the scene and CAM operations.
      :type context: Context

      :returns: True if the active CAM operation is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous calculation of a path.

      This method performs an asynchronous operation to calculate a path based
      on the provided context. It awaits the result of the calculation and
      prints the success status along with the return value. The return value
      can be used for further processing or analysis.

      :param context: The context in which the path calculation is to be executed.
      :type context: Any

      :returns: The result of the path calculation.
      :rtype: Any



.. py:class:: PathsAll

   Bases: :py:obj:`bpy.types.Operator`


   Calculate All CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_all'



   .. py:attribute:: bl_label
      :value: 'Calculate All CAM Paths'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute CAM operations in the current Blender context.

      This function iterates through the CAM operations defined in the
      current scene and executes the background calculation for each
      operation. It sets the active CAM operation index and prints the name
      of each operation being processed. This is typically used in a Blender
      add-on or script to automate CAM path calculations.

      :param context: The current Blender context.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



   .. py:method:: draw(context)

      Draws the user interface elements for the operation selection.

      This method utilizes the Blender layout system to create a property
      search interface for selecting operations related to CAM
      functionalities. It links the current instance's operation property to
      the available CAM operations defined in the Blender scene.

      :param context: The context in which the drawing occurs,
      :type context: bpy.context



.. py:class:: PathsChain(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`fabex.operators.async_op.AsyncOperatorMixin`


   Calculate a Chain and Export the G-code Alltogether.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_chain'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Current Chain and Export Chain G-code'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active CAM chain in the given context.

      This method retrieves the active CAM chain from the scene and checks
      its validity using the `isChainValid` function. It returns a boolean
      value indicating whether the CAM chain is valid or not.

      :param context: The context containing the scene and CAM chain information.
      :type context: Context

      :returns: True if the active CAM chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute_async(context)
      :async:


      Execute asynchronous operations for CAM path calculations.

      This method sets the object mode for the Blender scene and processes a
      series of CAM operations defined in the active CAM chain. It
      reports the progress of each operation and handles any exceptions that
      may occur during the path calculation. After successful calculations, it
      exports the resulting mesh data to a specified G-code file.

      :param context: The Blender context containing scene and
      :type context: bpy.context

      :returns: A dictionary indicating the result of the operation,
                typically {'FINISHED'}.
      :rtype: dict



.. py:class:: PathExportChain

   Bases: :py:obj:`bpy.types.Operator`


   Calculate a Chain and Export the G-code Together.


   .. py:attribute:: bl_idname
      :value: 'object.cam_export_paths_chain'



   .. py:attribute:: bl_label
      :value: 'Export CAM Paths in Current Chain as G-code'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active CAM chain in the given context.

      This method retrieves the currently active CAM chain from the scene
      context and checks its validity using the `isChainValid` function. It
      returns a boolean indicating whether the active CAM chain is valid or
      not.

      :param context: The context containing the scene and CAM chain information.
      :type context: object

      :returns: True if the active CAM chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute(context)

      Execute the CAM path export process.

      This function retrieves the active CAM chain from the current scene
      and gathers the mesh data associated with the operations of that chain.
      It then exports the G-code path using the specified filename and the
      collected mesh data. The function is designed to be called within the
      context of a Blender operator.

      :param context: The context in which the operator is executed.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: PathExport

   Bases: :py:obj:`bpy.types.Operator`


   Export G-code. Can Be Used only when the Path Object Is Present


   .. py:attribute:: bl_idname
      :value: 'object.cam_export'



   .. py:attribute:: bl_label
      :value: 'Export Operation G-code'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the CAM operation and export the G-code path.

      This method retrieves the active CAM operation from the current scene
      and exports the corresponding G-code path to a specified filename. It
      prints the filename and relevant operation details to the console for
      debugging purposes. The G-code path is generated based on the CAM
      path data associated with the active operation.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



