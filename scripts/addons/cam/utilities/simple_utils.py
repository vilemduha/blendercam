"""Fabex 'simple_utils.py' © 2012 Vilem Novak

Various helper functions, less complex than those found in the 'utils' files.
"""

from math import (
    hypot,
    pi,
)
import os
import string
import sys
import time

from shapely.geometry import Polygon

import bpy
from mathutils import Vector

from ..constants import BULLET_SCALE


def tuple_add(t, t1):  # add two tuples as Vectors
    """Add two tuples as vectors.

    This function takes two tuples, each representing a vector in three-
    dimensional space, and returns a new tuple that is the element-wise sum
    of the two input tuples. It assumes that both tuples contain exactly
    three numeric elements.

    Args:
        t (tuple): A tuple containing three numeric values representing the first vector.
        t1 (tuple): A tuple containing three numeric values representing the second vector.

    Returns:
        tuple: A tuple containing three numeric values that represent the sum of the
            input vectors.
    """
    return t[0] + t1[0], t[1] + t1[1], t[2] + t1[2]


def tuple_subtract(t, t1):  # sub two tuples as Vectors
    """Subtract two tuples element-wise.

    This function takes two tuples of three elements each and performs an
    element-wise subtraction, treating the tuples as vectors. The result is
    a new tuple containing the differences of the corresponding elements
    from the input tuples.

    Args:
        t (tuple): A tuple containing three numeric values.
        t1 (tuple): A tuple containing three numeric values.

    Returns:
        tuple: A tuple containing the results of the element-wise subtraction.
    """
    return t[0] - t1[0], t[1] - t1[1], t[2] - t1[2]


def tuple_multiply(t, c):  # multiply two tuples with a number
    """Multiply each element of a tuple by a given number.

    This function takes a tuple containing three elements and a numeric
    value, then multiplies each element of the tuple by the provided number.
    The result is returned as a new tuple containing the multiplied values.

    Args:
        t (tuple): A tuple containing three numeric values.
        c (numeric): A number by which to multiply each element of the tuple.

    Returns:
        tuple: A new tuple containing the results of the multiplication.
    """
    return t[0] * c, t[1] * c, t[2] * c


def tuple_length(t):  # get length of vector, but passed in as tuple.
    """Get the length of a vector represented as a tuple.

    This function takes a tuple as input, which represents the coordinates
    of a vector, and returns its length by creating a Vector object from the
    tuple. The length is calculated using the appropriate mathematical
    formula for vector length.

    Args:
        t (tuple): A tuple representing the coordinates of the vector.

    Returns:
        float: The length of the vector.
    """
    return Vector(t).length


# timing functions for optimisation purposes...
def timing_init():
    """Initialize timing metrics.

    This function sets up the initial state for timing functions by
    returning a list containing two zero values. These values can be used to
    track elapsed time or other timing-related metrics in subsequent
    operations.

    Returns:
        list: A list containing two zero values, representing the
        initial timing metrics.
    """
    return [0, 0]


def timing_start(tinf):
    """Start timing by recording the current time.

    This function updates the second element of the provided list with the
    current time in seconds since the epoch. It is useful for tracking the
    start time of an operation or process.

    Args:
        tinf (list): A list where the second element will be updated
            with the current time.
    """
    t = time.time()
    tinf[1] = t


def timing_add(tinf):
    """Update the timing information.

    This function updates the first element of the `tinf` list by adding the
    difference between the current time and the second element of the list.
    It is typically used to track elapsed time in a timing context.

    Args:
        tinf (list): A list where the first element is updated with the
    """
    t = time.time()
    tinf[0] += t - tinf[1]


def timing_print(tinf):
    """Print the timing information.

    This function takes a tuple containing timing information and prints it
    in a formatted string. It specifically extracts the first element of the
    tuple, which is expected to represent time, and appends the string
    'seconds' to it before printing.

    Args:
        tinf (tuple): A tuple where the first element is expected to be a numeric value
            representing time.

    Returns:
        None: This function does not return any value; it only prints output to the
            console.
    """
    print("time " + str(tinf[0]) + "seconds")


def progress(text, n=None):
    """Report progress during script execution.

    This function outputs a progress message to the standard output. It is
    designed to work for background operations and provides a formatted
    string that includes the specified text and an optional numeric progress
    value. If the numeric value is provided, it is formatted as a
    percentage.

    Args:
        text (str): The message to display as progress.
        n (float?): A float representing the progress as a
            fraction (0.0 to 1.0). If not provided, no percentage will
            be displayed.

    Returns:
        None: This function does not return a value; it only prints
            to the standard output.
    """
    text = str(text)
    if n is None:
        n = ""
    else:
        n = str(int(n * 1000) / 1000) + "%"
    sys.stdout.write(f"Progress: {text}{n}\n")
    sys.stdout.flush()


def activate(o):
    """Makes an object active in Blender.

    This function sets the specified object as the active object in the
    current Blender scene. It first deselects all objects, then selects the
    given object and makes it the active object in the view layer. This is
    useful for operations that require a specific object to be active, such
    as transformations or modifications.

    Args:
        o (bpy.types.Object): The Blender object to be activated.
    """
    s = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(state=True)
    s.objects[o.name].select_set(state=True)
    bpy.context.view_layer.objects.active = o


def distance_2d(v1, v2):
    """Calculate the distance between two points in 2D space.

    This function computes the Euclidean distance between two points
    represented by their coordinates in a 2D plane. It uses the Pythagorean
    theorem to calculate the distance based on the differences in the x and
    y coordinates of the points.

    Args:
        v1 (tuple): A tuple representing the coordinates of the first point (x1, y1).
        v2 (tuple): A tuple representing the coordinates of the second point (x2, y2).

    Returns:
        float: The Euclidean distance between the two points.
    """
    return hypot((v1[0] - v2[0]), (v1[1] - v2[1]))


def delete_object(ob):
    """Delete an object in Blender for multiple uses.

    This function activates the specified object and then deletes it using
    Blender's built-in operations. It is designed to facilitate the deletion
    of objects within the Blender environment, ensuring that the object is
    active before performing the deletion operation.

    Args:
        ob (Object): The Blender object to be deleted.
    """
    activate(ob)
    bpy.ops.object.delete(use_global=False)


def duplicate_object(o, pos):
    """Helper function for visualizing cutter positions in bullet simulation.

    This function duplicates the specified object and resizes it according
    to a predefined scale factor. It also removes any existing rigidbody
    properties from the duplicated object and sets its location to the
    specified position. This is useful for managing multiple cutter
    positions in a bullet simulation environment.

    Args:
        o (Object): The object to be duplicated.
        pos (Vector): The new position to place the duplicated object.
    """
    activate(o)
    bpy.ops.object.duplicate()
    s = 1.0 / BULLET_SCALE
    bpy.ops.transform.resize(
        value=(s, s, s),
        constraint_axis=(False, False, False),
        orient_type="GLOBAL",
        mirror=False,
        use_proportional_edit=False,
        proportional_edit_falloff="SMOOTH",
        proportional_size=1,
    )
    o = bpy.context.active_object
    bpy.ops.rigidbody.object_remove()
    o.location = pos


def add_to_group(ob, groupname):
    """Add an object to a specified group in Blender.

    This function activates the given object and checks if the specified
    group exists in Blender's data. If the group does not exist, it creates
    a new group with the provided name. If the group already exists, it
    links the object to that group.

    Args:
        ob (Object): The object to be added to the group.
        groupname (str): The name of the group to which the object will be added.
    """
    activate(ob)
    if bpy.data.groups.get(groupname) is None:
        bpy.ops.group.create(name=groupname)
    else:
        bpy.ops.object.group_link(group=groupname)


def compare(v1, v2, vmiddle, e):
    """Comparison for optimization of paths.

    This function compares two vectors and checks if the distance between a
    calculated vector and a reference vector is less than a specified
    threshold. It normalizes the vector difference and scales it by the
    length of another vector to determine if the resulting vector is within
    the specified epsilon value.

    Args:
        v1 (Vector): The first vector for comparison.
        v2 (Vector): The second vector for comparison.
        vmiddle (Vector): The middle vector used for calculating the
            reference vector.
        e (float): The threshold value for comparison.

    Returns:
        bool: True if the distance is less than the threshold,
            otherwise False.
    """
    # e=0.0001
    v1 = Vector(v1)
    v2 = Vector(v2)
    vmiddle = Vector(vmiddle)
    vect1 = v2 - v1
    vect2 = vmiddle - v1
    vect1.normalize()
    vect1 *= vect2.length
    v = vect2 - vect1
    if v.length < e:
        return True
    return False


def is_vertical_limit(v1, v2, limit):
    """Test Path Segment on Verticality Threshold for protect_vertical option.

    This function evaluates the verticality of a path segment defined by two
    points, v1 and v2, based on a specified limit. It calculates the angle
    between the vertical vector and the vector formed by the two points. If
    the angle is within the defined limit, it adjusts the vertical position
    of either v1 or v2 to ensure that the segment adheres to the verticality
    threshold.

    Args:
        v1 (tuple): A 3D point represented as a tuple (x, y, z).
        v2 (tuple): A 3D point represented as a tuple (x, y, z).
        limit (float): The angle threshold for determining verticality.

    Returns:
        tuple: The adjusted 3D points v1 and v2 after evaluating the verticality.
    """
    z = abs(v1[2] - v2[2])
    # verticality=0.05
    # this will be better.
    #
    # print(a)
    if z > 0:
        v2d = Vector((0, 0, -1))
        v3d = Vector((v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]))
        a = v3d.angle(v2d)
        if a > pi / 2:
            a = abs(a - pi)
        # print(a)
        if a < limit:
            # print(abs(v1[0]-v2[0])/z)
            # print(abs(v1[1]-v2[1])/z)
            if v1[2] > v2[2]:
                v1 = (v2[0], v2[1], v1[2])
                return v1, v2
            else:
                v2 = (v1[0], v1[1], v2[2])
                return v1, v2
    return v1, v2


def get_cache_path(o):
    """Get the cache path for a given object.

    This function constructs a cache path based on the current Blender
    file's filepath and the name of the provided object. It retrieves the
    base name of the file, removes the last six characters, and appends a
    specified directory and the object's name to create a complete cache
    path.

    Args:
        o (Object): The Blender object for which the cache path is being generated.

    Returns:
        str: The constructed cache path as a string.
    """
    fn = bpy.data.filepath
    l = len(bpy.path.basename(fn))
    bn = bpy.path.basename(fn)[:-6]
    print("Folder:", fn[:-l])
    print("File:", bn)

    iname = fn[:-l] + "temp_cam" + os.sep + bn + "_" + o.name
    return iname


def get_simulation_path():
    """Get the simulation path for temporary CAM files.

    This function retrieves the file path of the current Blender project and
    constructs a new path for temporary CAM files by appending 'temp_cam'
    to the directory of the current file. The constructed path is returned
    as a string.

    Returns:
        str: The path to the temporary CAM directory.
    """
    fn = bpy.data.filepath
    l = len(bpy.path.basename(fn))
    iname = fn[:-l] + "temp_cam" + os.sep
    return iname


def safe_filename(name):  # for export gcode
    """Generate a safe file name from the given string.

    This function takes a string input and removes any characters that are
    not considered valid for file names. The valid characters include
    letters, digits, and a few special characters. The resulting string can
    be used safely as a file name for exporting purposes.

    Args:
        name (str): The input string to be sanitized into a safe file name.

    Returns:
        str: A sanitized version of the input string that contains only valid
        characters for a file name.
    """
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    filename = "".join(c for c in name if c in valid_chars)
    return filename


def unit_value_to_string(x, precision=5):
    """Convert a value to a string representation in the current unit system.

    This function takes a numeric value and converts it to a string
    formatted according to the unit system set in the Blender context. If
    the unit system is metric, the value is converted to millimeters. If the
    unit system is imperial, the value is converted to inches. The precision
    of the output can be specified.

    Args:
        x (float): The numeric value to be converted.
        precision (int?): The number of decimal places to round to.
            Defaults to 5.

    Returns:
        str: The string representation of the value in the appropriate units.
    """
    if bpy.context.scene.unit_settings.system == "METRIC":
        return str(round(x * 1000, precision)) + " mm "
    elif bpy.context.scene.unit_settings.system == "IMPERIAL":
        return str(round(x * 1000 / 25.4, precision)) + "'' "
    else:
        return str(x)


# select multiple object starting with name
def select_multiple(name):
    """Select multiple objects in the scene based on their names.

    This function deselects all objects in the current Blender scene and
    then selects all objects whose names start with the specified prefix. It
    iterates through all objects in the scene and checks if their names
    begin with the given string. If they do, those objects are selected;
    otherwise, they are deselected.

    Args:
        name (str): The prefix used to select objects in the scene.
    """
    scene = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    for ob in scene.objects:  # join pocket curve calculations
        if ob.name.startswith(name):
            ob.select_set(True)
        else:
            ob.select_set(False)


# join multiple objects starting with 'name' renaming final object as 'name'
def join_multiple(name):
    """Join multiple objects and rename the final object.

    This function selects multiple objects in the Blender context, joins
    them into a single object, and renames the resulting object to the
    specified name. It is assumed that the objects to be joined are already
    selected in the Blender interface.

    Args:
        name (str): The new name for the joined object.
    """
    select_multiple(name)
    bpy.ops.object.join()
    bpy.context.active_object.name = name  # rename object


# remove multiple objects starting with 'name'.... useful for fixed name operation
def remove_multiple(name):
    """Remove multiple objects from the scene based on their name prefix.

    This function deselects all objects in the current Blender scene and
    then iterates through all objects. If an object's name starts with the
    specified prefix, it selects that object and deletes it from the scene.
    This is useful for operations that require removing multiple objects
    with a common naming convention.

    Args:
        name (str): The prefix of the object names to be removed.
    """
    scene = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    for ob in scene.objects:
        if ob.name.startswith(name):
            ob.select_set(True)
            bpy.ops.object.delete()


def deselect():
    """Deselect all objects in the current Blender context.

    This function utilizes the Blender Python API to deselect all objects in
    the current scene. It is useful for clearing selections before
    performing other operations on objects.  Raises:     None
    """
    bpy.ops.object.select_all(action="DESELECT")


# makes the object with the name active
def make_active(name):
    """Make an object active in the Blender scene.

    This function takes the name of an object and sets it as the active
    object in the current Blender scene. It first deselects all objects,
    then selects the specified object and makes it active, allowing for
    further operations to be performed on it.

    Args:
        name (str): The name of the object to be made active.
    """
    ob = bpy.context.scene.objects[name]
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


# change the name of the active object
def active_name(name):
    """Change the name of the active object in Blender.

    This function sets the name of the currently active object in the
    Blender context to the specified name. It directly modifies the `name`
    attribute of the active object, allowing users to rename objects
    programmatically.

    Args:
        name (str): The new name to assign to the active object.
    """
    bpy.context.active_object.name = name


# renames and makes active name and makes it active
def rename(name, name2):
    """Rename an object and make it active.

    This function renames an object in the Blender context and sets it as
    the active object. It first calls the `make_active` function to ensure
    the object is active, then updates the name of the active object to the
    new name provided.

    Args:
        name (str): The current name of the object to be renamed.
        name2 (str): The new name to assign to the active object.
    """
    make_active(name)
    bpy.context.active_object.name = name2


# boolean union of objects starting with name result is object name.
# all objects starting with name will be deleted and the result will be name
def union(name):
    """Perform a boolean union operation on objects.

    This function selects multiple objects that start with the given name,
    performs a boolean union operation on them using Blender's operators,
    and then renames the resulting object to the specified name. After the
    operation, it removes the original objects that were used in the union
    process.

    Args:
        name (str): The base name of the objects to be unioned.
    """
    select_multiple(name)
    bpy.ops.object.curve_boolean(boolean_type="UNION")
    active_name("unionboolean")
    remove_multiple(name)
    rename("unionboolean", name)


def intersect(name):
    """Perform an intersection operation on a curve object.

    This function selects multiple objects based on the provided name and
    then executes a boolean operation to create an intersection of the
    selected objects. The resulting intersection is then named accordingly.

    Args:
        name (str): The name of the object(s) to be selected for the intersection.
    """
    select_multiple(name)
    bpy.ops.object.curve_boolean(boolean_type="INTERSECT")
    active_name("intersection")


# boolean difference of objects starting with name result is object from basename.
# all objects starting with name will be deleted and the result will be basename


def difference(name, basename):
    """Perform a boolean difference operation on objects.

    This function selects a series of objects specified by `name` and
    performs a boolean difference operation with the object specified by
    `basename`. After the operation, the resulting object is renamed to
    'booleandifference'. The original objects specified by `name` are
    deleted after the operation.

    Args:
        name (str): The name of the series of objects to select for the operation.
        basename (str): The name of the base object to perform the boolean difference with.
    """
    #   name is the series to select
    #   basename is what the base you want to cut including name
    select_multiple(name)
    bpy.context.view_layer.objects.active = bpy.data.objects[basename]
    bpy.ops.object.curve_boolean(boolean_type="DIFFERENCE")
    active_name("booleandifference")
    remove_multiple(name)
    rename("booleandifference", basename)


# duplicate active object or duplicate move
# if x or y not the default, duplicate move will be executed
def duplicate(x=0.0, y=0.0):
    """Duplicate an active object or move it based on the provided coordinates.

    This function duplicates the currently active object in Blender. If both
    x and y are set to their default values (0), the object is duplicated in
    place. If either x or y is non-zero, the object is duplicated and moved
    by the specified x and y offsets.

    Args:
        x (float): The x-coordinate offset for the duplication.
            Defaults to 0.
        y (float): The y-coordinate offset for the duplication.
            Defaults to 0.
    """
    if x == 0.0 and y == 0.0:
        bpy.ops.object.duplicate()
    else:
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
            TRANSFORM_OT_translate={"value": (x, y, 0.0)},
        )


# Mirror active object along the x axis
def mirror_x():
    """Mirror the active object along the x-axis.

    This function utilizes Blender's operator to mirror the currently active
    object in the 3D view along the x-axis. It sets the orientation to
    global and applies the transformation based on the specified orientation
    matrix and constraint axis.
    """
    bpy.ops.transform.mirror(
        orient_type="GLOBAL",
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        orient_matrix_type="GLOBAL",
        constraint_axis=(True, False, False),
    )


# mirror active object along y axis
def mirror_y():
    """Mirror the active object along the Y axis.

    This function uses Blender's operator to perform a mirror transformation
    on the currently active object in the scene. The mirroring is done with
    respect to the global coordinate system, specifically along the Y axis.
    This can be useful for creating symmetrical objects or for correcting
    the orientation of an object in a 3D environment.  Raises:     None
    """
    bpy.ops.transform.mirror(
        orient_type="GLOBAL",
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        orient_matrix_type="GLOBAL",
        constraint_axis=(False, True, False),
    )


# move active object and apply translation
def move(x=0.0, y=0.0):
    """Move the active object in the 3D space by applying a translation.

    This function translates the active object in Blender's 3D view by the
    specified x and y values. It uses Blender's built-in operations to
    perform the translation and then applies the transformation to the
    object's location.

    Args:
        x (float): The distance to move the object along the x-axis. Defaults to 0.0.
        y (float): The distance to move the object along the y-axis. Defaults to 0.0.
    """
    bpy.ops.transform.translate(value=(x, y, 0.0))
    bpy.ops.object.transform_apply(location=True)


# Rotate active object and apply rotation
def rotate(angle):
    """Rotate the active object by a specified angle.

    This function modifies the rotation of the currently active object in
    the Blender context by setting its Z-axis rotation to the given angle.
    After updating the rotation, it applies the transformation to ensure
    that the changes are saved to the object's data.

    Args:
        angle (float): The angle in radians to rotate the active object
            around the Z-axis.
    """
    bpy.context.object.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(rotation=True)


# remove doubles
def remove_doubles():
    """Remove duplicate vertices from the selected curve object.

    This function utilizes the Blender Python API to remove duplicate
    vertices from the currently selected curve object in the Blender
    environment. It is essential for cleaning up geometry and ensuring that
    the curve behaves as expected without unnecessary complexity.
    """
    bpy.ops.object.curve_remove_doubles()


# Add overcut to active object
def add_overcut(diametre, overcut=True):
    """Add overcut to the active object.

    This function adds an overcut to the currently active object in the
    Blender context. If the `overcut` parameter is set to True, it performs
    a series of operations including creating a curve overcut with the
    specified diameter, deleting the original object, and renaming the new
    object to match the original. The function also ensures that any
    duplicate vertices are removed from the resulting object.

    Args:
        diametre (float): The diameter to be used for the overcut.
        overcut (bool): A flag indicating whether to apply the overcut. Defaults to True.
    """
    if overcut:
        name = bpy.context.active_object.name
        bpy.ops.object.curve_overcuts(diameter=diametre, threshold=pi / 2.05)
        overcut_name = bpy.context.active_object.name
        make_active(name)
        bpy.ops.object.delete()
        rename(overcut_name, name)
        remove_doubles()


# add bounding rectangtle to curve
def add_bound_rectangle(xmin, ymin, xmax, ymax, name="bounds_rectangle"):
    """Add a bounding rectangle to a curve.

    This function creates a rectangle defined by the minimum and maximum x
    and y coordinates provided as arguments. The rectangle is added to the
    scene at the center of the defined bounds. The resulting rectangle is
    named according to the 'name' parameter.

    Args:
        xmin (float): The minimum x-coordinate of the rectangle.
        ymin (float): The minimum y-coordinate of the rectangle.
        xmax (float): The maximum x-coordinate of the rectangle.
        ymax (float): The maximum y-coordinate of the rectangle.
        name (str): The name of the resulting rectangle object. Defaults to
            'bounds_rectangle'.
    """

    xsize = xmax - xmin
    ysize = ymax - ymin

    bpy.ops.curve.simple(
        align="WORLD",
        location=(xmin + xsize / 2, ymin + ysize / 2, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=xsize,
        Simple_length=ysize,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    bpy.ops.object.transform_apply(location=True)
    active_name(name)


def add_rectangle(width, height, center_x=True, center_y=True):
    """Add a rectangle to the scene.

    This function creates a rectangle in the 3D space using the specified
    width and height. The rectangle can be centered at the origin or offset
    based on the provided parameters. If `center_x` or `center_y` is set to
    True, the rectangle will be positioned at the center of the specified
    dimensions; otherwise, it will be positioned based on the offsets.

    Args:
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.
        center_x (bool?): If True, centers the rectangle along the x-axis. Defaults to True.
        center_y (bool?): If True, centers the rectangle along the y-axis. Defaults to True.
    """
    x_offset = width / 2
    y_offset = height / 2

    if center_x:
        x_offset = 0
    if center_y:
        y_offset = 0

    bpy.ops.curve.simple(
        align="WORLD",
        location=(x_offset, y_offset, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=width,
        Simple_length=height,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    bpy.ops.object.transform_apply(location=True)
    active_name("simple_rectangle")


#  Returns coords from active object
def active_to_coords():
    """Convert the active object to a list of its vertex coordinates.

    This function duplicates the currently active object in the Blender
    context, converts it to a mesh, and extracts the X and Y coordinates of
    its vertices. After extracting the coordinates, it removes the temporary
    mesh object created during the process. The resulting list contains
    tuples of (x, y) coordinates for each vertex in the active object.

    Returns:
        list: A list of tuples, each containing the X and Y coordinates of the
        vertices from the active object.
    """
    bpy.ops.object.duplicate()
    obj = bpy.context.active_object
    bpy.ops.object.convert(target="MESH")
    active_name("_tmp_mesh")

    coords = []
    for v in obj.data.vertices:  # extract X,Y coordinates from the vertices data
        coords.append((v.co.x, v.co.y))
    remove_multiple("_tmp_mesh")
    return coords


# returns shapely polygon from active object
def active_to_shapely_poly():
    """Convert the active object to a Shapely polygon.

    This function retrieves the coordinates of the currently active object
    and converts them into a Shapely Polygon data structure. It is useful
    for geometric operations and spatial analysis using the Shapely library.

    Returns:
        Polygon: A Shapely Polygon object created from the active object's coordinates.
    """
    # convert coordinates to shapely Polygon datastructure
    return Polygon(active_to_coords())


# checks for curve splines shorter than three points and subdivides if necessary
def subdivide_short_lines(co):
    """Subdivide all polylines to have at least three points.

    This function iterates through the splines of a curve, checks if they are not bezier
    and if they have less or equal to two points. If so, each spline is subdivided to get
    at least three points.

    Args:
        co (Object): A curve object to be analyzed and modified.
    """

    bpy.ops.object.mode_set(mode="EDIT")
    for sp in co.data.splines:
        if len(sp.points) == 2 and sp.type != "BEZIER":
            bpy.ops.curve.select_all(action="DESELECT")
            for pt in sp.points:
                pt.select = True
            bpy.ops.curve.subdivide()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action="SELECT")
