fabex.gcode_path
================

.. py:module:: fabex.gcode_path

.. autoapi-nested-parse::

   Fabex 'gcodepath.py' © 2012 Vilem Novak

   Generate and Export G-Code based on scene, machine, chain, operation and path settings.



Functions
---------

.. autoapisummary::

   fabex.gcode_path.point_on_line
   fabex.gcode_path.export_gcode_path
   fabex.gcode_path.get_path
   fabex.gcode_path.get_change_data
   fabex.gcode_path.check_memory_limit
   fabex.gcode_path.get_path_3_axis
   fabex.gcode_path.get_path_4_axis


Module Contents
---------------

.. py:function:: point_on_line(a, b, c, tolerance)

   Determine if the angle between two vectors is within a specified
   tolerance.

   This function checks if the angle formed by two vectors, defined by
   points `b` and `c` relative to point `a`, is less than or equal to a
   given tolerance. It converts the points into vectors, calculates the dot
   product, and then computes the angle between them using the arccosine
   function. If the angle exceeds the specified tolerance, the function
   returns False; otherwise, it returns True.

   :param a: The origin point as a vector.
   :type a: numpy.ndarray
   :param b: The first point as a vector.
   :type b: numpy.ndarray
   :param c: The second point as a vector.
   :type c: numpy.ndarray
   :param tolerance: The maximum allowable angle (in degrees) between the vectors.
   :type tolerance: float

   :returns:

             True if the angle between vectors b and c is within the specified
                 tolerance,
                 False otherwise.
   :rtype: bool


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


.. py:function:: get_change_data(o)

   Check if object properties have changed to determine if image updates
   are needed.

   This function inspects the properties of objects specified by the input
   parameter to see if any changes have occurred. It concatenates the
   location, rotation, and dimensions of the relevant objects into a single
   string, which can be used to determine if an image update is necessary
   based on changes in the object's state.

   :param o: An object containing properties that specify the geometry source
             and relevant object or collection names.
   :type o: object

   :returns:

             A string representation of the location, rotation, and dimensions of
                 the specified objects.
   :rtype: str


.. py:function:: check_memory_limit(o)

   Check and adjust the memory limit for an object.

   This function calculates the resolution of an object based on its
   dimensions and the specified pixel size. If the calculated resolution
   exceeds the defined memory limit, it adjusts the pixel size accordingly
   to reduce the resolution. A warning message is appended to the object's
   info if the pixel size is modified.

   :param o: An object containing properties such as max, min, optimisation, and
             info.
   :type o: object

   :returns:

             This function modifies the object's properties in place and does not
                 return a value.
   :rtype: None


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


