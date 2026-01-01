fabex.utilities.addon_utils
===========================

.. py:module:: fabex.utilities.addon_utils

.. autoapi-nested-parse::

   Fabex 'addon_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.addon_utils.addon_dependencies
   fabex.utilities.addon_utils.python_dependencies
   fabex.utilities.addon_utils.load_defaults
   fabex.utilities.addon_utils.copy_if_not_exists
   fabex.utilities.addon_utils.copy_presets
   fabex.utilities.addon_utils.on_blender_startup
   fabex.utilities.addon_utils.on_engine_change
   fabex.utilities.addon_utils.fix_units
   fabex.utilities.addon_utils.keymap_register
   fabex.utilities.addon_utils.keymap_unregister
   fabex.utilities.addon_utils.add_asset_library
   fabex.utilities.addon_utils.add_workspace
   fabex.utilities.addon_utils.add_collections
   fabex.utilities.addon_utils.edit_user_post_processor
   fabex.utilities.addon_utils.append_asset_from_library


Module Contents
---------------

.. py:function:: addon_dependencies()

   Checks for and installs Blender addon dependencies.

   This function installs a number of addons that previously came
   with Blender, but now have to be downloaded from an online repository.
   It checks for the addon in the users Blender install, and if it
   can't find them, attempts to download them from Blender.


.. py:function:: python_dependencies()

   Checks for and installs Python library dependencies.

   This function checks for required Python packages. These should
   be installed via the included 'wheels', but if there is a version
   mismatch this function will attempt to install them via pip.


.. py:function:: load_defaults(addon_prefs)

   Assigns scene settings based on user preferences.

   When Fabex is activated it will restore the user's scene settings.
   This includes the interface level (Beginner - Experimental), viewport
   shading, panel layout and machine preset.


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

   Copies Presets from the addon to Blender's Script Directory

   This function copies new presets without overwriting the existing presets,
   unless it detects that the presets have not been updated to the current spec,
   in which case it will overwrite them with the addon presets.


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

   Callback function to setup Fabex when activated.

   In combination with a message bus (msgbus) listener, this function will
   run when the Render Engine is changed. If it detects that Fabex is active
   it will call the required setup functions, and log the Fabex activation.


.. py:function:: fix_units()

   Set up units for Fabex.

   This function configures the unit settings for the current Blender
   scene. It sets the rotation system to degrees and the scale length to
   1.0, ensuring that the units are appropriately configured for use within
   Fabex.


.. py:function:: keymap_register()

   Adds a Keyboard Shortcut to the Active Key Config

   This function binds the keyboard shortcut 'Alt+C' to the Fabex
   Pie Menu, and adds that shortcut to the user's active key configuration.


.. py:function:: keymap_unregister()

   Removes a Keyboard Shortcut from the Active Key Config

   This function removes the keyboard shortcut 'Alt+C' from
   the user's active key configuration.


.. py:function:: add_asset_library()

   Installs the Fabex Asset Library.

   This function adds the /assets/ folder from Fabex to the users'
   Asset Library, which adds a number of Material and Geometry Node
   assets.


.. py:function:: add_workspace()

   Installs the Fabex Workspace

   This function adds the Fabex Workspace to the users' default Blender
   startup scene.


.. py:function:: add_collections()

   Adds color-coded Collection folders to the scene.

   This function adds three collections to aid in scene management.
   Bridges, Paths and Simulations are now auto-sorted into their
   own collections upon creation, which can be shown or hidden as
   groups.


.. py:function:: edit_user_post_processor()

   Open and Edit the User Post Processor file in the Text Editor

   This function finds the path to the 'user.py' post processor file
   and opens it for editing in Blender's Text Editor. In order to open
   the file Blender's Context must be overridden to ensure the Text Editor
   actions can run no matter what Context the user is currently in.


.. py:function:: append_asset_from_library(asset_type, asset_name)

   Append an Asset from the Fabex Asset Library

   This function adds an asset from the Fabex Asset Library to the
   current file. The path to the library is automatically filled, but
   the user must provide the type and name of the asset they wish to
   append. Currently the library contains materials, node groups and
   scenes, and separate logic is provided for each.


