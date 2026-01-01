fabex.toolpath
==============

.. py:module:: fabex.toolpath

.. autoapi-nested-parse::

   Fabex 'toolpath.py' © 2012 Vilem Novak

   Generate toolpaths from path chunks.



Functions
---------

.. autoapisummary::

   fabex.toolpath.path_profiler
   fabex.toolpath.get_path
   fabex.toolpath.get_path_3_axis
   fabex.toolpath.get_path_4_axis


Module Contents
---------------

.. py:function:: path_profiler(strategy)
   :async:


.. py:function:: get_path(context, operation)
   :async:


   Calculate the path for a given operation in a specified context.

   This function performs various calculations to determine the path based
   on the operation's parameters and context. It checks for changes in the
   operation's data and updates relevant tags accordingly. Depending on the
   number of machine axes specified in the operation, it calls different
   functions to handle 3-axis, 4-axis, or 5-axis operations. Additionally,
   if automatic export is enabled, it exports the generated G-code path.

   :param context: The context in which the operation is being performed.
   :param operation: An object representing the operation with various
                     attributes such as machine_axes, strategy, and
                     auto_export.


.. py:function:: get_path_3_axis(context, operation)
   :async:


   Generate a machining path based on the specified operation strategy.

   This function evaluates the provided operation's strategy and generates
   the corresponding machining path. It supports various strategies such as
   'CUTOUT', 'CURVE', 'PROJECTED_CURVE', 'POCKET', and others. Depending on
   the strategy, it performs specific calculations and manipulations on the
   input data to create a path that can be used for machining operations.
   The function handles different strategies by calling appropriate methods
   from the `strategy` module and processes the path samples accordingly.
   It also manages the generation of chunks, which represent segments of
   the machining path, and applies any necessary transformations based on
   the operation's parameters.

   :param context: The Blender context containing scene information.
   :type context: bpy.context
   :param operation: An object representing the machining operation,
                     which includes strategy and other relevant parameters.
   :type operation: Operation

   :returns: This function does not return a value but modifies the state of
             the operation and context directly.
   :rtype: None


.. py:function:: get_path_4_axis(context, operation)
   :async:


   Generate a path for a specified axis based on the given operation.

   This function retrieves the bounds of the operation and checks the
   strategy associated with the axis. If the strategy is one of the
   specified types ('PARALLELR', 'PARALLEL', 'HELIX', 'CROSS'), it
   generates path samples and processes them into chunks for meshing. The
   function utilizes various helper functions to achieve this, including
   obtaining layers and sampling chunks.

   :param context: The context in which the operation is executed.
   :param operation: An object that contains the strategy and other
                     necessary parameters for generating the path.

   :returns:

             This function does not return a value but modifies
                 the state of the operation by processing chunks for meshing.
   :rtype: None


