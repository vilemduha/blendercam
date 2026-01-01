fabex.gcode.gcode_export
========================

.. py:module:: fabex.gcode.gcode_export

.. autoapi-nested-parse::

   Fabex 'gcodepath.py' © 2012 Vilem Novak

   Generate and Export G-Code based on scene, machine, chain, operation and path settings.



Functions
---------

.. autoapisummary::

   fabex.gcode.gcode_export.export_gcode_path


Module Contents
---------------

.. py:function:: export_gcode_path(filename, vertslist, operations)

   Exports G-code using the Heeks NC Adopted Library.

   This function generates G-code from a list of vertices and operations
   specified by the user. It handles various post-processor settings based
   on the machine configuration and can split the output into multiple
   files if the total number of operations exceeds a specified limit. The
   G-code is tailored for different machine types and includes options for
   tool changes, spindle control, and various movement commands.

   :param filename: The name of the file to which the G-code will be exported.
   :type filename: str
   :param vertslist: A list of mesh objects containing vertex data.
   :type vertslist: list
   :param operations: A list of operations to be performed, each containing
                      specific parameters for G-code generation.
   :type operations: list

   :returns: This function does not return a value; it writes the G-code to a file.
   :rtype: None


