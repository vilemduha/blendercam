fabex.utilities.addon_utils
===========================

.. py:module:: fabex.utilities.addon_utils

.. autoapi-nested-parse::

   Fabex 'addon_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.addon_utils.addon_dependencies
   fabex.utilities.addon_utils.load_defaults
   fabex.utilities.addon_utils.copy_if_not_exists
   fabex.utilities.addon_utils.copy_presets
   fabex.utilities.addon_utils.on_blender_startup
   fabex.utilities.addon_utils.on_engine_change
   fabex.utilities.addon_utils.fix_units
   fabex.utilities.addon_utils.keymap_register
   fabex.utilities.addon_utils.keymap_unregister


Module Contents
---------------

.. py:function:: addon_dependencies()

.. py:function:: load_defaults(addon_prefs)

.. py:function:: copy_if_not_exists(src, dst)

   Copy a file from source to destination if it does not already exist.

   This function checks if the destination file exists. If it does not, the
   function copies the source file to the destination using a high-level
   file operation that preserves metadata.

   :param src: The path to the source file to be copied.
   :type src: str
   :param dst: The path to the destination where the file should be copied.
   :type dst: str


.. py:function:: copy_presets(addon_prefs)

.. py:function:: on_blender_startup(context)

   Checks for any broken computations on load and resets them.

   This function verifies the presence of necessary Blender add-ons and
   installs any that are missing. It also resets any ongoing computations
   in CAM operations and sets the interface level to the previously used
   level when loading a new file. If the add-on has been updated, it copies
   the necessary presets from the source to the target directory.
   Additionally, it checks for updates to the CAM plugin and updates
   operation presets if required.

   :param context: The context in which the function is executed, typically containing
                   information about
                   the current Blender environment.


.. py:function:: on_engine_change(*args)

.. py:function:: fix_units()

   Set up units for Fabex.

   This function configures the unit settings for the current Blender
   scene. It sets the rotation system to degrees and the scale length to
   1.0, ensuring that the units are appropriately configured for use within
   Fabex.


.. py:function:: keymap_register()

.. py:function:: keymap_unregister()

