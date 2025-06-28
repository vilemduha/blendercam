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


