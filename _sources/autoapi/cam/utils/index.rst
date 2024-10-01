cam.utils
=========

.. py:module:: cam.utils

.. autoapi-nested-parse::

   BlenderCAM 'utils.py' © 2012 Vilem Novak

   Main functionality of BlenderCAM.
   The functions here are called with operators defined in 'ops.py'



Attributes
----------

.. autoapisummary::

   cam.utils.SHAPELY
   cam.utils.USE_PROFILER
   cam.utils.was_hidden_dict
   cam.utils._IS_LOADING_DEFAULTS


Classes
-------

.. autoapisummary::

   cam.utils.Point


Functions
---------

.. autoapisummary::

   cam.utils.opencamlib_version
   cam.utils.positionObject
   cam.utils.getBoundsWorldspace
   cam.utils.getSplineBounds
   cam.utils.getOperationSources
   cam.utils.getBounds
   cam.utils.getBoundsMultiple
   cam.utils.samplePathLow
   cam.utils.sampleChunks
   cam.utils.sampleChunksNAxis
   cam.utils.extendChunks5axis
   cam.utils.curveToShapely
   cam.utils.silhoueteOffset
   cam.utils.polygonBoolean
   cam.utils.polygonConvexHull
   cam.utils.Helix
   cam.utils.comparezlevel
   cam.utils.overlaps
   cam.utils.connectChunksLow
   cam.utils.getClosest
   cam.utils.sortChunks
   cam.utils.getVectorRight
   cam.utils.cleanUpDict
   cam.utils.dictRemove
   cam.utils.addLoop
   cam.utils.cutloops
   cam.utils.getOperationSilhouete
   cam.utils.getObjectSilhouete
   cam.utils.getAmbient
   cam.utils.getObjectOutline
   cam.utils.addOrientationObject
   cam.utils.removeOrientationObject
   cam.utils.addTranspMat
   cam.utils.addMachineAreaObject
   cam.utils.addMaterialAreaObject
   cam.utils.getContainer
   cam.utils.unique
   cam.utils.checkEqual
   cam.utils.prepareIndexed
   cam.utils.cleanupIndexed
   cam.utils.rotTo2axes
   cam.utils.reload_paths
   cam.utils.updateMachine
   cam.utils.updateMaterial
   cam.utils.updateOperation
   cam.utils.isValid
   cam.utils.operationValid
   cam.utils.isChainValid
   cam.utils.updateOperationValid
   cam.utils.updateChipload
   cam.utils.updateOffsetImage
   cam.utils.updateZbufferImage
   cam.utils.updateStrategy
   cam.utils.updateCutout
   cam.utils.updateExact
   cam.utils.updateOpencamlib
   cam.utils.updateBridges
   cam.utils.updateRotation
   cam.utils.updateRest
   cam.utils.getStrategyList
   cam.utils.update_material
   cam.utils.update_operation
   cam.utils.update_exact_mode
   cam.utils.update_opencamlib
   cam.utils.update_zbuffer_image
   cam.utils.check_operations_on_load
   cam.utils.Add_Pocket


Module Contents
---------------

.. py:data:: SHAPELY
   :value: True


.. py:function:: opencamlib_version()

   Return the version of the OpenCamLib library.

   This function attempts to import the OpenCamLib library and returns its
   version. If the library is not available, it will return None. The
   function first tries to import the library using the name 'ocl', and if
   that fails, it attempts to import it using 'opencamlib' as an alias. If
   both imports fail, it returns None.

   :returns: The version of OpenCamLib if available, None otherwise.
   :rtype: str or None


.. py:function:: positionObject(operation)

   Position an object based on specified operation parameters.

   This function adjusts the location of a Blender object according to the
   provided operation settings. It calculates the bounding box of the
   object in world space and modifies its position based on the material's
   center settings and specified z-positioning (BELOW, ABOVE, or CENTERED).
   The function also applies transformations to the object if it is not of
   type 'CURVE'.

   :param operation: An object containing parameters for positioning,
                     including object_name, use_modifiers, and material
                     settings.
   :type operation: OperationType


.. py:function:: getBoundsWorldspace(obs, use_modifiers=False)

   Get the bounding box of a list of objects in world space.

   This function calculates the minimum and maximum coordinates that
   encompass all the specified objects in the 3D world space. It iterates
   through each object, taking into account their transformations and
   modifiers if specified. The function supports different object types,
   including meshes and fonts, and handles the conversion of font objects
   to mesh format for accurate bounding box calculations.

   :param obs: A list of Blender objects to calculate bounds for.
   :type obs: list
   :param use_modifiers: If True, apply modifiers to the objects
                         before calculating bounds. Defaults to False.
   :type use_modifiers: bool

   :returns:

             A tuple containing the minimum and maximum coordinates
                 in the format (minx, miny, minz, maxx, maxy, maxz).
   :rtype: tuple

   :raises CamException: If an object type does not support CAM operations.


.. py:function:: getSplineBounds(ob, curve)

   Get the bounding box of a spline object.

   This function calculates the minimum and maximum coordinates (x, y, z)
   of the given spline object by iterating through its bezier points and
   regular points. It transforms the local coordinates to world coordinates
   using the object's transformation matrix. The resulting bounds can be
   used for various purposes, such as collision detection or rendering.

   :param ob: The object containing the spline whose bounds are to be calculated.
   :type ob: Object
   :param curve: The curve object that contains the bezier points and regular points.
   :type curve: Curve

   :returns: A tuple containing the minimum and maximum coordinates in the
             format (minx, miny, minz, maxx, maxy, maxz).
   :rtype: tuple


.. py:function:: getOperationSources(o)

   Get operation sources based on the geometry source type.

   This function retrieves and sets the operation sources for a given
   object based on its geometry source type. It handles three types of
   geometry sources: 'OBJECT', 'COLLECTION', and 'IMAGE'. For 'OBJECT', it
   selects the specified object and applies rotations if enabled. For
   'COLLECTION', it retrieves all objects within the specified collection.
   For 'IMAGE', it sets a specific optimization flag. Additionally, it
   determines whether the objects are curves or meshes based on the
   geometry source.

   :param o: An object containing properties such as geometry_source,
             object_name, collection_name, rotation_A, rotation_B,
             enable_A, enable_B, old_rotation_A, old_rotation_B,
             A_along_x, and optimisation.
   :type o: Object

   :returns:

             This function does not return a value but modifies the
                 properties of the input object.
   :rtype: None


.. py:function:: getBounds(o)

   Calculate the bounding box for a given object.

   This function determines the minimum and maximum coordinates of an
   object's bounding box based on its geometry source. It handles different
   geometry types such as OBJECT, COLLECTION, and CURVE. The function also
   considers material properties and image cropping if applicable. The
   bounding box is adjusted according to the object's material settings and
   the optimization parameters defined in the object.

   :param o: An object containing geometry and material properties, as well as
             optimization settings.
   :type o: object

   :returns:

             This function modifies the input object in place and does not return a
                 value.
   :rtype: None


.. py:function:: getBoundsMultiple(operations)

   Gets bounds of multiple operations for simulations or rest milling.

   This function iterates through a list of operations to determine the
   minimum and maximum bounds in three-dimensional space (x, y, z). It
   initializes the bounds to extreme values and updates them based on the
   bounds of each operation. The function is primarily intended for use in
   simulations or rest milling processes, although it is noted that the
   implementation may not be optimal.

   :param operations: A list of operation objects, each containing
                      'min' and 'max' attributes with 'x', 'y',
                      and 'z' coordinates.
   :type operations: list

   :returns:

             A tuple containing the minimum and maximum bounds in the
                 order (minx, miny, minz, maxx, maxy, maxz).
   :rtype: tuple


.. py:function:: samplePathLow(o, ch1, ch2, dosample)

   Generate a sample path between two channels.

   This function computes a series of points that form a path between two
   given channels. It calculates the direction vector from the end of the
   first channel to the start of the second channel and generates points
   along this vector up to a specified distance. If sampling is enabled, it
   modifies the z-coordinate of the generated points based on the cutter
   shape or image sampling, ensuring that the path accounts for any
   obstacles or features in the environment.

   :param o: An object containing optimization parameters and properties related to
             the path generation.
   :param ch1: The first channel object, which provides a point for the starting
               location of the path.
   :param ch2: The second channel object, which provides a point for the ending
               location of the path.
   :param dosample: A flag indicating whether to perform sampling along the generated path.
   :type dosample: bool

   :returns: An object representing the generated path points.
   :rtype: camPathChunk


.. py:function:: sampleChunks(o, pathSamples, layers)
   :async:


   Sample chunks of paths based on the provided parameters.

   This function processes the given path samples and layers to generate
   chunks of points that represent the sampled paths. It takes into account
   various optimization settings and strategies to determine how the points
   are sampled and organized into layers. The function handles different
   scenarios based on the object's properties and the specified layers,
   ensuring that the resulting chunks are correctly structured for further
   processing.

   :param o: An object containing various properties and settings
             related to the sampling process.
   :type o: object
   :param pathSamples: A list of path samples to be processed.
   :type pathSamples: list
   :param layers: A list of layers defining the z-coordinate ranges
                  for sampling.
   :type layers: list

   :returns:

             A list of sampled chunks, each containing points that represent
                 the sampled paths.
   :rtype: list


.. py:function:: sampleChunksNAxis(o, pathSamples, layers)
   :async:


   Sample chunks along a specified axis based on provided paths and layers.

   This function processes a set of path samples and organizes them into
   chunks according to specified layers. It prepares the collision world if
   necessary, updates the cutter's rotation based on the path samples, and
   handles the sampling of points along the paths. The function also
   manages the relationships between the sampled points and their
   respective layers, ensuring that the correct points are added to each
   chunk. The resulting chunks can be used for further processing in a 3D
   environment.

   :param o: An object containing properties such as min/max coordinates,
             cutter shape, and other relevant parameters.
   :type o: object
   :param pathSamples: A list of path samples, each containing start points,
                       end points, and rotations.
   :type pathSamples: list
   :param layers: A list of layer definitions that specify the boundaries
                  for sampling.
   :type layers: list

   :returns: A list of sampled chunks organized by layers.
   :rtype: list


.. py:function:: extendChunks5axis(chunks, o)

   Extend chunks with 5-axis cutter start and end points.

   This function modifies the provided chunks by appending calculated start
   and end points for a cutter based on the specified orientation and
   movement parameters. It determines the starting position of the cutter
   based on the machine's settings and the object's movement constraints.
   The function iterates through each point in the chunks and updates their
   start and end points accordingly.

   :param chunks: A list of chunk objects that will be modified.
   :type chunks: list
   :param o: An object containing movement and orientation data.
   :type o: object


.. py:function:: curveToShapely(cob, use_modifiers=False)

   Convert a curve object to Shapely polygons.

   This function takes a curve object and converts it into a list of
   Shapely polygons. It first breaks the curve into chunks and then
   transforms those chunks into Shapely-compatible polygon representations.
   The `use_modifiers` parameter allows for additional processing of the
   curve before conversion, depending on the specific requirements of the
   application.

   :param cob: The curve object to be converted.
   :param use_modifiers: A flag indicating whether to apply modifiers
                         during the conversion process. Defaults to False.
   :type use_modifiers: bool

   :returns: A list of Shapely polygons created from the curve object.
   :rtype: list


.. py:function:: silhoueteOffset(context, offset, style=1, mitrelimit=1.0)

   Offset the silhouette of a curve or font object in Blender.

   This function takes an active curve or font object in Blender and
   creates an offset silhouette based on the specified parameters. It first
   retrieves the silhouette of the object and then applies a buffer
   operation to create the offset shape. The resulting shape is then
   converted back into a curve object in the Blender scene.

   :param context: The current Blender context.
   :type context: bpy.context
   :param offset: The distance to offset the silhouette.
   :type offset: float
   :param style: The join style for the offset. Defaults to 1.
   :type style: int?
   :param mitrelimit: The mitre limit for the offset. Defaults to 1.0.
   :type mitrelimit: float?

   :returns: A dictionary indicating the operation is finished.
   :rtype: dict


.. py:function:: polygonBoolean(context, boolean_type)

   Perform a boolean operation on selected polygons.

   This function takes the active object and applies a specified boolean
   operation (UNION, DIFFERENCE, or INTERSECT) with respect to other
   selected objects in the Blender context. It first converts the polygons
   of the active object and the selected objects into a Shapely
   MultiPolygon. Depending on the boolean type specified, it performs the
   corresponding boolean operation and then converts the result back into a
   Blender curve.

   :param context: The Blender context containing scene and object data.
   :type context: bpy.context
   :param boolean_type: The type of boolean operation to perform.
                        Must be one of 'UNION', 'DIFFERENCE', or 'INTERSECT'.
   :type boolean_type: str

   :returns: A dictionary indicating the operation result, typically {'FINISHED'}.
   :rtype: dict


.. py:function:: polygonConvexHull(context)

   Generate the convex hull of a polygon from the given context.

   This function duplicates the current object, joins it, and converts it
   into a 3D mesh. It then extracts the X and Y coordinates of the vertices
   to create a MultiPoint data structure using Shapely. Finally, it
   computes the convex hull of these points and converts the result back
   into a curve named 'ConvexHull'. Temporary objects created during this
   process are deleted to maintain a clean workspace.

   :param context: The context in which the operation is performed, typically
                   related to Blender's current state.

   :returns: A dictionary indicating the operation's completion status.
   :rtype: dict


.. py:function:: Helix(r, np, zstart, pend, rev)

   Generate a helix of points in 3D space.

   This function calculates a series of points that form a helix based on
   the specified parameters. It starts from a given radius and
   z-coordinate, and generates points by rotating around the z-axis while
   moving linearly along the z-axis. The number of points generated is
   determined by the number of turns (revolutions) and the number of points
   per revolution.

   :param r: The radius of the helix.
   :type r: float
   :param np: The number of points per revolution.
   :type np: int
   :param zstart: The starting z-coordinate for the helix.
   :type zstart: float
   :param pend: A tuple containing the x, y, and z coordinates of the endpoint.
   :type pend: tuple
   :param rev: The number of revolutions to complete.
   :type rev: int

   :returns:

             A list of tuples representing the coordinates of the points in the
                 helix.
   :rtype: list


.. py:function:: comparezlevel(x)

.. py:function:: overlaps(bb1, bb2)

   Determine if one bounding box is a child of another.

   This function checks if the first bounding box (bb1) is completely
   contained within the second bounding box (bb2). It does this by
   comparing the coordinates of both bounding boxes to see if all corners
   of bb1 are within the bounds of bb2.

   :param bb1: A tuple representing the coordinates of the first bounding box
               in the format (x_min, y_min, x_max, y_max).
   :type bb1: tuple
   :param bb2: A tuple representing the coordinates of the second bounding box
               in the format (x_min, y_min, x_max, y_max).
   :type bb2: tuple

   :returns: True if bb1 is a child of bb2, otherwise False.
   :rtype: bool


.. py:function:: connectChunksLow(chunks, o)
   :async:


   Connects chunks that are close to each other without lifting, sampling
   them 'low'.

   This function processes a list of chunks and connects those that are
   within a specified distance based on the provided options. It takes into
   account various strategies for connecting the chunks, including 'CARVE',
   'PENCIL', and 'MEDIAL_AXIS', and adjusts the merging distance
   accordingly. The function also handles specific movement settings, such
   as whether to stay low or to merge distances, and may resample chunks if
   certain optimization conditions are met.

   :param chunks: A list of chunk objects to be connected.
   :type chunks: list
   :param o: An options object containing movement and strategy parameters.
   :type o: object

   :returns: A list of connected chunk objects.
   :rtype: list


.. py:function:: getClosest(o, pos, chunks)

   Find the closest chunk to a given position.

   This function iterates through a list of chunks and determines which
   chunk is closest to the specified position. It checks if each chunk's
   children are sorted before calculating the distance. The chunk with the
   minimum distance to the given position is returned.

   :param o: An object representing the origin point.
   :param pos: A position to which the closest chunk is calculated.
   :param chunks: A list of chunk objects to evaluate.
   :type chunks: list

   :returns:

             The closest chunk object to the specified position, or None if no valid
                 chunk is found.
   :rtype: Chunk


.. py:function:: sortChunks(chunks, o, last_pos=None)
   :async:


   Sort a list of chunks based on a specified strategy.

   This function sorts a list of chunks according to the provided options
   and the current position. It utilizes a recursive approach to find the
   closest chunk to the current position and adapts its distance if it has
   not been sorted before. The function also handles progress updates
   asynchronously and adjusts the recursion limit to accommodate deep
   recursion scenarios.

   :param chunks: A list of chunk objects to be sorted.
   :type chunks: list
   :param o: An options object that contains sorting strategy and other parameters.
   :type o: object
   :param last_pos: The last known position as a tuple of coordinates.
                    Defaults to None, which initializes the position to (0, 0, 0).
   :type last_pos: tuple?

   :returns: A sorted list of chunk objects.
   :rtype: list


.. py:function:: getVectorRight(lastv, verts)

   Get the index of the vector that is most to the right based on angle.

   This function calculates the angle between a reference vector (formed by
   the last two vectors in `lastv`) and each vector in the `verts` list. It
   identifies the vector that has the smallest angle with respect to the
   reference vector, indicating that it is the most rightward vector in
   relation to the specified direction.

   :param lastv: A list containing two vectors, where each vector is
                 represented as a tuple or list of coordinates.
   :type lastv: list
   :param verts: A list of vectors represented as tuples or lists of
                 coordinates.
   :type verts: list

   :returns:

             The index of the vector in `verts` that is most to the right
                 based on the calculated angle.
   :rtype: int


.. py:function:: cleanUpDict(ndict)

   Remove lonely points from a dictionary.

   This function iterates over the keys of the provided dictionary and
   removes any entries that contain one or fewer associated values. It
   continues to check for and remove "lonely" points until no more can be
   found. The process is repeated until all such entries are eliminated
   from the dictionary.

   :param ndict: A dictionary where keys are associated with lists of values.
   :type ndict: dict

   :returns:

             This function modifies the input dictionary in place and does not return
                 a value.
   :rtype: None


.. py:function:: dictRemove(dict, val)

   Remove a key and its associated values from a dictionary.

   This function takes a dictionary and a key (val) as input. It iterates
   through the list of values associated with the given key and removes the
   key from each of those values' lists. Finally, it removes the key itself
   from the dictionary.

   :param dict: A dictionary where the key is associated with a list of values.
   :type dict: dict
   :param val: The key to be removed from the dictionary and from the lists of its
               associated values.


.. py:function:: addLoop(parentloop, start, end)

   Add a loop to a parent loop structure.

   This function recursively checks if the specified start and end values
   can be added as a new loop to the parent loop. If an existing loop
   encompasses the new loop, it will call itself on that loop. If no such
   loop exists, it appends the new loop defined by the start and end values
   to the parent loop's list of loops.

   :param parentloop: A list representing the parent loop, where the
                      third element is a list of child loops.
   :type parentloop: list
   :param start: The starting value of the new loop to be added.
   :type start: int
   :param end: The ending value of the new loop to be added.
   :type end: int

   :returns:

             This function modifies the parentloop in place and does not
                 return a value.
   :rtype: None


.. py:function:: cutloops(csource, parentloop, loops)

   Cut loops from a source code segment.

   This function takes a source code segment and a parent loop defined by
   its start and end indices, along with a list of nested loops. It creates
   a copy of the source code segment and removes the specified nested loops
   from it. The modified segment is then appended to the provided list of
   loops. The function also recursively processes any nested loops found
   within the parent loop.

   :param csource: The source code from which loops will be cut.
   :type csource: str
   :param parentloop: A tuple containing the start index, end index, and a list of nested
                      loops.
                      The list of nested loops should contain tuples with start and end
                      indices for each loop.
   :type parentloop: tuple
   :param loops: A list that will be populated with the modified source code segments
                 after
                 removing the specified loops.
   :type loops: list

   :returns:

             This function modifies the `loops` list in place and does not return a
                 value.
   :rtype: None


.. py:function:: getOperationSilhouete(operation)

   Gets the silhouette for the given operation.

   This function determines the silhouette of an operation using image
   thresholding techniques. It handles different geometry sources, such as
   objects or images, and applies specific methods based on the type of
   geometry. If the geometry source is 'OBJECT' or 'COLLECTION', it checks
   whether to process curves or not. The function also considers the number
   of faces in mesh objects to decide on the appropriate method for
   silhouette extraction.

   :param operation: An object containing the necessary data
   :type operation: Operation

   :returns: The computed silhouette for the operation.
   :rtype: Silhouette


.. py:function:: getObjectSilhouete(stype, objects=None, use_modifiers=False)

   Get the silhouette of objects based on the specified type.

   This function computes the silhouette of a given set of objects in
   Blender based on the specified type. It can handle both curves and mesh
   objects, converting curves to polygon format and calculating the
   silhouette for mesh objects. The function also considers the use of
   modifiers if specified. The silhouette is generated by processing the
   geometry of the objects and returning a Shapely representation of the
   silhouette.

   :param stype: The type of silhouette to generate ('CURVES' or 'OBJECTS').
   :type stype: str
   :param objects: A list of Blender objects to process. Defaults to None.
   :type objects: list?
   :param use_modifiers: Whether to apply modifiers to the objects. Defaults to False.
   :type use_modifiers: bool?

   :returns: The computed silhouette as a Shapely MultiPolygon.
   :rtype: shapely.geometry.MultiPolygon


.. py:function:: getAmbient(o)

   Calculate and update the ambient geometry based on the provided object.

   This function computes the ambient shape for a given object based on its
   properties, such as cutter restrictions and ambient behavior. It
   determines the appropriate radius and creates the ambient geometry
   either from the silhouette or as a polygon defined by the object's
   minimum and maximum coordinates. If a limit curve is specified, it will
   also intersect the ambient shape with the limit polygon.

   :param o: An object containing properties that define the ambient behavior,
             cutter restrictions, and limit curve.
   :type o: object

   :returns: The function updates the ambient property of the object in place.
   :rtype: None


.. py:function:: getObjectOutline(radius, o, Offset)

   Get the outline of a geometric object based on specified parameters.

   This function generates an outline for a given geometric object by
   applying a buffer operation to its polygons. The buffer radius can be
   adjusted based on the `radius` parameter, and the operation can be
   offset based on the `Offset` flag. The function also considers whether
   the polygons should be merged or not, depending on the properties of the
   object `o`.

   :param radius: The radius for the buffer operation.
   :type radius: float
   :param o: An object containing properties that influence the outline generation.
   :type o: object
   :param Offset: A flag indicating whether to apply a positive or negative offset.
   :type Offset: bool

   :returns: The resulting outline of the geometric object as a MultiPolygon.
   :rtype: MultiPolygon


.. py:function:: addOrientationObject(o)

   Set up orientation for a milling object.

   This function creates an orientation object in the Blender scene for
   4-axis and 5-axis milling operations. It checks if an orientation object
   with the specified name already exists, and if not, it adds a new empty
   object of type 'ARROWS'. The function then configures the rotation locks
   and initial rotation angles based on the specified machine axes and
   rotary axis.

   :param o: An object containing properties such as name,
   :type o: object


.. py:function:: removeOrientationObject(o)

   Remove an orientation object from the current Blender scene.

   This function constructs the name of the orientation object based on the
   name of the provided object and attempts to find and delete it from the
   Blender scene. If the orientation object exists, it will be removed
   using the `delob` function.

   :param o: The object whose orientation object is to be removed.
   :type o: Object


.. py:function:: addTranspMat(ob, mname, color, alpha)

   Add a transparent material to a given object.

   This function checks if a material with the specified name already
   exists in the Blender data. If it does, it retrieves that material; if
   not, it creates a new material with the given name and enables the use
   of nodes. The function then assigns the material to the specified
   object, ensuring that it is applied correctly whether the object already
   has materials or not.

   :param ob: The Blender object to which the material will be assigned.
   :type ob: bpy.types.Object
   :param mname: The name of the material to be added or retrieved.
   :type mname: str
   :param color: The RGBA color value for the material (not used in this function).
   :type color: tuple
   :param alpha: The transparency value for the material (not used in this function).
   :type alpha: float


.. py:function:: addMachineAreaObject()

   Add a machine area object to the current Blender scene.

   This function checks if a machine object named 'CAM_machine' already
   exists in the current scene. If it does not exist, it creates a new cube
   mesh object, applies transformations, and modifies its geometry to
   represent a machine area. The function ensures that the scene's unit
   settings are set to metric before creating the object and restores the
   original unit settings afterward. It also configures the display
   properties of the object for better visibility in the scene.  The
   function operates within Blender's context and utilizes various Blender
   operations to create and modify the mesh. It also handles the selection
   state of the active object.


.. py:function:: addMaterialAreaObject()

   Add a material area object to the current Blender scene.

   This function checks if a material area object named 'CAM_material'
   already exists in the current scene. If it does, it retrieves that
   object; if not, it creates a new cube mesh object to serve as the
   material area. The dimensions and location of the object are set based
   on the current camera operation's bounds. The function also applies
   transformations to ensure the object's location and dimensions are
   correctly set.  The created or retrieved object is configured to be non-
   renderable and non-selectable in the viewport, while still being
   selectable for operations. This is useful for visualizing the working
   area of the camera without affecting the render output.  Raises:
   None


.. py:function:: getContainer()

   Get or create a container object for camera objects.

   This function checks if a container object named 'CAM_OBJECTS' exists in
   the current Blender scene. If it does not exist, the function creates a
   new empty object of type 'PLAIN_AXES', names it 'CAM_OBJECTS', and sets
   its location to the origin (0, 0, 0). The newly created container is
   also hidden. If the container already exists, it simply retrieves and
   returns that object.

   :returns:

             The container object for camera objects, either newly created or
                 existing.
   :rtype: bpy.types.Object


.. py:class:: Point(x, y, z)

.. py:function:: unique(L)

   Return a list of unhashable elements in L, but without duplicates.

   This function processes a list of lists, specifically designed to handle
   unhashable elements. It sorts the input list and removes duplicates by
   comparing the elements based on their coordinates. The function counts
   the number of duplicate vertices and the number of collinear points
   along the Z-axis.

   :param L: A list of lists, where each inner list represents a point
   :type L: list

   :returns:

             A tuple containing two integers:
                 - The first integer represents the count of duplicate vertices.
                 - The second integer represents the count of Z-collinear points.
   :rtype: tuple


.. py:function:: checkEqual(lst)

.. py:function:: prepareIndexed(o)

   Prepare and index objects in the given collection.

   This function stores the world matrices and parent relationships of the
   objects in the provided collection. It then clears the parent
   relationships while maintaining their transformations, sets the
   orientation of the objects based on a specified orientation object, and
   finally re-establishes the parent-child relationships with the
   orientation object. The function also resets the location and rotation
   of the orientation object to the origin.

   :param o: A collection of objects to be prepared and indexed.
   :type o: ObjectCollection


.. py:function:: cleanupIndexed(operation)

   Clean up indexed operations by updating object orientations and paths.

   This function takes an operation object and updates the orientation of a
   specified object in the scene based on the provided orientation matrix.
   It also sets the location and rotation of a camera path object to match
   the updated orientation. Additionally, it reassigns parent-child
   relationships for the objects involved in the operation and updates
   their world matrices.

   :param operation: An object containing the necessary data
   :type operation: OperationType


.. py:function:: rotTo2axes(e, axescombination)

   Converts an Orientation Object Rotation to Rotation Defined by 2
   Rotational Axes on the Machine.

   This function takes an orientation object and a specified axes
   combination, and computes the angles of rotation around two axes based
   on the provided orientation. It supports different axes combinations for
   indexed machining. The function utilizes vector mathematics to determine
   the angles of rotation and returns them as a tuple.

   :param e: The orientation object representing the rotation.
   :type e: OrientationObject
   :param axescombination: A string indicating the axes combination ('CA' or 'CB').
   :type axescombination: str

   :returns: A tuple containing two angles (float) representing the rotation
             around the specified axes.
   :rtype: tuple


.. py:function:: reload_paths(o)

   Reload the camera path data from a pickle file.

   This function retrieves the camera path data associated with the given
   object `o`. It constructs a new mesh from the path vertices and updates
   the object's properties with the loaded data. If a previous path mesh
   exists, it is removed to avoid memory leaks. The function also handles
   the creation of a new mesh object if one does not already exist in the
   current scene.

   :param o: The object for which the camera path is being
   :type o: Object


.. py:data:: USE_PROFILER
   :value: False


.. py:data:: was_hidden_dict

.. py:data:: _IS_LOADING_DEFAULTS
   :value: False


.. py:function:: updateMachine(self, context)

   Update the machine with the given context.

   This function is responsible for updating the machine state based on the
   provided context. It prints a message indicating that the update process
   has started. If the global variable _IS_LOADING_DEFAULTS is not set to
   True, it proceeds to add a machine area object.

   :param context: The context in which the machine update is being performed.


.. py:function:: updateMaterial(self, context)

   Update the material in the given context.

   This method is responsible for updating the material based on the
   provided context. It performs necessary operations to ensure that the
   material is updated correctly. Currently, it prints a message indicating
   the update process and calls the `addMaterialAreaObject` function to
   handle additional material area object updates.

   :param context: The context in which the material update is performed.


.. py:function:: updateOperation(self, context)

   Update the visibility and selection state of camera operations in the
   scene.

   This method manages the visibility of objects associated with camera
   operations based on the current active operation. If the
   'hide_all_others' flag is set to true, it hides all other objects except
   for the currently active one. If the flag is false, it restores the
   visibility of previously hidden objects. The method also attempts to
   highlight the currently active object in the 3D view and make it the
   active object in the scene.

   :param context: The context containing the current scene and
   :type context: bpy.types.Context


.. py:function:: isValid(o, context)

   Check the validity of a geometry source.

   This function verifies if the provided geometry source is valid based on
   its type. It checks for three types of geometry sources: 'OBJECT',
   'COLLECTION', and 'IMAGE'. For 'OBJECT', it ensures that the object name
   ends with '_cut_bridges' or exists in the Blender data objects. For
   'COLLECTION', it checks if the collection name exists and contains
   objects. For 'IMAGE', it verifies if the source image name exists in the
   Blender data images.

   :param o: An object containing geometry source information, including
             attributes like `geometry_source`, `object_name`, `collection_name`,
             and `source_image_name`.
   :type o: object
   :param context: The context in which the validation is performed (not used in this
                   function).

   :returns: True if the geometry source is valid, False otherwise.
   :rtype: bool


.. py:function:: operationValid(self, context)

   Validate the current camera operation in the given context.

   This method checks if the active camera operation is valid based on the
   current scene context. It updates the operation's validity status and
   provides warnings if the source object is invalid. Additionally, it
   configures specific settings related to image geometry sources.

   :param context: The context containing the scene and camera operations.
   :type context: Context


.. py:function:: isChainValid(chain, context)

   Check the validity of a chain of operations within a given context.

   This function verifies if all operations in the provided chain are valid
   according to the current scene context. It first checks if the chain
   contains any operations. If it does, it iterates through each operation
   in the chain and checks if it exists in the scene's camera operations.
   If an operation is not found or is deemed invalid, the function returns
   a tuple indicating the failure and provides an appropriate error
   message. If all operations are valid, it returns a success indication.

   :param chain: The chain of operations to validate.
   :type chain: Chain
   :param context: The context containing the scene and camera operations.
   :type context: Context

   :returns:

             A tuple containing a boolean indicating validity and an error message
                 (if any). The first element is True if valid, otherwise False. The
                 second element is an error message string.
   :rtype: tuple


.. py:function:: updateOperationValid(self, context)

.. py:function:: updateChipload(self, context)

   Update the chipload based on feedrate, spindle RPM, and cutter
   parameters.

   This function calculates the chipload using the formula: chipload =
   feedrate / (spindle_rpm * cutter_flutes). It also attempts to account
   for chip thinning when cutting at less than 50% cutter engagement with
   cylindrical end mills by combining two formulas. The first formula
   provides the nominal chipload based on standard recommendations, while
   the second formula adjusts for the cutter diameter and distance between
   paths.  The current implementation may not yield consistent results, and
   there are concerns regarding the correctness of the units used in the
   calculations. Further review and refinement of this function may be
   necessary to improve accuracy and reliability.

   :param context: The context in which the update is performed (not used in this
                   implementation).

   :returns: This function does not return a value; it updates the chipload in place.
   :rtype: None


.. py:function:: updateOffsetImage(self, context)

   Refresh the Offset Image Tag for re-rendering.

   This method updates the chip load and marks the offset image tag for re-
   rendering. It sets the `changed` attribute to True and indicates that
   the offset image tag needs to be updated.

   :param context: The context in which the update is performed.


.. py:function:: updateZbufferImage(self, context)

   Update the Z-buffer and offset image tags for recalculation.

   This method modifies the internal state to indicate that the Z-buffer
   image and offset image tags need to be updated during the calculation
   process. It sets the `changed` attribute to True and marks the relevant
   tags for updating. Additionally, it calls the `getOperationSources`
   function to ensure that the necessary operation sources are retrieved.

   :param context: The context in which the update is being performed.


.. py:function:: updateStrategy(o, context)

   Update the strategy of the given object.

   This function modifies the state of the object `o` by setting its
   `changed` attribute to True and printing a message indicating that the
   strategy is being updated. Depending on the value of `machine_axes` and
   `strategy4axis`, it either adds or removes an orientation object
   associated with `o`. Finally, it calls the `updateExact` function to
   perform further updates based on the provided context.

   :param o: The object whose strategy is to be updated.
   :type o: object
   :param context: The context in which the update is performed.
   :type context: object


.. py:function:: updateCutout(o, context)

.. py:function:: updateExact(o, context)

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


.. py:function:: updateOpencamlib(o, context)

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


.. py:function:: updateBridges(o, context)

   Update the status of bridges.

   This function marks the bridge object as changed, indicating that an
   update has occurred. It prints a message to the console for logging
   purposes. The function takes in an object and a context, but the context
   is not utilized within the function.

   :param o: The bridge object that needs to be updated.
   :type o: object
   :param context: Additional context for the update, not used in this function.
   :type context: object


.. py:function:: updateRotation(o, context)

   Update the rotation of a specified object in Blender.

   This function modifies the rotation of a Blender object based on the
   properties of the provided object 'o'. It checks which rotations are
   enabled and applies the corresponding rotation values to the active
   object in the scene. The rotation can be aligned either along the X or Y
   axis, depending on the configuration of 'o'.

   :param o: An object containing rotation settings and flags.
   :type o: object
   :param context: The context in which the operation is performed.
   :type context: object


.. py:function:: updateRest(o, context)

   Update the state of the object.

   This function modifies the given object by setting its 'changed'
   attribute to True. It also prints a message indicating that the update
   operation has been performed.

   :param o: The object to be updated.
   :type o: object
   :param context: The context in which the update is being performed.
   :type context: object


.. py:function:: getStrategyList(scene, context)

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


.. py:function:: update_material(self, context)

.. py:function:: update_operation(self, context)

   Update the camera operation based on the current context.

   This function retrieves the active camera operation from the Blender
   context and updates it using the `updateRest` function. It accesses the
   active operation from the scene's camera operations and passes the
   current context to the updating function.

   :param context: The context in which the operation is being updated.


.. py:function:: update_exact_mode(self, context)

   Update the exact mode of the active camera operation.

   This function retrieves the currently active camera operation from the
   Blender context and updates its exact mode using the `updateExact`
   function. It accesses the active operation through the `cam_operations`
   list in the current scene and passes the active operation along with the
   current context to the `updateExact` function.

   :param context: The context in which the update is performed.


.. py:function:: update_opencamlib(self, context)

   Update the OpenCamLib with the current active operation.

   This function retrieves the currently active camera operation from the
   Blender context and updates the OpenCamLib accordingly. It accesses the
   active operation from the scene's camera operations and passes it along
   with the current context to the update function.

   :param context: The context in which the operation is being performed, typically
                   provided by
                   Blender's internal API.


.. py:function:: update_zbuffer_image(self, context)

   Update the Z-buffer image based on the active camera operation.

   This function retrieves the currently active camera operation from the
   Blender context and updates the Z-buffer image accordingly. It accesses
   the scene's camera operations and invokes the `updateZbufferImage`
   function with the active operation and context.

   :param context: The current Blender context.
   :type context: bpy.context


.. py:function:: check_operations_on_load(context)

   Checks for any broken computations on load and resets them.

   This function verifies the presence of necessary Blender add-ons and
   installs any that are missing. It also resets any ongoing computations
   in camera operations and sets the interface level to the previously used
   level when loading a new file. If the add-on has been updated, it copies
   the necessary presets from the source to the target directory.
   Additionally, it checks for updates to the camera plugin and updates
   operation presets if required.

   :param context: The context in which the function is executed, typically containing
                   information about
                   the current Blender environment.


.. py:function:: Add_Pocket(self, maxdepth, sname, new_cutter_diameter)

   Add a pocket operation for the medial axis and profile cut.

   This function first deselects all objects in the scene and then checks
   for any existing medial pocket objects, deleting them if found. It
   verifies whether a medial pocket operation already exists in the camera
   operations. If it does not exist, it creates a new pocket operation with
   the specified parameters. The function also modifies the selected
   object's silhouette offset based on the new cutter diameter.

   :param maxdepth: The maximum depth of the pocket to be created.
   :type maxdepth: float
   :param sname: The name of the object to which the pocket will be added.
   :type sname: str
   :param new_cutter_diameter: The diameter of the new cutter to be used.
   :type new_cutter_diameter: float


