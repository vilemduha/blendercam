"""Fabex 'shapely_utils.py' © 2012 Vilem Novak

Functions to handle shapely operations and conversions - curve, coords, polygon
"""

from math import pi

import shapely
from shapely.geometry import polygon as spolygon
from shapely import geometry as sgeometry

from mathutils import Euler, Vector

try:
    import bl_ext.blender_org.simplify_curves_plus as curve_simplify
except ImportError:
    pass


from ..constants import SHAPELY


def shapely_remove_doubles(p, optimize_threshold):
    """Remove duplicate points from the boundary of a shape.

    This function simplifies the boundary of a given shape by removing
    duplicate points using the Ramer-Douglas-Peucker algorithm. It iterates
    through each contour of the shape, applies the simplification, and adds
    the resulting contours to a new shape. The optimization threshold can be
    adjusted to control the level of simplification.

    Args:
        p (Shape): The shape object containing boundaries to be simplified.
        optimize_threshold (float): A threshold value that influences the
            simplification process.

    Returns:
        Shape: A new shape object with simplified boundaries.
    """

    optimize_threshold *= 0.000001

    soptions = ["distance", "distance", 0.0, 5, optimize_threshold, 5, optimize_threshold]
    for ci, c in enumerate(p.boundary):  # in range(0,len(p)):
        veclist = []
        for v in c:
            veclist.append(Vector((v[0], v[1])))
        s = curve_simplify.simplify_RDP(veclist, soptions)
        nc = []
        for i in range(0, len(s)):
            nc.append(c[s[i]])

        if len(nc) > 2:
            pnew.addContour(nc, p.isHole(ci))
        else:
            pnew.addContour(p[ci], p.isHole(ci))
    return pnew


def shapely_to_multipolygon(anydata):
    """Convert a Shapely geometry to a MultiPolygon.

    This function takes a Shapely geometry object and converts it to a
    MultiPolygon. If the input geometry is already a MultiPolygon, it
    returns it as is. If the input is a Polygon and not empty, it wraps the
    Polygon in a MultiPolygon. If the input is an empty Polygon, it returns
    an empty MultiPolygon. For any other geometry type, it prints a message
    indicating that the conversion was aborted and returns an empty
    MultiPolygon.

    Args:
        anydata (shapely.geometry.base.BaseGeometry): A Shapely geometry object

    Returns:
        shapely.geometry.MultiPolygon: A MultiPolygon representation of the input
        geometry.
    """
    print("Geometry Type: ", anydata.geom_type)
    print("Anydata Empty: ", anydata.is_empty)
    ## bug: empty mesh circle makes anydata empty: geometry type 'GeometryCollection'
    if anydata.geom_type == "MultiPolygon":
        return anydata
    elif anydata.geom_type == "Polygon":
        if not anydata.is_empty:
            return shapely.geometry.MultiPolygon([anydata])
        else:
            return sgeometry.MultiPolygon()
    else:
        print("Shapely Conversion Aborted")
        return sgeometry.MultiPolygon()


def shapely_to_coordinates(anydata):
    """Convert a Shapely geometry object to a list of coordinates.

    This function takes a Shapely geometry object and extracts its
    coordinates based on the geometry type. It handles various types of
    geometries including Polygon, MultiPolygon, LineString, MultiLineString,
    and GeometryCollection. If the geometry is empty or of type MultiPoint,
    it returns an empty list. The coordinates are returned in a nested list
    format, where each sublist corresponds to the exterior or interior
    coordinates of the geometries.

    Args:
        anydata (shapely.geometry.base.BaseGeometry): A Shapely geometry object

    Returns:
        list: A list of coordinates extracted from the input geometry.
        The structure of the list depends on the geometry type.
    """

    p = anydata
    seq = []

    if p.is_empty:
        return seq
    elif p.geom_type == "Polygon":
        clen = len(p.exterior.coords)
        seq = [p.exterior.coords]
        for interior in p.interiors:
            seq.append(interior.coords)
    elif p.geom_type == "MultiPolygon":
        clen = 0
        seq = []
        for sp in p.geoms:
            clen += len(sp.exterior.coords)
            seq.append(sp.exterior.coords)
            for interior in sp.interiors:
                seq.append(interior.coords)

    elif p.geom_type == "MultiLineString":
        seq = []
        for linestring in p.geoms:
            seq.append(linestring.coords)
    elif p.geom_type == "LineString":
        seq = []
        seq.append(p.coords)

    elif p.geom_type == "MultiPoint":
        return
    elif p.geom_type == "GeometryCollection":
        clen = 0
        seq = []
        for sp in p.geoms:  # TODO
            clen += len(sp.exterior.coords)
            seq.append(sp.exterior.coords)
            for interior in sp.interiors:
                seq.extend(interior.coords)

    return seq


def shapely_to_curve(name, p, z, cyclic=True):
    """Create a 3D curve object in Blender from a Shapely geometry.

    This function takes a Shapely geometry and converts it into a 3D curve
    object in Blender. It extracts the coordinates from the Shapely geometry
    and creates a new curve object with the specified name. The curve is
    created in the 3D space at the given z-coordinate, with a default weight
    for the points.

    Args:
        name (str): The name of the curve object to be created.
        p (shapely.geometry): A Shapely geometry object from which to extract
            coordinates.
        z (float): The z-coordinate for all points of the curve.

    Returns:
        bpy.types.Object: The newly created curve object in Blender.
    """

    import bpy
    import bmesh
    from bpy_extras import object_utils

    verts = []
    edges = []
    vi = 0
    ci = 0

    seq = shapely_to_coordinates(p)
    w = 1  # weight

    curvedata = bpy.data.curves.new(name=name, type="CURVE")
    curvedata.dimensions = "3D"

    objectdata = bpy.data.objects.new(name, curvedata)
    objectdata.location = (0, 0, 0)  # object origin
    bpy.context.collection.objects.link(objectdata)

    for c in seq:
        polyline = curvedata.splines.new("POLY")
        polyline.points.add(len(c) - 1)
        for num in range(len(c)):
            x, y = c[num][0], c[num][1]
            polyline.points[num].co = (x, y, z, w)

    bpy.context.view_layer.objects.active = objectdata
    objectdata.select_set(state=True)

    for c in objectdata.data.splines:
        c.use_cyclic_u = cyclic

    return objectdata  # bpy.context.active_object
