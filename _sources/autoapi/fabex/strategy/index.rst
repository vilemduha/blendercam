fabex.strategy
==============

.. py:module:: fabex.strategy

.. autoapi-nested-parse::

   Fabex 'strategy.py' © 2012 Vilem Novak

   Strategy functionality of Fabex - e.g. Cutout, Parallel, Spiral, Waterline
   The functions here are called with operators defined in 'ops.py'



Functions
---------

.. autoapisummary::

   fabex.strategy.add_pocket
   fabex.strategy.cutout
   fabex.strategy.curve
   fabex.strategy.project_curve
   fabex.strategy.pocket
   fabex.strategy.drill
   fabex.strategy.medial_axis
   fabex.strategy.get_layers
   fabex.strategy.chunks_to_mesh
   fabex.strategy.check_min_z


Module Contents
---------------

.. py:function:: add_pocket(maxdepth, sname, new_cutter_diameter)

   Add a pocket operation for the medial axis and profile cut.

   This function first deselects all objects in the scene and then checks
   for any existing medial pocket objects, deleting them if found. It
   verifies whether a medial pocket operation already exists in the CAM
   operations. If it does not exist, it creates a new pocket operation with
   the specified parameters. The function also modifies the selected
   object's silhouette offset based on the new cutter diameter.

   :param maxdepth: The maximum depth of the pocket to be created.
   :type maxdepth: float
   :param sname: The name of the object to which the pocket will be added.
   :type sname: str
   :param new_cutter_diameter: The diameter of the new cutter to be used.
   :type new_cutter_diameter: float


.. py:function:: cutout(o)
   :async:


   Perform a cutout operation based on the provided parameters.

   This function calculates the necessary cutter offset based on the cutter
   type and its parameters. It processes a list of objects to determine how
   to cut them based on their geometry and the specified cutting type. The
   function handles different cutter types such as 'VCARVE', 'CYLCONE',
   'BALLCONE', and 'BALLNOSE', applying specific calculations for each. It
   also manages the layering and movement strategies for the cutting
   operation, including options for lead-ins, ramps, and bridges.

   :param o: An object containing parameters for the cutout operation,
             including cutter type, diameter, depth, and other settings.
   :type o: object

   :returns:

             This function does not return a value but performs operations
                 on the provided object.
   :rtype: None


.. py:function:: curve(o)
   :async:


   Process and convert curve objects into mesh chunks.

   This function takes an operation object and processes the curves
   contained within it. It first checks if all objects are curves; if not,
   it raises an exception. The function then converts the curves into
   chunks, sorts them, and refines them. If layers are to be used, it
   applies layer information to the chunks, adjusting their Z-offsets
   accordingly. Finally, it converts the processed chunks into a mesh.

   :param o: An object containing operation parameters, including a list of
             objects, flags for layer usage, and movement constraints.
   :type o: Operation

   :returns:

             This function does not return a value; it performs operations on the
                 input.
   :rtype: None

   :raises CamException: If not all objects in the operation are curves.


.. py:function:: project_curve(s, o)
   :async:


   Project a curve onto another curve object.

   This function takes a source object and a target object, both of which
   are expected to be curve objects. It projects the points of the source
   curve onto the target curve, adjusting the start and end points based on
   specified extensions. The resulting projected points are stored in the
   source object's path samples.

   :param s: The source object containing the curve to be projected.
   :type s: object
   :param o: An object containing references to the curve objects
             involved in the projection.
   :type o: object

   :returns:

             This function does not return a value; it modifies the
                 source object's path samples in place.
   :rtype: None

   :raises CamException: If the target curve is not of type 'CURVE'.


.. py:function:: pocket(o)
   :async:


   Perform pocketing operation based on the provided parameters.

   This function executes a pocketing operation using the specified
   parameters from the object `o`. It calculates the cutter offset based on
   the cutter type and depth, processes curves, and generates the necessary
   chunks for the pocketing operation. The function also handles various
   movement types and optimizations, including helix entry and retract
   movements.

   :param o: An object containing parameters for the pocketing
   :type o: object

   :returns: The function modifies the scene and generates geometry
             based on the pocketing operation.
   :rtype: None


.. py:function:: drill(o)
   :async:


   Perform a drilling operation on the specified objects.

   This function iterates through the objects in the provided context,
   activating each object and applying transformations. It duplicates the
   objects and processes them based on their type (CURVE or MESH). For
   CURVE objects, it calculates the bounding box and center points of the
   splines and bezier points, and generates chunks based on the specified
   drill type. For MESH objects, it generates chunks from the vertices. The
   function also manages layers and chunk depths for the drilling
   operation.

   :param o: An object containing properties and methods required
             for the drilling operation, including a list of
             objects to drill, drill type, and depth parameters.
   :type o: object

   :returns:

             This function does not return a value but performs operations
                 that modify the state of the Blender context.
   :rtype: None


.. py:function:: medial_axis(o)
   :async:


   Generate the medial axis for a given operation.

   This function computes the medial axis of the specified operation, which
   involves processing various cutter types and their parameters. It starts
   by removing any existing medial mesh, then calculates the maximum depth
   based on the cutter type and its properties. The function refines curves
   and computes the Voronoi diagram for the points derived from the
   operation's silhouette. It filters points and edges based on their
   positions relative to the computed shapes, and generates a mesh
   representation of the medial axis. Finally, it handles layers and
   optionally adds a pocket operation if specified.

   :param o: An object containing parameters for the operation, including
             cutter type, dimensions, and other relevant properties.
   :type o: Operation

   :returns: A dictionary indicating the completion status of the operation.
   :rtype: dict

   :raises CamException: If an unsupported cutter type is provided or if the input curve
       is not closed.


.. py:function:: get_layers(operation, startdepth, enddepth)

   Returns a list of layers bounded by start depth and end depth.

   This function calculates the layers between the specified start and end
   depths based on the step down value defined in the operation. If the
   operation is set to use layers, it computes the number of layers by
   dividing the difference between start and end depths by the step down
   value. The function raises an exception if the start depth is lower than
   the end depth.

   :param operation: An object that contains the properties `use_layers`,
                     `stepdown`, and `maxz` which are used to determine
                     how layers are generated.
   :type operation: object
   :param startdepth: The starting depth for layer calculation.
   :type startdepth: float
   :param enddepth: The ending depth for layer calculation.
   :type enddepth: float

   :returns:

             A list of layers, where each layer is represented as a list
                 containing the start and end depths of that layer.
   :rtype: list

   :raises CamException: If the start depth is lower than the end depth.


.. py:function:: chunks_to_mesh(chunks, o)

   Convert sampled chunks into a mesh path for a given optimization object.

   This function takes a list of sampled chunks and converts them into a
   mesh path based on the specified optimization parameters. It handles
   different machine axes configurations and applies optimizations as
   needed. The resulting mesh is created in the Blender context, and the
   function also manages the lifting and dropping of the cutter based on
   the chunk positions.

   :param chunks: A list of chunk objects to be converted into a mesh.
   :type chunks: list
   :param o: An object containing optimization parameters and settings.
   :type o: object

   :returns:

             The function creates a mesh in the Blender context but does not return a
                 value.
   :rtype: None


.. py:function:: check_min_z(o)

   Check the minimum value based on the specified condition.

   This function evaluates the 'minz_from' attribute of the input object
   'o'. If 'minz_from' is set to 'MATERIAL', it returns the value of
   'min.z'. Otherwise, it returns the value of 'minz'.

   :param o: An object that has attributes 'minz_from', 'min', and 'minz'.
   :type o: object

   :returns:

             The minimum value, which can be either 'o.min.z' or 'o.min_z' depending
                 on the condition.


