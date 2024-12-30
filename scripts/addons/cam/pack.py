"""Fabex 'pack.py' © 2012 Vilem Novak

Takes all selected curves, converts them to polygons, offsets them by the pre-set margin
then chooses a starting location possibly inside the already occupied area and moves and rotates the
polygon out of the occupied area if one or more positions are found where the poly doesn't overlap,
it is placed and added to the occupied area - allpoly
Very slow and STUPID, a collision algorithm would be much much faster...
"""

from math import pi
import random
import time

import shapely
from shapely import geometry as sgeometry
from shapely import affinity, prepared, speedups

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from mathutils import Euler, Vector

from . import constants
from .cam_chunk import curve_to_chunks

from .utilities.chunk_utils import chunks_to_shapely
from .utilities.shapely_utils import shapely_to_curve
from .utilities.simple_utils import activate


def s_rotate(s, r, x, y):
    """Rotate a polygon's coordinates around a specified point.

    This function takes a polygon and rotates its exterior coordinates
    around a given point (x, y) by a specified angle (r) in radians. It uses
    the Euler rotation to compute the new coordinates for each point in the
    polygon's exterior. The resulting coordinates are then used to create a
    new polygon.

    Args:
        s (shapely.geometry.Polygon): The polygon to be rotated.
        r (float): The angle of rotation in radians.
        x (float): The x-coordinate of the point around which to rotate.
        y (float): The y-coordinate of the point around which to rotate.

    Returns:
        shapely.geometry.Polygon: A new polygon with the rotated coordinates.
    """

    ncoords = []
    e = Euler((0, 0, r))
    for p in s.exterior.coords:
        v1 = Vector((p[0], p[1], 0))
        v2 = Vector((x, y, 0))
        v = v1 - v2
        v.rotate(e)
        ncoords.append((v[0], v[1]))

    return sgeometry.Polygon(ncoords)


def pack_curves():
    """Pack selected curves into a defined area based on specified settings.

    This function organizes selected curve objects in Blender by packing
    them into a specified area defined by the camera pack settings. It
    calculates the optimal positions for each curve while considering
    parameters such as sheet size, fill direction, distance, tolerance, and
    rotation. The function utilizes geometric operations to ensure that the
    curves do not overlap and fit within the defined boundaries. The packed
    curves are then transformed and their properties are updated
    accordingly.  The function performs the following steps: 1. Activates
    speedup features if available. 2. Retrieves packing settings from the
    current scene. 3. Processes each selected object to create polygons from
    curves. 4. Attempts to place each polygon within the defined area while
    avoiding    overlaps and respecting the specified fill direction. 5.
    Outputs the final arrangement of polygons.
    """

    if speedups.available:
        speedups.enable()
    t = time.time()
    packsettings = bpy.context.scene.cam_pack

    sheetsizex = packsettings.sheet_x
    sheetsizey = packsettings.sheet_y
    direction = packsettings.sheet_fill_direction
    distance = packsettings.distance
    tolerance = packsettings.tolerance
    rotate = packsettings.rotate
    rotate_angle = packsettings.rotate_angle

    # in this, position, rotation, and actual poly will be stored.
    polyfield = []
    for ob in bpy.context.selected_objects:
        activate(ob)
        bpy.ops.object.make_single_user(type="SELECTED_OBJECTS")
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
        z = ob.location.z
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()

        chunks = curve_to_chunks(ob)
        npolys = chunks_to_shapely(chunks)
        # add all polys in silh to one poly
        poly = shapely.ops.unary_union(npolys)

        poly = poly.buffer(distance / 1.5, 8)
        poly = poly.simplify(0.0003)
        polyfield.append([[0, 0], 0.0, poly, ob, z])
    random.shuffle(polyfield)
    # primitive layout here:
    allpoly = prepared.prep(sgeometry.Polygon())  # main collision poly.

    shift = tolerance  # one milimeter by now.
    rotchange = rotate_angle  # in radians

    xmin, ymin, xmax, ymax = polyfield[0][2].bounds
    if direction == "X":
        mindist = -xmin
    else:
        mindist = -ymin
    i = 0
    p = polyfield[0][2]
    placedpolys = []
    rotcenter = sgeometry.Point(0, 0)
    for pf in polyfield:
        print(i)
        rot = 0
        porig = pf[2]
        placed = False
        xmin, ymin, xmax, ymax = p.bounds
        if direction == "X":
            x = mindist
            y = -ymin
        if direction == "Y":
            x = -xmin
            y = mindist

        itera = 0
        best = None
        hits = 0
        besthit = None
        while not placed:
            # swap x and y, and add to x
            # print(x,y)
            p = porig

            if rotate:
                ptrans = affinity.rotate(p, rot, origin=rotcenter, use_radians=True)
                ptrans = affinity.translate(ptrans, x, y)
            else:
                ptrans = affinity.translate(p, x, y)
            xmin, ymin, xmax, ymax = ptrans.bounds
            # print(iter,p.bounds)

            if (
                xmin > 0
                and ymin > 0
                and (
                    (direction == "Y" and xmax < sheetsizex)
                    or (direction == "X" and ymax < sheetsizey)
                )
            ):
                if not allpoly.intersects(ptrans):
                    # we do more good solutions, choose best out of them:
                    hits += 1
                    if best is None:
                        best = [x, y, rot, xmax, ymax]
                        besthit = hits
                    if direction == "X":
                        if xmax < best[3]:
                            best = [x, y, rot, xmax, ymax]
                            besthit = hits
                    elif ymax < best[4]:
                        best = [x, y, rot, xmax, ymax]
                        besthit = hits

            if hits >= 15 or (
                itera > 20000 and hits > 0
            ):  # here was originally more, but 90% of best solutions are still 1
                placed = True
                pf[3].location.x = best[0]
                pf[3].location.y = best[1]
                pf[3].location.z = pf[4]
                pf[3].rotation_euler.z = best[2]

                pf[3].select_set(state=True)

                # print(mindist)
                mindist = mindist - 0.5 * (xmax - xmin)
                # print(mindist)
                # print(iter)

                # reset polygon to best position here:
                ptrans = affinity.rotate(porig, best[2], rotcenter, use_radians=True)
                ptrans = affinity.translate(ptrans, best[0], best[1])

                print(best[0], best[1], itera)
                placedpolys.append(ptrans)
                allpoly = prepared.prep(sgeometry.MultiPolygon(placedpolys))

                # cleanup allpoly
                print(itera, hits, besthit)
            if not placed:
                if direction == "Y":
                    x += shift
                    mindist = y
                    if xmax + shift > sheetsizex:
                        x = x - xmin
                        y += shift
                if direction == "X":
                    y += shift
                    mindist = x
                    if ymax + shift > sheetsizey:
                        y = y - ymin
                        x += shift
                if rotate:
                    rot += rotchange
            itera += 1
        i += 1
    t = time.time() - t

    shapely_to_curve("test", sgeometry.MultiPolygon(placedpolys), 0)
    print(t)
