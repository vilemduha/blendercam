fabex.utilities.simple_utils
============================

.. py:module:: fabex.utilities.simple_utils

.. autoapi-nested-parse::

   Fabex 'simple_utils.py' © 2012 Vilem Novak

   Various helper functions, less complex than those found in the 'utils' files.



Functions
---------

.. autoapisummary::

   fabex.utilities.simple_utils.tuple_add
   fabex.utilities.simple_utils.tuple_subtract
   fabex.utilities.simple_utils.tuple_multiply
   fabex.utilities.simple_utils.tuple_length
   fabex.utilities.simple_utils.timing_init
   fabex.utilities.simple_utils.timing_start
   fabex.utilities.simple_utils.timing_add
   fabex.utilities.simple_utils.timing_print
   fabex.utilities.simple_utils.progress
   fabex.utilities.simple_utils.activate
   fabex.utilities.simple_utils.distance_2d
   fabex.utilities.simple_utils.delete_object
   fabex.utilities.simple_utils.duplicate_object
   fabex.utilities.simple_utils.add_to_group
   fabex.utilities.simple_utils.compare
   fabex.utilities.simple_utils.is_vertical_limit
   fabex.utilities.simple_utils.get_cache_path
   fabex.utilities.simple_utils.get_simulation_path
   fabex.utilities.simple_utils.safe_filename
   fabex.utilities.simple_utils.unit_value_to_string
   fabex.utilities.simple_utils.select_multiple
   fabex.utilities.simple_utils.join_multiple
   fabex.utilities.simple_utils.remove_multiple
   fabex.utilities.simple_utils.deselect
   fabex.utilities.simple_utils.make_active
   fabex.utilities.simple_utils.active_name
   fabex.utilities.simple_utils.rename
   fabex.utilities.simple_utils.union
   fabex.utilities.simple_utils.intersect
   fabex.utilities.simple_utils.difference
   fabex.utilities.simple_utils.duplicate
   fabex.utilities.simple_utils.mirror_x
   fabex.utilities.simple_utils.mirror_y
   fabex.utilities.simple_utils.move
   fabex.utilities.simple_utils.rotate
   fabex.utilities.simple_utils.remove_doubles
   fabex.utilities.simple_utils.add_overcut
   fabex.utilities.simple_utils.add_bound_rectangle
   fabex.utilities.simple_utils.add_rectangle
   fabex.utilities.simple_utils.active_to_coords
   fabex.utilities.simple_utils.active_to_shapely_poly
   fabex.utilities.simple_utils.make_visible
   fabex.utilities.simple_utils.restore_visibility
   fabex.utilities.simple_utils.subdivide_short_lines
   fabex.utilities.simple_utils.subdivide_long_edges
   fabex.utilities.simple_utils.dilate_array
   fabex.utilities.simple_utils.rotate_point_by_point


Module Contents
---------------

.. py:function:: tuple_add(t, t1)

   Add two tuples as vectors.

   This function takes two tuples, each representing a vector in three-
   dimensional space, and returns a new tuple that is the element-wise sum
   of the two input tuples. It assumes that both tuples contain exactly
   three numeric elements.

   :param t: A tuple containing three numeric values representing the first vector.
   :type t: tuple
   :param t1: A tuple containing three numeric values representing the second vector.
   :type t1: tuple

   :returns:

             A tuple containing three numeric values that represent the sum of the
                 input vectors.
   :rtype: tuple


.. py:function:: tuple_subtract(t, t1)

   Subtract two tuples element-wise.

   This function takes two tuples of three elements each and performs an
   element-wise subtraction, treating the tuples as vectors. The result is
   a new tuple containing the differences of the corresponding elements
   from the input tuples.

   :param t: A tuple containing three numeric values.
   :type t: tuple
   :param t1: A tuple containing three numeric values.
   :type t1: tuple

   :returns: A tuple containing the results of the element-wise subtraction.
   :rtype: tuple


.. py:function:: tuple_multiply(t, c)

   Multiply each element of a tuple by a given number.

   This function takes a tuple containing three elements and a numeric
   value, then multiplies each element of the tuple by the provided number.
   The result is returned as a new tuple containing the multiplied values.

   :param t: A tuple containing three numeric values.
   :type t: tuple
   :param c: A number by which to multiply each element of the tuple.
   :type c: numeric

   :returns: A new tuple containing the results of the multiplication.
   :rtype: tuple


.. py:function:: tuple_length(t)

   Get the length of a vector represented as a tuple.

   This function takes a tuple as input, which represents the coordinates
   of a vector, and returns its length by creating a Vector object from the
   tuple. The length is calculated using the appropriate mathematical
   formula for vector length.

   :param t: A tuple representing the coordinates of the vector.
   :type t: tuple

   :returns: The length of the vector.
   :rtype: float


.. py:function:: timing_init()

   Initialize timing metrics.

   This function sets up the initial state for timing functions by
   returning a list containing two zero values. These values can be used to
   track elapsed time or other timing-related metrics in subsequent
   operations.

   :returns: A list containing two zero values, representing the
             initial timing metrics.
   :rtype: list


.. py:function:: timing_start(tinf)

   Start timing by recording the current time.

   This function updates the second element of the provided list with the
   current time in seconds since the epoch. It is useful for tracking the
   start time of an operation or process.

   :param tinf: A list where the second element will be updated
                with the current time.
   :type tinf: list


.. py:function:: timing_add(tinf)

   Update the timing information.

   This function updates the first element of the `tinf` list by adding the
   difference between the current time and the second element of the list.
   It is typically used to track elapsed time in a timing context.

   :param tinf: A list where the first element is updated with the
   :type tinf: list


.. py:function:: timing_print(tinf)

   Print the timing information.

   This function takes a tuple containing timing information and prints it
   in a formatted string. It specifically extracts the first element of the
   tuple, which is expected to represent time, and appends the string
   'seconds' to it before printing.

   :param tinf: A tuple where the first element is expected to be a numeric value
                representing time.
   :type tinf: tuple

   :returns:

             This function does not return any value; it only prints output to the
                 console.
   :rtype: None


.. py:function:: progress(text, n=None)

   Report progress during script execution.

   This function outputs a progress message to the standard output. It is
   designed to work for background operations and provides a formatted
   string that includes the specified text and an optional numeric progress
   value. If the numeric value is provided, it is formatted as a
   percentage.

   :param text: The message to display as progress.
   :type text: str
   :param n: A float representing the progress as a
             fraction (0.0 to 1.0). If not provided, no percentage will
             be displayed.
   :type n: float?

   :returns:

             This function does not return a value; it only prints
                 to the standard output.
   :rtype: None


.. py:function:: activate(o)

   Makes an object active in Blender.

   This function sets the specified object as the active object in the
   current Blender scene. It first deselects all objects, then selects the
   given object and makes it the active object in the view layer. This is
   useful for operations that require a specific object to be active, such
   as transformations or modifications.

   :param o: The Blender object to be activated.
   :type o: bpy.types.Object


.. py:function:: distance_2d(v1, v2)

   Calculate the distance between two points in 2D space.

   This function computes the Euclidean distance between two points
   represented by their coordinates in a 2D plane. It uses the Pythagorean
   theorem to calculate the distance based on the differences in the x and
   y coordinates of the points.

   :param v1: A tuple representing the coordinates of the first point (x1, y1).
   :type v1: tuple
   :param v2: A tuple representing the coordinates of the second point (x2, y2).
   :type v2: tuple

   :returns: The Euclidean distance between the two points.
   :rtype: float


.. py:function:: delete_object(ob)

   Delete an object in Blender for multiple uses.

   This function activates the specified object and then deletes it using
   Blender's built-in operations. It is designed to facilitate the deletion
   of objects within the Blender environment, ensuring that the object is
   active before performing the deletion operation.

   :param ob: The Blender object to be deleted.
   :type ob: Object


.. py:function:: duplicate_object(o, pos)

   Helper function for visualizing cutter positions in bullet simulation.

   This function duplicates the specified object and resizes it according
   to a predefined scale factor. It also removes any existing rigidbody
   properties from the duplicated object and sets its location to the
   specified position. This is useful for managing multiple cutter
   positions in a bullet simulation environment.

   :param o: The object to be duplicated.
   :type o: Object
   :param pos: The new position to place the duplicated object.
   :type pos: Vector


.. py:function:: add_to_group(ob, groupname)

   Add an object to a specified group in Blender.

   This function activates the given object and checks if the specified
   group exists in Blender's data. If the group does not exist, it creates
   a new group with the provided name. If the group already exists, it
   links the object to that group.

   :param ob: The object to be added to the group.
   :type ob: Object
   :param groupname: The name of the group to which the object will be added.
   :type groupname: str


.. py:function:: compare(v1, v2, vmiddle, e)

   Comparison for optimization of paths.

   This function compares two vectors and checks if the distance between a
   calculated vector and a reference vector is less than a specified
   threshold. It normalizes the vector difference and scales it by the
   length of another vector to determine if the resulting vector is within
   the specified epsilon value.

   :param v1: The first vector for comparison.
   :type v1: Vector
   :param v2: The second vector for comparison.
   :type v2: Vector
   :param vmiddle: The middle vector used for calculating the
                   reference vector.
   :type vmiddle: Vector
   :param e: The threshold value for comparison.
   :type e: float

   :returns:

             True if the distance is less than the threshold,
                 otherwise False.
   :rtype: bool


.. py:function:: is_vertical_limit(v1, v2, limit)

   Test Path Segment on Verticality Threshold for protect_vertical option.

   This function evaluates the verticality of a path segment defined by two
   points, v1 and v2, based on a specified limit. It calculates the angle
   between the vertical vector and the vector formed by the two points. If
   the angle is within the defined limit, it adjusts the vertical position
   of either v1 or v2 to ensure that the segment adheres to the verticality
   threshold.

   :param v1: A 3D point represented as a tuple (x, y, z).
   :type v1: tuple
   :param v2: A 3D point represented as a tuple (x, y, z).
   :type v2: tuple
   :param limit: The angle threshold for determining verticality.
   :type limit: float

   :returns: The adjusted 3D points v1 and v2 after evaluating the verticality.
   :rtype: tuple


.. py:function:: get_cache_path(o)

   Get the cache path for a given object.

   This function constructs a cache path based on the current Blender
   file's filepath and the name of the provided object. It retrieves the
   base name of the file, removes the last six characters, and appends a
   specified directory and the object's name to create a complete cache
   path.

   :param o: The Blender object for which the cache path is being generated.
   :type o: Object

   :returns: The constructed cache path as a string.
   :rtype: str


.. py:function:: get_simulation_path()

   Get the simulation path for temporary CAM files.

   This function retrieves the file path of the current Blender project and
   constructs a new path for temporary CAM files by appending 'temp_cam'
   to the directory of the current file. The constructed path is returned
   as a string.

   :returns: The path to the temporary CAM directory.
   :rtype: str


.. py:function:: safe_filename(name)

   Generate a safe file name from the given string.

   This function takes a string input and removes any characters that are
   not considered valid for file names. The valid characters include
   letters, digits, and a few special characters. The resulting string can
   be used safely as a file name for exporting purposes.

   :param name: The input string to be sanitized into a safe file name.
   :type name: str

   :returns: A sanitized version of the input string that contains only valid
             characters for a file name.
   :rtype: str


.. py:function:: unit_value_to_string(x, precision=5)

   Convert a value to a string representation in the current unit system.

   This function takes a numeric value and converts it to a string
   formatted according to the unit system set in the Blender context. If
   the unit system is metric, the value is converted to millimeters. If the
   unit system is imperial, the value is converted to inches. The precision
   of the output can be specified.

   :param x: The numeric value to be converted.
   :type x: float
   :param precision: The number of decimal places to round to.
                     Defaults to 5.
   :type precision: int?

   :returns: The string representation of the value in the appropriate units.
   :rtype: str


.. py:function:: select_multiple(name)

   Select multiple objects in the scene based on their names.

   This function deselects all objects in the current Blender scene and
   then selects all objects whose names start with the specified prefix. It
   iterates through all objects in the scene and checks if their names
   begin with the given string. If they do, those objects are selected;
   otherwise, they are deselected.

   :param name: The prefix used to select objects in the scene.
   :type name: str


.. py:function:: join_multiple(name)

   Join multiple objects and rename the final object.

   This function selects multiple objects in the Blender context, joins
   them into a single object, and renames the resulting object to the
   specified name. It is assumed that the objects to be joined are already
   selected in the Blender interface.

   :param name: The new name for the joined object.
   :type name: str


.. py:function:: remove_multiple(name)

   Remove multiple objects from the scene based on their name prefix.

   This function deselects all objects in the current Blender scene and
   then iterates through all objects. If an object's name starts with the
   specified prefix, it selects that object and deletes it from the scene.
   This is useful for operations that require removing multiple objects
   with a common naming convention.

   :param name: The prefix of the object names to be removed.
   :type name: str


.. py:function:: deselect()

   Deselect all objects in the current Blender context.

   This function utilizes the Blender Python API to deselect all objects in
   the current scene. It is useful for clearing selections before
   performing other operations on objects.  Raises:     None


.. py:function:: make_active(name)

   Make an object active in the Blender scene.

   This function takes the name of an object and sets it as the active
   object in the current Blender scene. It first deselects all objects,
   then selects the specified object and makes it active, allowing for
   further operations to be performed on it.

   :param name: The name of the object to be made active.
   :type name: str


.. py:function:: active_name(name)

   Change the name of the active object in Blender.

   This function sets the name of the currently active object in the
   Blender context to the specified name. It directly modifies the `name`
   attribute of the active object, allowing users to rename objects
   programmatically.

   :param name: The new name to assign to the active object.
   :type name: str


.. py:function:: rename(name, name2)

   Rename an object and make it active.

   This function renames an object in the Blender context and sets it as
   the active object. It first calls the `make_active` function to ensure
   the object is active, then updates the name of the active object to the
   new name provided.

   :param name: The current name of the object to be renamed.
   :type name: str
   :param name2: The new name to assign to the active object.
   :type name2: str


.. py:function:: union(name)

   Perform a boolean union operation on objects.

   This function selects multiple objects that start with the given name,
   performs a boolean union operation on them using Blender's operators,
   and then renames the resulting object to the specified name. After the
   operation, it removes the original objects that were used in the union
   process.

   :param name: The base name of the objects to be unioned.
   :type name: str


.. py:function:: intersect(name)

   Perform an intersection operation on a curve object.

   This function selects multiple objects based on the provided name and
   then executes a boolean operation to create an intersection of the
   selected objects. The resulting intersection is then named accordingly.

   :param name: The name of the object(s) to be selected for the intersection.
   :type name: str


.. py:function:: difference(name, basename)

   Perform a boolean difference operation on objects.

   This function selects a series of objects specified by `name` and
   performs a boolean difference operation with the object specified by
   `basename`. After the operation, the resulting object is renamed to
   'booleandifference'. The original objects specified by `name` are
   deleted after the operation.

   :param name: The name of the series of objects to select for the operation.
   :type name: str
   :param basename: The name of the base object to perform the boolean difference with.
   :type basename: str


.. py:function:: duplicate(x=0.0, y=0.0)

   Duplicate an active object or move it based on the provided coordinates.

   This function duplicates the currently active object in Blender. If both
   x and y are set to their default values (0), the object is duplicated in
   place. If either x or y is non-zero, the object is duplicated and moved
   by the specified x and y offsets.

   :param x: The x-coordinate offset for the duplication.
             Defaults to 0.
   :type x: float
   :param y: The y-coordinate offset for the duplication.
             Defaults to 0.
   :type y: float


.. py:function:: mirror_x()

   Mirror the active object along the x-axis.

   This function utilizes Blender's operator to mirror the currently active
   object in the 3D view along the x-axis. It sets the orientation to
   global and applies the transformation based on the specified orientation
   matrix and constraint axis.


.. py:function:: mirror_y()

   Mirror the active object along the Y axis.

   This function uses Blender's operator to perform a mirror transformation
   on the currently active object in the scene. The mirroring is done with
   respect to the global coordinate system, specifically along the Y axis.
   This can be useful for creating symmetrical objects or for correcting
   the orientation of an object in a 3D environment.  Raises:     None


.. py:function:: move(x=0.0, y=0.0)

   Move the active object in the 3D space by applying a translation.

   This function translates the active object in Blender's 3D view by the
   specified x and y values. It uses Blender's built-in operations to
   perform the translation and then applies the transformation to the
   object's location.

   :param x: The distance to move the object along the x-axis. Defaults to 0.0.
   :type x: float
   :param y: The distance to move the object along the y-axis. Defaults to 0.0.
   :type y: float


.. py:function:: rotate(angle)

   Rotate the active object by a specified angle.

   This function modifies the rotation of the currently active object in
   the Blender context by setting its Z-axis rotation to the given angle.
   After updating the rotation, it applies the transformation to ensure
   that the changes are saved to the object's data.

   :param angle: The angle in radians to rotate the active object
                 around the Z-axis.
   :type angle: float


.. py:function:: remove_doubles()

   Remove duplicate vertices from the selected curve object.

   This function utilizes the Blender Python API to remove duplicate
   vertices from the currently selected curve object in the Blender
   environment. It is essential for cleaning up geometry and ensuring that
   the curve behaves as expected without unnecessary complexity.


.. py:function:: add_overcut(diametre, overcut=True)

   Add overcut to the active object.

   This function adds an overcut to the currently active object in the
   Blender context. If the `overcut` parameter is set to True, it performs
   a series of operations including creating a curve overcut with the
   specified diameter, deleting the original object, and renaming the new
   object to match the original. The function also ensures that any
   duplicate vertices are removed from the resulting object.

   :param diametre: The diameter to be used for the overcut.
   :type diametre: float
   :param overcut: A flag indicating whether to apply the overcut. Defaults to True.
   :type overcut: bool


.. py:function:: add_bound_rectangle(xmin, ymin, xmax, ymax, name='bounds_rectangle')

   Add a bounding rectangle to a curve.

   This function creates a rectangle defined by the minimum and maximum x
   and y coordinates provided as arguments. The rectangle is added to the
   scene at the center of the defined bounds. The resulting rectangle is
   named according to the 'name' parameter.

   :param xmin: The minimum x-coordinate of the rectangle.
   :type xmin: float
   :param ymin: The minimum y-coordinate of the rectangle.
   :type ymin: float
   :param xmax: The maximum x-coordinate of the rectangle.
   :type xmax: float
   :param ymax: The maximum y-coordinate of the rectangle.
   :type ymax: float
   :param name: The name of the resulting rectangle object. Defaults to
                'bounds_rectangle'.
   :type name: str


.. py:function:: add_rectangle(width, height, center_x=True, center_y=True)

   Add a rectangle to the scene.

   This function creates a rectangle in the 3D space using the specified
   width and height. The rectangle can be centered at the origin or offset
   based on the provided parameters. If `center_x` or `center_y` is set to
   True, the rectangle will be positioned at the center of the specified
   dimensions; otherwise, it will be positioned based on the offsets.

   :param width: The width of the rectangle.
   :type width: float
   :param height: The height of the rectangle.
   :type height: float
   :param center_x: If True, centers the rectangle along the x-axis. Defaults to True.
   :type center_x: bool?
   :param center_y: If True, centers the rectangle along the y-axis. Defaults to True.
   :type center_y: bool?


.. py:function:: active_to_coords()

   Convert the active object to a list of its vertex coordinates.

   This function duplicates the currently active object in the Blender
   context, converts it to a mesh, and extracts the X and Y coordinates of
   its vertices. After extracting the coordinates, it removes the temporary
   mesh object created during the process. The resulting list contains
   tuples of (x, y) coordinates for each vertex in the active object.

   :returns: A list of tuples, each containing the X and Y coordinates of the
             vertices from the active object.
   :rtype: list


.. py:function:: active_to_shapely_poly()

   Convert the active object to a Shapely polygon.

   This function retrieves the coordinates of the currently active object
   and converts them into a Shapely Polygon data structure. It is useful
   for geometric operations and spatial analysis using the Shapely library.

   :returns: A Shapely Polygon object created from the active object's coordinates.
   :rtype: Polygon


.. py:function:: make_visible(o)

.. py:function:: restore_visibility(o, storage)

.. py:function:: subdivide_short_lines(co)

   Subdivide all polylines to have at least three points.

   This function iterates through the splines of a curve, checks if they are not bezier
   and if they have less or equal to two points. If so, each spline is subdivided to get
   at least three points.

   :param co: A curve object to be analyzed and modified.
   :type co: Object


.. py:function:: subdivide_long_edges(ob, threshold)

   Subdivide edges of a mesh object that exceed a specified length.

   This function iteratively checks the edges of a given mesh object and
   subdivides those that are longer than a specified threshold. The process
   involves toggling the edit mode of the object, selecting the long edges,
   and applying a subdivision operation. The function continues to
   subdivide until no edges exceed the threshold.

   :param ob: The Blender object containing the mesh to be
              subdivided.
   :type ob: bpy.types.Object
   :param threshold: The length threshold above which edges will be
                     subdivided.
   :type threshold: float


.. py:function:: dilate_array(ar, cycles)

   Dilate a binary array using a specified number of cycles.

   This function performs a dilation operation on a 2D binary array. For
   each cycle, it updates the array by applying a logical OR operation
   between the current array and its neighboring elements. The dilation
   effect expands the boundaries of the foreground (True) pixels in the
   binary array.

   :param ar: A 2D binary array (numpy array) where
              dilation will be applied.
   :type ar: numpy.ndarray
   :param cycles: The number of dilation cycles to perform.
   :type cycles: int

   :returns:

             The function modifies the input array in place and does not
                 return a value.
   :rtype: None


.. py:function:: rotate_point_by_point(originp, p, ang)

