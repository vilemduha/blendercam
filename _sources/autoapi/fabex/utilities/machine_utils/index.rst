fabex.utilities.machine_utils
=============================

.. py:module:: fabex.utilities.machine_utils

.. autoapi-nested-parse::

   Fabex 'machine_utils.py' © 2012 Vilem Novak

   Main functionality of Fabex.
   The functions here are called with operators defined in 'ops.py'



Functions
---------

.. autoapisummary::

   fabex.utilities.machine_utils.add_machine_area_object
   fabex.utilities.machine_utils.update_machine
   fabex.utilities.machine_utils.update_unit_system


Module Contents
---------------

.. py:function:: add_machine_area_object()

   Add a machine area object to the current Blender scene.

   This function checks if a machine object named 'CAM_Machine' already
   exists in the current scene. If it does not exist, it creates a new cube
   mesh object, applies transformations, and modifies its geometry to
   represent a machine area. The function ensures that the scene's unit
   settings are set to metric before creating the object and restores the
   original unit settings afterward. It also configures the display
   properties of the object for better visibility in the scene.  The
   function operates within Blender's context and utilizes various Blender
   operations to create and modify the mesh. It also handles the selection
   state of the active object.


.. py:function:: update_machine(self, context)

   Update the machine with the given context.

   This function is responsible for updating the machine state based on the
   provided context. It prints a message indicating that the update process
   has started. If the global variable _IS_LOADING_DEFAULTS is not set to
   True, it proceeds to add a machine area object.

   :param context: The context in which the machine update is being performed.


.. py:function:: update_unit_system(self, context)

   Update the scene units based on the machine units

   This function is responsible for updating the Blender scene unit system
   and length unit settings, it reads the 'machine_unit' string and sets the
   scene to Imperial, Inches or Metric, Millimeters.

   :param context: The context in which the machine update is being performed.


