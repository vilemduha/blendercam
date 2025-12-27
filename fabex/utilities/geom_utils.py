"""Fabex 'geom_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

from math import pi

from shapely.geometry import Polygon

import bpy
from mathutils import Euler, Vector


def circle(r, np):
    """Generate a circle defined by a given radius and number of points.

    This function creates a polygon representing a circle by generating a
    list of points based on the specified radius and the number of points
    (np). It uses vector rotation to calculate the coordinates of each point
    around the circle. The resulting points are then used to create a
    polygon object.

    Args:
        r (float): The radius of the circle.
        np (int): The number of points to generate around the circle.

    Returns:
        Polygon: A polygon object representing the circle.
    """

    c = []
    v = Vector((r, 0, 0))
    e = Euler((0, 0, 2.0 * pi / np))
    for a in range(0, np):
        c.append((v.x, v.y))
        v.rotate(e)

    p = Polygon(c)
    return p


def helix(r, np, zstart, pend, rev):
    """Generate a helix of points in 3D space.

    This function calculates a series of points that form a helix based on
    the specified parameters. It starts from a given radius and
    z-coordinate, and generates points by rotating around the z-axis while
    moving linearly along the z-axis. The number of points generated is
    determined by the number of turns (revolutions) and the number of points
    per revolution.

    Args:
        r (float): The radius of the helix.
        np (int): The number of points per revolution.
        zstart (float): The starting z-coordinate for the helix.
        pend (tuple): A tuple containing the x, y, and z coordinates of the endpoint.
        rev (int): The number of revolutions to complete.

    Returns:
        list: A list of tuples representing the coordinates of the points in the
            helix.
    """

    c = []
    v = Vector((r, 0, zstart))
    e = Euler((0, 0, 2.0 * pi / np))
    zstep = (zstart - pend[2]) / (np * rev)
    for a in range(0, int(np * rev)):
        c.append((v.x + pend[0], v.y + pend[1], zstart - (a * zstep)))
        v.rotate(e)
    c.append((v.x + pend[0], v.y + pend[1], pend[2]))

    return c


def get_container():
    """Get or create a container object for CAM objects.

    This function checks if a container object named 'CAM_OBJECTS' exists in
    the current Blender scene. If it does not exist, the function creates a
    new empty object of type 'PLAIN_AXES', names it 'CAM_OBJECTS', and sets
    its location to the origin (0, 0, 0). The newly created container is
    also hidden. If the container already exists, it simply retrieves and
    returns that object.

    Returns:
        bpy.types.Object: The container object for CAM objects, either newly created or
            existing.
    """

    s = bpy.context.scene
    if s.objects.get("CAM_OBJECTS") is None:
        bpy.ops.object.empty_add(type="PLAIN_AXES", align="WORLD")
        container = bpy.context.active_object
        container.name = "CAM_OBJECTS"
        container.location = [0, 0, 0]
        container.hide = True
    else:
        container = s.objects["CAM_OBJECTS"]

    return container


# tools for voroni graphs all copied from the delaunayVoronoi addon:
class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def triangle(i, T, A):
    s = f"{A * 8 / (pi**2)} * ("
    for n in range(i):
        if n % 2 != 0:
            e = (n - 1) / 2
            a = round(((-1) ** e) / (n**2), 8)
            b = round(n * pi / (T / 2), 8)
            if n > 1:
                s += "+"
            s += f"{a} * sin({b} * t)"
    s += ")"
    return s


def s_sine(A, T, dc_offset=0, phase_shift=0):
    args = [dc_offset, phase_shift, A, T]
    for arg in args:
        arg = round(arg, 6)

    return f"{dc_offset} + {A} * sin((2 * pi / {T}) * (t + {phase_shift}))"


def get_circle(r, z):
    """Generate a 2D array representing a circle.

    This function creates a 2D NumPy array filled with a specified value for
    points that fall within a circle of a given radius. The circle is
    centered in the array, and the function uses the Euclidean distance to
    determine which points are inside the circle. The resulting array has
    dimensions that are twice the radius, ensuring that the entire circle
    fits within the array.

    Args:
        r (int): The radius of the circle.
        z (float): The value to fill the points inside the circle.

    Returns:
        numpy.ndarray: A 2D array where points inside the circle are filled
        with the value `z`, and points outside are filled with -10.
    """

    car = numpy.full(shape=(r * 2, r * 2), fill_value=-10, dtype=numpy.double)
    res = 2 * r
    m = r
    v = Vector((0, 0, 0))
    for a in range(0, res):
        v.x = a + 0.5 - m
        for b in range(0, res):
            v.y = b + 0.5 - m
            if v.length <= r:
                car[a, b] = z
    return car


def get_circle_binary(r):
    """Generate a binary representation of a circle in a 2D grid.

    This function creates a 2D boolean array where the elements inside a
    circle of radius `r` are set to `True`, and the elements outside the
    circle are set to `False`. The circle is centered in the middle of the
    array, which has dimensions of (2*r, 2*r). The function iterates over
    each point in the grid and checks if it lies within the specified
    radius.

    Args:
        r (int): The radius of the circle.

    Returns:
        numpy.ndarray: A 2D boolean array representing the circle.
    """

    car = numpy.full(shape=(r * 2, r * 2), fill_value=False, dtype=bool)
    res = 2 * r
    m = r
    v = Vector((0, 0, 0))
    for a in range(0, res):
        v.x = a + 0.5 - m
        for b in range(0, res):
            v.y = b + 0.5 - m
            if v.length <= r:
                car.itemset((a, b), True)
    return car
