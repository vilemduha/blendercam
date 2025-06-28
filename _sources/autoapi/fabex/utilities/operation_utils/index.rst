fabex.utilities.operation_utils
===============================

.. py:module:: fabex.utilities.operation_utils

.. autoapi-nested-parse::

   Fabex 'operation_utils.py' © 2012 Vilem Novak

   Main functionality of Fabex.
   The functions here are called with operators defined in 'ops.py'



Functions
---------

.. autoapisummary::

   fabex.utilities.operation_utils.get_operation_sources
   fabex.utilities.operation_utils.reload_paths
   fabex.utilities.operation_utils.update_operation
   fabex.utilities.operation_utils.source_valid
   fabex.utilities.operation_utils.operation_valid
   fabex.utilities.operation_utils.chain_valid
   fabex.utilities.operation_utils.update_operation_valid
   fabex.utilities.operation_utils.update_chipload
   fabex.utilities.operation_utils.update_offset_image
   fabex.utilities.operation_utils.update_Z_buffer_image
   fabex.utilities.operation_utils.update_image_size_y
   fabex.utilities.operation_utils.update_bridges
   fabex.utilities.operation_utils.update_rotation
   fabex.utilities.operation_utils.update_rest
   fabex.utilities.operation_utils.update_operation
   fabex.utilities.operation_utils.update_zbuffer_image
   fabex.utilities.operation_utils.get_chain_operations


Module Contents
---------------

.. py:function:: get_operation_sources(o)

   Get operation sources based on the geometry source type.

   This function retrieves and sets the operation sources for a given
   object based on its geometry source type. It handles three types of
   geometry sources: 'OBJECT', 'COLLECTION', and 'IMAGE'. For 'OBJECT', it
   selects the specified object and applies rotations if enabled. For
   'COLLECTION', it retrieves all objects within the specified collection.
   For 'IMAGE', it sets a specific optimization flag. Additionally, it
   determines whether the objects are curves or meshes based on the
   geometry source.

   :param o: An object containing properties such as geometry_source,
             object_name, collection_name, rotation_a, rotation_b,
             enable_A, enable_B, old_rotation_a, old_rotation_b,
             A_along_x, and optimisation.
   :type o: Object

   :returns:

             This function does not return a value but modifies the
                 properties of the input object.
   :rtype: None


.. py:function:: reload_paths(o)

   Reload the CAM path data from a pickle file.

   This function retrieves the CAM path data associated with the given
   object `o`. It constructs a new mesh from the path vertices and updates
   the object's properties with the loaded data. If a previous path mesh
   exists, it is removed to avoid memory leaks. The function also handles
   the creation of a new mesh object if one does not already exist in the
   current scene.

   :param o: The object for which the CAM path is being
   :type o: Object


.. py:function:: update_operation(self, context)

   Update the visibility and selection state of CAM operations in the
   scene.

   This method manages the visibility of objects associated with CAM
   operations based on the current active operation. If the
   'hide_all_others' flag is set to true, it hides all other objects except
   for the currently active one. If the flag is false, it restores the
   visibility of previously hidden objects. The method also attempts to
   highlight the currently active object in the 3D view and make it the
   active object in the scene.

   :param context: The context containing the current scene and
   :type context: bpy.types.Context


.. py:function:: source_valid(o, context)

   Check the validity of a geometry source.

   This function verifies if the provided geometry source is valid based on
   its type. It checks for three types of geometry sources: 'OBJECT',
   'COLLECTION', and 'IMAGE'. For 'OBJECT', it ensures that the object name
   ends with '_cut_bridges' or exists in the Blender data objects. For
   'COLLECTION', it checks if the collection name exists and contains
   objects. For 'IMAGE', it verifies if the source image name exists in the
   Blender data images.

   :param o: An object containing geometry source information, including
             attributes like `geometry_source`, `object_name`, `collection_name`,
             and `source_image_name`.
   :type o: object
   :param context: The context in which the validation is performed (not used in this
                   function).

   :returns: True if the geometry source is valid, False otherwise.
   :rtype: bool


.. py:function:: operation_valid(self, context)

   Validate the current CAM operation in the given context.

   This method checks if the active CAM operation is valid based on the
   current scene context. It updates the operation's validity status and
   provides warnings if the source object is invalid. Additionally, it
   configures specific settings related to image geometry sources.

   :param context: The context containing the scene and CAM operations.
   :type context: Context


.. py:function:: chain_valid(chain, context)

   Check the validity of a chain of operations within a given context.

   This function verifies if all operations in the provided chain are valid
   according to the current scene context. It first checks if the chain
   contains any operations. If it does, it iterates through each operation
   in the chain and checks if it exists in the scene's CAM operations.
   If an operation is not found or is deemed invalid, the function returns
   a tuple indicating the failure and provides an appropriate error
   message. If all operations are valid, it returns a success indication.

   :param chain: The chain of operations to validate.
   :type chain: Chain
   :param context: The context containing the scene and CAM operations.
   :type context: Context

   :returns:

             A tuple containing a boolean indicating validity and an error message
                 (if any). The first element is True if valid, otherwise False. The
                 second element is an error message string.
   :rtype: tuple


.. py:function:: update_operation_valid(self, context)

.. py:function:: update_chipload(self, context)

   Update the chipload based on feedrate, spindle RPM, and cutter
   parameters.

   This function calculates the chipload using the formula: chipload =
   feedrate / (spindle_rpm * cutter_flutes). It also attempts to account
   for chip thinning when cutting at less than 50% cutter engagement with
   cylindrical end mills by combining two formulas. The first formula
   provides the nominal chipload based on standard recommendations, while
   the second formula adjusts for the cutter diameter and distance between
   paths.  The current implementation may not yield consistent results, and
   there are concerns regarding the correctness of the units used in the
   calculations. Further review and refinement of this function may be
   necessary to improve accuracy and reliability.

   :param context: The context in which the update is performed (not used in this
                   implementation).

   :returns: This function does not return a value; it updates the chipload in place.
   :rtype: None


.. py:function:: update_offset_image(self, context)

   Refresh the Offset Image Tag for re-rendering.

   This method updates the chip load and marks the offset image tag for re-
   rendering. It sets the `changed` attribute to True and indicates that
   the offset image tag needs to be updated.

   :param context: The context in which the update is performed.


.. py:function:: update_Z_buffer_image(self, context)

   Update the Z-buffer and offset image tags for recalculation.

   This method modifies the internal state to indicate that the Z-buffer
   image and offset image tags need to be updated during the calculation
   process. It sets the `changed` attribute to True and marks the relevant
   tags for updating. Additionally, it calls the `getOperationSources`
   function to ensure that the necessary operation sources are retrieved.

   :param context: The context in which the update is being performed.


.. py:function:: update_image_size_y(self, context)

   Updates the Image Y size based on the following function.


.. py:function:: update_bridges(o, context)

   Update the status of bridges.

   This function marks the bridge object as changed, indicating that an
   update has occurred. It prints a message to the console for logging
   purposes. The function takes in an object and a context, but the context
   is not utilized within the function.

   :param o: The bridge object that needs to be updated.
   :type o: object
   :param context: Additional context for the update, not used in this function.
   :type context: object


.. py:function:: update_rotation(o, context)

   Update the rotation of a specified object in Blender.

   This function modifies the rotation of a Blender object based on the
   properties of the provided object 'o'. It checks which rotations are
   enabled and applies the corresponding rotation values to the active
   object in the scene. The rotation can be aligned either along the X or Y
   axis, depending on the configuration of 'o'.

   :param o: An object containing rotation settings and flags.
   :type o: object
   :param context: The context in which the operation is performed.
   :type context: object


.. py:function:: update_rest(o, context)

   Update the state of the object.

   This function modifies the given object by setting its 'changed'
   attribute to True. It also prints a message indicating that the update
   operation has been performed.

   :param o: The object to be updated.
   :type o: object
   :param context: The context in which the update is being performed.
   :type context: object


.. py:function:: update_operation(self, context)

   Update the CAM operation based on the current context.

   This function retrieves the active CAM operation from the Blender
   context and updates it using the `updateRest` function. It accesses the
   active operation from the scene's CAM operations and passes the
   current context to the updating function.

   :param context: The context in which the operation is being updated.


.. py:function:: update_zbuffer_image(self, context)

   Update the Z-buffer image based on the active CAM operation.

   This function retrieves the currently active CAM operation from the
   Blender context and updates the Z-buffer image accordingly. It accesses
   the scene's CAM operations and invokes the `updateZbufferImage`
   function with the active operation and context.

   :param context: The current Blender context.
   :type context: bpy.context


.. py:function:: get_chain_operations(chain)

   Return chain operations associated with a given chain object.

   This function iterates through the operations of the provided chain
   object and retrieves the corresponding operations from the current
   scene's CAM operations in Blender. Due to limitations in Blender,
   chain objects cannot store operations directly, so this function serves
   to extract and return the relevant operations for further processing.

   :param chain: The chain object from which to retrieve operations.
   :type chain: object

   :returns: A list of operations associated with the given chain object.
   :rtype: list


