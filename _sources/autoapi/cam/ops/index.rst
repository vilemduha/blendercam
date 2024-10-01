cam.ops
=======

.. py:module:: cam.ops

.. autoapi-nested-parse::

   BlenderCAM 'ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   cam.ops.threadCom
   cam.ops.PathsBackground
   cam.ops.KillPathsBackground
   cam.ops.CalculatePath
   cam.ops.PathsAll
   cam.ops.CamPackObjects
   cam.ops.CamSliceObjects
   cam.ops.PathsChain
   cam.ops.PathExportChain
   cam.ops.PathExport
   cam.ops.CAMSimulate
   cam.ops.CAMSimulateChain
   cam.ops.CamChainAdd
   cam.ops.CamChainRemove
   cam.ops.CamChainOperationAdd
   cam.ops.CamChainOperationUp
   cam.ops.CamChainOperationDown
   cam.ops.CamChainOperationRemove
   cam.ops.CamOperationAdd
   cam.ops.CamOperationCopy
   cam.ops.CamOperationRemove
   cam.ops.CamOperationMove
   cam.ops.CamOrientationAdd
   cam.ops.CamBridgesAdd


Functions
---------

.. autoapisummary::

   cam.ops.threadread
   cam.ops.timer_update
   cam.ops._calc_path
   cam.ops.getChainOperations
   cam.ops.fixUnits


Module Contents
---------------

.. py:class:: threadCom(o, proc)

   .. py:attribute:: opname


   .. py:attribute:: outtext
      :value: ''



   .. py:attribute:: proc


   .. py:attribute:: lasttext
      :value: ''



.. py:function:: threadread(tcom)

   Reads the standard output of a background process in a non-blocking
   manner.

   This function reads a line from the standard output of a background
   process associated with the provided `tcom` object. It searches for a
   specific substring that indicates progress information, and if found,
   extracts that information and assigns it to the `outtext` attribute of
   the `tcom` object. This allows for real-time monitoring of the
   background process's output without blocking the main thread.

   :param tcom: An object that has a `proc` attribute with a `stdout`
                stream from which to read the output.
   :type tcom: object

   :returns:

             This function does not return a value; it modifies the `tcom`
                 object in place.
   :rtype: None


.. py:function:: timer_update(context)

   Monitor background processes related to camera path calculations.

   This function checks the status of background processes that are
   responsible for calculating camera paths. It retrieves the current
   processes and monitors their state. If a process has finished, it
   updates the corresponding camera operation and reloads the necessary
   paths. If the process is still running, it restarts the associated
   thread to continue monitoring.

   :param context: The context in which the function is called, typically
                   containing information about the current scene and operations.


.. py:class:: PathsBackground

   Bases: :py:obj:`bpy.types.Operator`


   Calculate CAM Paths in Background. File Has to Be Saved Before.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_background'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Background'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the camera operation in the background.

      This method initiates a background process to perform camera operations
      based on the current scene and active camera operation. It sets up the
      necessary paths for the script and starts a subprocess to handle the
      camera computations. Additionally, it manages threading to ensure that
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

      Execute the camera operation in the given context.

      This method retrieves the active camera operation from the scene and
      checks if there are any ongoing processes related to camera path
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

   This function processes the current scene's camera operations based on
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


.. py:class:: CalculatePath

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


   Calculate CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_path'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check if the current camera operation is valid.

      This method checks the active camera operation in the given context and
      determines if it is valid. It retrieves the active operation from the
      scene's camera operations and validates it using the `isValid` function.
      If the operation is valid, it returns True; otherwise, it returns False.

      :param context: The context containing the scene and camera operations.
      :type context: Context

      :returns: True if the active camera operation is valid, False otherwise.
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

      Execute camera operations in the current Blender context.

      This function iterates through the camera operations defined in the
      current scene and executes the background calculation for each
      operation. It sets the active camera operation index and prints the name
      of each operation being processed. This is typically used in a Blender
      add-on or script to automate camera path calculations.

      :param context: The current Blender context.
      :type context: bpy.context

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



   .. py:method:: draw(context)

      Draws the user interface elements for the operation selection.

      This method utilizes the Blender layout system to create a property
      search interface for selecting operations related to camera
      functionalities. It links the current instance's operation property to
      the available camera operations defined in the Blender scene.

      :param context: The context in which the drawing occurs,
      :type context: bpy.context



.. py:class:: CamPackObjects

   Bases: :py:obj:`bpy.types.Operator`


   Calculate All CAM Paths


   .. py:attribute:: bl_idname
      :value: 'object.cam_pack_objects'



   .. py:attribute:: bl_label
      :value: 'Pack Curves on Sheet'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the operation in the given context.

      This function sets the Blender object mode to 'OBJECT', retrieves the
      currently selected objects, and calls the `packCurves` function from the
      `pack` module. It is typically used to finalize operations on selected
      objects in Blender.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the completion status of the operation.
      :rtype: dict



   .. py:method:: draw(context)


.. py:class:: CamSliceObjects

   Bases: :py:obj:`bpy.types.Operator`


   Slice a Mesh Object Horizontally


   .. py:attribute:: bl_idname
      :value: 'object.cam_slice_objects'



   .. py:attribute:: bl_label
      :value: 'Slice Object - Useful for Lasercut Puzzles etc'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)

      Execute the slicing operation on the active Blender object.

      This function retrieves the currently active object in the Blender
      context and performs a slicing operation on it using the `sliceObject`
      function from the `cam` module. The operation is intended to modify the
      object based on the slicing logic defined in the external module.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the result of the operation,
                    typically containing the key 'FINISHED' upon successful execution.
      :rtype: dict



   .. py:method:: draw(context)


.. py:function:: getChainOperations(chain)

   Return chain operations associated with a given chain object.

   This function iterates through the operations of the provided chain
   object and retrieves the corresponding operations from the current
   scene's camera operations in Blender. Due to limitations in Blender,
   chain objects cannot store operations directly, so this function serves
   to extract and return the relevant operations for further processing.

   :param chain: The chain object from which to retrieve operations.
   :type chain: object

   :returns: A list of operations associated with the given chain object.
   :rtype: list


.. py:class:: PathsChain

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


   Calculate a Chain and Export the G-code Alltogether.


   .. py:attribute:: bl_idname
      :value: 'object.calculate_cam_paths_chain'



   .. py:attribute:: bl_label
      :value: 'Calculate CAM Paths in Current Chain and Export Chain G-code'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active camera chain in the given context.

      This method retrieves the active camera chain from the scene and checks
      its validity using the `isChainValid` function. It returns a boolean
      value indicating whether the camera chain is valid or not.

      :param context: The context containing the scene and camera chain information.
      :type context: Context

      :returns: True if the active camera chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute_async(context)
      :async:


      Execute asynchronous operations for camera path calculations.

      This method sets the object mode for the Blender scene and processes a
      series of camera operations defined in the active camera chain. It
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


      Check the validity of the active camera chain in the given context.

      This method retrieves the currently active camera chain from the scene
      context and checks its validity using the `isChainValid` function. It
      returns a boolean indicating whether the active camera chain is valid or
      not.

      :param context: The context containing the scene and camera chain information.
      :type context: object

      :returns: True if the active camera chain is valid, False otherwise.
      :rtype: bool



   .. py:method:: execute(context)

      Execute the camera path export process.

      This function retrieves the active camera chain from the current scene
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

      Execute the camera operation and export the G-code path.

      This method retrieves the active camera operation from the current scene
      and exports the corresponding G-code path to a specified filename. It
      prints the filename and relevant operation details to the console for
      debugging purposes. The G-code path is generated based on the camera
      path data associated with the active operation.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the completion status of the operation,
                    typically {'FINISHED'}.
      :rtype: dict



.. py:class:: CAMSimulate

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


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


      Execute an asynchronous simulation operation based on the active camera
      operation.

      This method retrieves the current scene and the active camera operation.
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

      Draws the user interface for selecting camera operations.

      This method creates a layout element in the user interface that allows
      users to search and select a specific camera operation from a list of
      available operations defined in the current scene. It utilizes the
      Blender Python API to integrate with the UI.

      :param context: The context in which the drawing occurs, typically
                      provided by Blender's UI system.



.. py:class:: CAMSimulateChain

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`cam.async_op.AsyncOperatorMixin`


   Simulate CAM Chain, Compared to Single Op Simulation Just Writes Into One Image and Thus Enables
   to See how Ops Work Together.


   .. py:attribute:: bl_idname
      :value: 'object.cam_simulate_chain'



   .. py:attribute:: bl_label
      :value: 'CAM Simulation'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:


      Check the validity of the active camera chain in the scene.

      This method retrieves the currently active camera chain from the scene's
      camera chains and checks its validity using the `isChainValid` function.
      It returns a boolean indicating whether the active camera chain is
      valid.

      :param context: The context containing the scene and its properties.
      :type context: object

      :returns: True if the active camera chain is valid, False otherwise.
      :rtype: bool



   .. py:attribute:: operation
      :type:  StringProperty(name='Operation', description='Specify the operation to calculate', default='Operation')


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous simulation for a specified camera chain.

      This method retrieves the active camera chain from the current Blender
      scene and determines the operations associated with that chain. It
      checks if all operations are valid and can be simulated. If valid, it
      proceeds to execute the simulation asynchronously. If any operation is
      invalid, it logs a message and returns a finished status without
      performing the simulation.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the status of the operation, either
                operation completed successfully.
      :rtype: dict



   .. py:method:: draw(context)

      Draw the user interface for selecting camera operations.

      This function creates a user interface element that allows the user to
      search and select a specific camera operation from a list of available
      operations in the current scene. It utilizes the Blender Python API to
      create a property search layout.

      :param context: The context in which the drawing occurs, typically containing
                      information about the current scene and UI elements.



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

      Execute the camera chain creation in the given context.

      This function adds a new camera chain to the current scene in Blender.
      It updates the active camera chain index and assigns a name and filename
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

      Execute the camera chain removal process.

      This function removes the currently active camera chain from the scene
      and decrements the active camera chain index if it is greater than zero.
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

      Execute an operation in the active camera chain.

      This function retrieves the active camera chain from the current scene
      and adds a new operation to it. It increments the active operation index
      and assigns the name of the currently selected camera operation to the
      newly added operation. This is typically used in the context of managing
      camera operations in a 3D environment.

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

      Execute the operation to move the active camera operation in the chain.

      This function retrieves the current scene and the active camera chain.
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

      Execute the operation to move the active camera operation in the chain.

      This function retrieves the current scene and the active camera chain.
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

      Execute the operation to remove the active operation from the camera
      chain.

      This method accesses the current scene and retrieves the active camera
      chain. It then removes the currently active operation from that chain
      and adjusts the index of the active operation accordingly. If the active
      operation index becomes negative, it resets it to zero to ensure it
      remains within valid bounds.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the execution status, typically
                    containing {'FINISHED'} upon successful completion.
      :rtype: dict



.. py:function:: fixUnits()

   Set up units for BlenderCAM.

   This function configures the unit settings for the current Blender
   scene. It sets the rotation system to degrees and the scale length to
   1.0, ensuring that the units are appropriately configured for use within
   BlenderCAM.


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

      Execute the camera operation based on the active object in the scene.

      This method retrieves the active object from the Blender context and
      performs operations related to camera settings. It checks if an object
      is selected and retrieves its bounding box dimensions. If no object is
      found, it reports an error and cancels the operation. If an object is
      present, it adds a new camera operation to the scene, sets its
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

      Execute the camera operation in the given context.

      This method handles the execution of camera operations within the
      Blender scene. It first checks if there are any camera operations
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

      Execute the camera operation in the given context.

      This function performs the active camera operation by deleting the
      associated object from the scene. It checks if there are any camera
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

      Execute a camera operation based on the specified direction.

      This method modifies the active camera operation in the Blender context
      based on the direction specified. If the direction is 'UP', it moves the
      active operation up in the list, provided it is not already at the top.
      Conversely, if the direction is not 'UP', it moves the active operation
      down in the list, as long as it is not at the bottom. The method updates
      the active operation index accordingly.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the operation has finished, with
                the key 'FINISHED'.
      :rtype: dict



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

      Execute the camera orientation operation in Blender.

      This function retrieves the active camera operation from the current
      scene, creates an empty object to represent the camera orientation, and
      adds it to a specified group. The empty object is named based on the
      operation's name and the current count of objects in the group. The size
      of the empty object is set to a predefined value for visibility.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    typically {'FINISHED'}.
      :rtype: dict



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

      Execute the camera operation in the given context.

      This function retrieves the active camera operation from the current
      scene and adds automatic bridges to it. It is typically called within
      the context of a Blender operator to perform specific actions related to
      camera operations.

      :param context: The context in which the operation is executed.

      :returns: A dictionary indicating the result of the operation, typically
                containing the key 'FINISHED' to signify successful completion.
      :rtype: dict



