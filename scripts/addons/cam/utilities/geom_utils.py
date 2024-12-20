"""Fabex 'geom_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

from math import pi

from shapely import affinity
from shapely.geometry import (
    polygon as spolygon,
    MultiLineString,
    box,
)

import bpy
from mathutils import Euler, Vector

from .shapely_utils import curve_to_shapely


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
        spolygon.Polygon: A polygon object representing the circle.
    """

    c = []
    v = Vector((r, 0, 0))
    e = Euler((0, 0, 2.0 * pi / np))
    for a in range(0, np):
        c.append((v.x, v.y))
        v.rotate(e)

    p = spolygon.Polygon(c)
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
    """Get or create a container object for camera objects.

    This function checks if a container object named 'CAM_OBJECTS' exists in
    the current Blender scene. If it does not exist, the function creates a
    new empty object of type 'PLAIN_AXES', names it 'CAM_OBJECTS', and sets
    its location to the origin (0, 0, 0). The newly created container is
    also hidden. If the container already exists, it simply retrieves and
    returns that object.

    Returns:
        bpy.types.Object: The container object for camera objects, either newly created or
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


def generate_crosshatch(context, angle, distance, offset, pocket_shape, join, ob=None):
    """Execute the crosshatch generation process based on the provided context.

    Args:
        context (bpy.context): The Blender context containing the active object.
        angle (float): The angle for rotating the crosshatch pattern.
        distance (float): The distance between crosshatch lines.
        offset (float): The offset for the bounds or hull.
        pocket_shape (str): Determines whether to use bounds, hull, or pocket.

    Returns:
        shapely.geometry.MultiLineString: The resulting intersection geometry of the crosshatch.
    """
    if ob is None:
        ob = context.active_object
    else:
        bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    if ob.data.splines and ob.data.splines[0].type == "BEZIER":
        bpy.ops.object.curve_remove_doubles(merge_distance=0.0001, keep_bezier=True)
    else:
        bpy.ops.object.curve_remove_doubles()

    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
    depth = ob.location[2]

    shapes = curve_to_shapely(ob)

    if pocket_shape == "HULL":
        shapes = shapes.convex_hull

    coords = []
    minx, miny, maxx, maxy = shapes.bounds
    minx -= offset
    miny -= offset
    maxx += offset
    maxy += offset
    centery = (miny + maxy) / 2
    length = maxy - miny
    width = maxx - minx
    centerx = (minx + maxx) / 2
    diagonal = hypot(width, length)

    bound_rectangle = box(minx, miny, maxx, maxy)
    amount = int(2 * diagonal / distance) + 1

    for x in range(amount):
        distance_val = x * distance - diagonal
        coords.append(((distance_val, diagonal + 0.5), (distance_val, -diagonal - 0.5)))

    # Create a multilinestring shapely object
    lines = MultiLineString(coords)
    rotated = affinity.rotate(lines, angle, use_radians=True)  # Rotate using shapely
    rotated_minx, rotated_miny, rotated_maxx, rotated_maxy = rotated.bounds
    rotated_centerx = (rotated_minx + rotated_maxx) / 2
    rotated_centery = (rotated_miny + rotated_maxy) / 2
    x_offset = centerx - rotated_centerx
    y_offset = centery - rotated_centery
    translated = affinity.translate(
        rotated, xoff=x_offset, yoff=y_offset, zoff=depth
    )  # Move using shapely

    bounds = bound_rectangle

    if pocket_shape == "BOUNDS":
        xing = translated.intersection(bounds)  # Intersection with bounding box
    else:
        xing = translated.intersection(
            shapes.buffer(offset, join_style=join)
        )  # Intersection with shapes or hull

    # Return the intersection result
    return xing


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
