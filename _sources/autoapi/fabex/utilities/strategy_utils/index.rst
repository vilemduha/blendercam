fabex.utilities.strategy_utils
==============================

.. py:module:: fabex.utilities.strategy_utils

.. autoapi-nested-parse::

   Fabex 'strategy_utils.py' © 2012 Vilem Novak

   Main functionality of Fabex.
   The functions here are called with operators defined in 'ops.py'



Functions
---------

.. autoapisummary::

   fabex.utilities.strategy_utils.update_strategy
   fabex.utilities.strategy_utils.update_cutout
   fabex.utilities.strategy_utils.update_exact
   fabex.utilities.strategy_utils.update_opencamlib_1
   fabex.utilities.strategy_utils.get_strategy_list
   fabex.utilities.strategy_utils.update_exact_mode
   fabex.utilities.strategy_utils.update_opencamlib
   fabex.utilities.strategy_utils.add_pocket
   fabex.utilities.strategy_utils.parallel_pattern


Module Contents
---------------

.. py:function:: update_strategy(o, context)

   Update the strategy of the given object.

   This function modifies the state of the object `o` by setting its
   `changed` attribute to True and printing a message indicating that the
   strategy is being updated. Depending on the value of `machine_axes` and
   `strategy_4_axis`, it either adds or removes an orientation object
   associated with `o`. Finally, it calls the `updateExact` function to
   perform further updates based on the provided context.

   :param o: The object whose strategy is to be updated.
   :type o: object
   :param context: The context in which the update is performed.
   :type context: object


.. py:function:: update_cutout(o, context)

.. py:function:: update_exact(o, context)

   Update the state of an object for exact operations.

   This function modifies the properties of the given object `o` to
   indicate that an update is required. It sets various flags related to
   the object's state and checks the optimization settings. If the
   optimization is set to use exact mode, it further checks the strategy
   and inverse properties to determine if exact mode can be used. If not,
   it disables the use of OpenCamLib.

   :param o: The object to be updated, which contains properties related
   :type o: object
   :param context: The context in which the update is being performed.
   :type context: object

   :returns: This function does not return a value.
   :rtype: None


.. py:function:: update_opencamlib_1(o, context)

   Update the OpenCAMLib settings for a given operation.

   This function modifies the properties of the provided operation object
   based on its current strategy and optimization settings. If the
   operation's strategy is either 'POCKET' or 'MEDIAL_AXIS', and if
   OpenCAMLib is being used for optimization, it disables the use of both
   exact optimization and OpenCAMLib, indicating that the current operation
   cannot utilize OpenCAMLib.

   :param o: The operation object containing optimization and strategy settings.
   :type o: object
   :param context: The context in which the operation is being updated.
   :type context: object

   :returns: This function does not return any value.
   :rtype: None


.. py:function:: get_strategy_list(scene, context)

   Get a list of available strategies for operations.

   This function retrieves a predefined list of operation strategies that
   can be used in the context of a 3D scene. Each strategy is represented
   as a tuple containing an identifier, a user-friendly name, and a
   description of the operation. The list includes various operations such
   as cutouts, pockets, drilling, and more. If experimental features are
   enabled in the preferences, additional experimental strategies may be
   included in the returned list.

   :param scene: The current scene context.
   :param context: The current context in which the operation is being performed.

   :returns:

             A list of tuples, each containing the strategy identifier,
                 name, and description.
   :rtype: list


.. py:function:: update_exact_mode(self, context)

   Update the exact mode of the active CAM operation.

   This function retrieves the currently active CAM operation from the
   Blender context and updates its exact mode using the `updateExact`
   function. It accesses the active operation through the `cam_operations`
   list in the current scene and passes the active operation along with the
   current context to the `updateExact` function.

   :param context: The context in which the update is performed.


.. py:function:: update_opencamlib(self, context)

   Update the OpenCamLib with the current active operation.

   This function retrieves the currently active CAM operation from the
   Blender context and updates the OpenCamLib accordingly. It accesses the
   active operation from the scene's CAM operations and passes it along
   with the current context to the update function.

   :param context: The context in which the operation is being performed, typically
                   provided by
                   Blender's internal API.


.. py:function:: add_pocket(max_depth, sname, new_cutter_diameter)

   Add a pocket operation for the medial axis and profile cut.

   This function first deselects all objects in the scene and then checks
   for any existing medial pocket objects, deleting them if found. It
   verifies whether a medial pocket operation already exists in the CAM
   operations. If it does not exist, it creates a new pocket operation with
   the specified parameters. The function also modifies the selected
   object's silhouette offset based on the new cutter diameter.

   :param max_depth: The maximum depth of the pocket to be created.
   :type max_depth: float
   :param sname: The name of the object to which the pocket will be added.
   :type sname: str
   :param new_cutter_diameter: The diameter of the new cutter to be used.
   :type new_cutter_diameter: float


.. py:function:: parallel_pattern(o, angle)

   Generate path chunks for parallel movement based on object dimensions
   and angle.

   This function calculates a series of path chunks for a given object,
   taking into account its dimensions and the specified angle. It utilizes
   both a traditional method and an alternative algorithm (currently
   disabled) to generate these paths. The paths are constructed by
   iterating over calculated vectors and applying transformations based on
   the object's properties. The resulting path chunks can be used for
   various movement types, including conventional and climb movements.

   :param o: An object containing properties such as dimensions and movement type.
   :type o: object
   :param angle: The angle to rotate the path generation.
   :type angle: float

   :returns:

             A list of path chunks generated based on the object's dimensions and
                 angle.
   :rtype: list


