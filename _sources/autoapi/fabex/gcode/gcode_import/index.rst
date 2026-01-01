fabex.gcode.gcode_import
========================

.. py:module:: fabex.gcode.gcode_import

.. autoapi-nested-parse::

   Fabex 'gcodeimportparser.py'


   Code modified from YAGV (Yet Another G-code Viewer) - https://github.com/jonathanwin/yagv

   No license terms found in YAGV repo, will assume GNU release



Attributes
----------

.. autoapisummary::

   fabex.gcode.gcode_import.path


Classes
-------

.. autoapisummary::

   fabex.gcode.gcode_import.GcodeParser
   fabex.gcode.gcode_import.GcodeModel
   fabex.gcode.gcode_import.Segment
   fabex.gcode.gcode_import.Layer


Functions
---------

.. autoapisummary::

   fabex.gcode.gcode_import.import_gcode
   fabex.gcode.gcode_import.segments_to_meshdata
   fabex.gcode.gcode_import.obj_from_pydata


Module Contents
---------------

.. py:function:: import_gcode(self, context, filepath)

   Import G-code data into the scene.


   This function reads G-code from a specified file and processes it

   according to the settings defined in the context. It utilizes the

   GcodeParser to parse the file and classify segments of the model.

   Depending on the options set in the scene, it may subdivide the model

   and draw it with or without layer splitting. The time taken for the
   import process is printed to the console.


   :param context: The context containing the scene and tool settings.
   :type context: Context
   :param filepath: The path to the G-code file to be imported.
   :type filepath: str

   :returns:

             A dictionary indicating the import status, typically

                 {'FINISHED'}.
   :rtype: dict


.. py:function:: segments_to_meshdata(segments)

   Convert a list of segments into mesh data consisting of vertices and
   edges.


   This function processes a list of segment objects, extracting the

   coordinates of vertices and defining edges based on the styles of the

   segments. It identifies when to add vertices and edges based on whether

   the segments are in 'extrude' or 'travel' styles. The resulting mesh

   data can be used for 3D modeling or rendering applications.


   :param segments: A list of segment objects, each containing 'style' and

                    'coords' attributes.
   :type segments: list

   :returns:

             A tuple containing two elements:

                 - list: A list of vertices, where each vertex is represented as a

                 list of coordinates [X, Y, Z].

                 - list: A list of edges, where each edge is represented as a list

                 of indices corresponding to the vertices.
   :rtype: tuple


.. py:function:: obj_from_pydata(name, verts, edges=None, close=True, collection_name=None)

   Create a Blender object from provided vertex and edge data.


   This function generates a mesh object in Blender using the specified

   vertices and edges. If edges are not provided, it automatically creates

   a chain of edges connecting the vertices. The function also allows for

   the option to close the mesh by connecting the last vertex back to the

   first. Additionally, it can place the created object into a specified

   collection within the Blender scene. The object is scaled down to a

   smaller size for better visibility in the Blender environment.


   :param name: The name of the object to be created.
   :type name: str
   :param verts: A list of vertex coordinates, where each vertex is represented as a

                 tuple of (x, y, z).
   :type verts: list
   :param edges: A list of edges defined by pairs of vertex indices. Defaults to None.
   :type edges: list?
   :param close: Whether to close the mesh by connecting the last vertex to the first.

                 Defaults to True.
   :type close: bool?
   :param collection_name: The name of the collection to which the object should be added. Defaults

                           to None.
   :type collection_name: str?

   :returns:

             The function does not return a value; it creates an object in the

                 Blender scene.
   :rtype: None


.. py:class:: GcodeParser

   .. py:attribute:: comment
      :value: ''



   .. py:attribute:: model


   .. py:method:: parse_file(path)

      Parse a G-code file and update the model.


      This function reads a G-code file line by line, increments a line

      counter for each line, and processes each line using the `parseLine`

      method. The function assumes that the file is well-formed and that each

      line can be parsed without errors. After processing all lines, it

      returns the updated model.


      :param path: The file path to the G-code file to be parsed.
      :type path: str

      :returns: The updated model after parsing the G-code file.
      :rtype: model



   .. py:method:: parse_line()

      Parse a line of G-code and execute the corresponding command.


      This method processes a line of G-code by stripping comments, cleaning

      the command, and identifying the command code and its arguments. It

      handles specific G-code commands and invokes the appropriate parsing

      method if available. If the command is unsupported, it prints an error

      message. The method also manages tool numbers and coordinates based on
      the parsed command.



   .. py:method:: parse_args(args)

      Parse command-line arguments into a dictionary.


      This function takes a string of arguments, splits it into individual

      components, and maps each component's first character to its

      corresponding numeric value. If a numeric value cannot be converted from

      the string, it defaults to 1. The resulting dictionary contains the

      first characters as keys and their associated numeric values as values.


      :param args: A string of space-separated arguments, where each argument

                   consists of a letter followed by a numeric value.
      :type args: str

      :returns: A dictionary mapping each letter to its corresponding numeric value.
      :rtype: dict



   .. py:method:: parse_G1(args, type='G1')


   .. py:method:: parse_G0(args, type='G0')


   .. py:method:: parse_G90(args)


   .. py:method:: parse_G91(args)


   .. py:method:: parse_G92(args)


   .. py:method:: warn(msg)


   .. py:method:: error(msg)

      Log an error message and raise an exception.


      This method prints an error message to the console, including the line

      number, the provided message, and the text associated with the error.

      After logging the error, it raises a generic Exception with the same
      message format.


      :param msg: The error message to be logged.
      :type msg: str

      :raises Exception: Always raises an Exception with the formatted error message.



.. py:class:: GcodeModel(parser)

   .. py:attribute:: parser


   .. py:attribute:: relative


   .. py:attribute:: offset


   .. py:attribute:: isRelative
      :value: False



   .. py:attribute:: color
      :value: [0, 0, 0, 0, 0, 0, 0, 0]



   .. py:attribute:: toolnumber
      :value: 0



   .. py:attribute:: segments
      :value: []



   .. py:attribute:: layers
      :value: []



   .. py:method:: do_G1(args, type)

      Perform a rapid or controlled movement based on the provided arguments.


      This method updates the current coordinates based on the input

      arguments, either in relative or absolute terms. It constructs a segment

      representing the movement and adds it to the model if there are changes

      in the XYZ coordinates. The function handles unknown axes by issuing a

      warning and ensures that the segment is only added if there are actual
      changes in position.


      :param args: A dictionary containing movement parameters for each axis.
      :type args: dict
      :param type: The type of movement (e.g., 'G0' for rapid move, 'G1' for controlled

                   move).
      :type type: str



   .. py:method:: do_G92(args)

      Set the current position of the axes without moving.


      This method updates the current coordinates for the specified axes based

      on the provided arguments. If no axes are mentioned, it sets all axes

      (X, Y, Z) to zero. The method adjusts the offset values by transferring

      the difference between the relative and specified values for each axis.

      If an unknown axis is provided, a warning is issued.


      :param args: A dictionary containing axis names as keys

                   (e.g., 'X', 'Y', 'Z') and their corresponding

                   position values as float.
      :type args: dict



   .. py:method:: do_M163(args)

      Update the color settings for a specific segment based on given
      parameters.


      This method modifies the color attributes of an object by updating the

      CMYKW values for a specified segment. It first creates a new list from

      the existing color attribute to avoid reference issues. The method then

      extracts the index and weight from the provided arguments and updates

      the color list accordingly. Additionally, it retrieves RGB values from
      the last comment and applies them to the color list.


      :param args: A dictionary containing the parameters for the operation.

                   - 'S' (int): The index of the segment to update.

                   - 'P' (float): The weight to set for the CMYKW color component.
      :type args: dict

      :returns: This method does not return a value; it modifies the object's state.
      :rtype: None



   .. py:method:: set_relative(isRelative)


   .. py:method:: add_segment(segment)


   .. py:method:: warn(msg)


   .. py:method:: error(msg)


   .. py:method:: classify_segments()

      Classify segments into layers based on their coordinates and extrusion

      style.


      This method processes a list of segments, determining their extrusion

      style (travel, retract, restore, or extrude) based on the movement of

      the coordinates and the state of the extruder. It organizes the segments

      into layers, which are used for later rendering. The classification is

      based on changes in the Z-coordinate and the extruder's position.  The

      function initializes the coordinates and iterates through each segment,

      checking for movements in the X, Y, and Z directions. It identifies when

      a new layer begins based on changes in the Z-coordinate and the

      extruder's state. Segments are then grouped into layers for further

      processing.  Raises:     None



   .. py:method:: subdivide(subd_threshold)

      Subdivide segments based on a specified threshold.


      This method processes a list of segments and subdivides them into

      smaller segments if the distance between consecutive segments exceeds

      the given threshold. The subdivision is performed by interpolating

      points between the original segment's coordinates, ensuring that the

      resulting segments maintain the original order and properties. This is

      particularly useful for manipulating attributes such as color and

      continuous deformation in graphical representations.


      :param subd_threshold: The distance threshold for subdividing segments.

                             Segments with a distance greater than this value

                             will be subdivided.
      :type subd_threshold: float

      :returns: The method modifies the instance's segments attribute in place.
      :rtype: None



   .. py:method:: draw(split_layers=False)

      Draws a mesh from segments and layers.


      This function creates a Blender curve and vertex information in a text

      file, which includes coordinates, style, and color. If the

      `split_layers` parameter is set to True, it processes each layer

      individually, generating vertices and edges for each layer. If False, it

      processes the segments as a whole.


      :param split_layers: A flag indicating whether to split the drawing into

                           separate layers or not.
      :type split_layers: bool



.. py:class:: Segment(type, coords, color, toolnumber, lineNb, line)

   .. py:attribute:: type


   .. py:attribute:: coords


   .. py:attribute:: color


   .. py:attribute:: toolnumber


   .. py:attribute:: lineNb


   .. py:attribute:: line


   .. py:attribute:: style
      :value: None



   .. py:attribute:: layerIdx
      :value: None



   .. py:method:: __str__()

      Return a string representation of the object.


      This method constructs a string that includes the coordinates, line

      number, style, layer index, and color of the object. It formats these

      attributes into a readable string format for easier debugging and
      logging.


      :returns: A formatted string representing the object's attributes.
      :rtype: str



.. py:class:: Layer(Z)

   .. py:attribute:: Z


   .. py:attribute:: segments
      :value: []



   .. py:attribute:: distance
      :value: None



   .. py:attribute:: extrudate
      :value: None



   .. py:method:: __str__()


.. py:data:: path
   :value: 'test.gcode'


