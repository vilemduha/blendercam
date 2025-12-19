"""Fabex 'shapely_utils.py' © 2012 Vilem Novak

Functions to handle shapely operations and conversions - curve, coords, polygon
"""

import shapely
from shapely.geometry import (
    Polygon,
    MultiPolygon,
)

from mathutils import Vector

try:
    import bl_ext.blender_org.simplify_curves_plus as curve_simplify
except ImportError:
    pass

from .chunk_builder import CamPathChunkBuilder
from .logging_utils import log


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
    log.info(f"Geometry Type: {anydata.geom_type}")
    log.info(f"Anydata Empty: {anydata.is_empty}")
    ## bug: empty mesh circle makes anydata empty: geometry type 'GeometryCollection'
    if anydata.geom_type == "MultiPolygon":
        return anydata
    elif anydata.geom_type == "Polygon":
        if not anydata.is_empty:
            return shapely.geometry.MultiPolygon([anydata])
        else:
            return MultiPolygon()
    else:
        log.info("Shapely Conversion Aborted")
        return MultiPolygon()


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


def image_to_shapely(o, i, with_border=False):
    """Convert an image to Shapely polygons.

    This function takes an image and converts it into a series of Shapely
    polygon objects. It first processes the image into chunks and then
    transforms those chunks into polygon geometries. The `with_border`
    parameter allows for the inclusion of borders in the resulting polygons.

    Args:
        o: The input image to be processed.
        i: Additional input parameters for processing the image.
        with_border (bool): A flag indicating whether to include
            borders in the resulting polygons. Defaults to False.

    Returns:
        list: A list of Shapely polygon objects created from the
            image chunks.
    """

    polychunks = image_to_chunks(o, i, with_border)
    polys = chunks_to_shapely(polychunks)

    return polys


def curve_to_shapely(cob, use_modifiers=False):
    """Convert a curve object to Shapely polygons.

    This function takes a curve object and converts it into a list of
    Shapely polygons. It first breaks the curve into chunks and then
    transforms those chunks into Shapely-compatible polygon representations.
    The `use_modifiers` parameter allows for additional processing of the
    curve before conversion, depending on the specific requirements of the
    application.

    Args:
        cob: The curve object to be converted.
        use_modifiers (bool): A flag indicating whether to apply modifiers
            during the conversion process. Defaults to False.

    Returns:
        list: A list of Shapely polygons created from the curve object.
    """

    chunks = curve_to_chunks(cob, use_modifiers)
    polys = chunks_to_shapely(chunks)
    return polys


# this does more cleve chunks to Poly with hierarchies... ;)
def chunks_to_shapely(chunks):
    # print ('analyzing paths')
    for ch in chunks:  # first convert chunk to poly
        if len(ch.points) > 2:
            # pchunk=[]
            ch.poly = Polygon(ch.points[:, 0:2])
            if not ch.poly.is_valid:
                ch.poly = Polygon()
        else:
            ch.poly = Polygon()

    for ppart in chunks:  # then add hierarchy relations
        for ptest in chunks:
            if ppart != ptest:
                if not ppart.poly.is_empty and not ptest.poly.is_empty:
                    if ptest.poly.contains(ppart.poly):
                        # hierarchy works like this: - children get milled first.
                        ppart.parents.append(ptest)

    for ch in chunks:  # now make only simple polygons with holes, not more polys inside others
        found = False
        if len(ch.parents) % 2 == 1:
            for parent in ch.parents:
                if len(parent.parents) + 1 == len(ch.parents):
                    # nparents serves as temporary storage for parents,
                    ch.nparents = [parent]
                    # not to get mixed with the first parenting during the check
                    found = True
                    break

        if not found:
            ch.nparents = []

    for ch in chunks:  # then subtract the 1st level holes
        ch.parents = ch.nparents
        ch.nparents = None
        if len(ch.parents) > 0:
            try:
                ch.parents[0].poly = ch.parents[0].poly.difference(
                    ch.poly
                )  # Polygon( ch.parents[0].poly, ch.poly)
            except:
                log.info("chunksToShapely oops!")

                lastPt = None
                tolerance = 0.0000003
                newPoints = []

                for pt in ch.points:
                    toleranceXok = True
                    toleranceYok = True
                    if lastPt is not None:
                        if abs(pt[0] - lastPt[0]) < tolerance:
                            toleranceXok = False
                        if abs(pt[1] - lastPt[1]) < tolerance:
                            toleranceYok = False

                        if toleranceXok or toleranceYok:
                            newPoints.append(pt)
                            lastPt = pt
                    else:
                        newPoints.append(pt)
                        lastPt = pt

                toleranceXok = True
                toleranceYok = True
                if abs(newPoints[0][0] - lastPt[0]) < tolerance:
                    toleranceXok = False
                if abs(newPoints[0][1] - lastPt[1]) < tolerance:
                    toleranceYok = False

                if not toleranceXok and not toleranceYok:
                    newPoints.pop()

                ch.points = np.array(newPoints)
                ch.poly = Polygon(ch.points)

                try:
                    ch.parents[0].poly = ch.parents[0].poly.difference(ch.poly)
                except:
                    # print('chunksToShapely double oops!')

                    lastPt = None
                    tolerance = 0.0000003
                    newPoints = []

                    for pt in ch.parents[0].points:
                        toleranceXok = True
                        toleranceYok = True
                        # print( '{0:.9f}, {0:.9f}, {0:.9f}'.format(pt[0], pt[1], pt[2]) )
                        # print(pt)
                        if lastPt is not None:
                            if abs(pt[0] - lastPt[0]) < tolerance:
                                toleranceXok = False
                            if abs(pt[1] - lastPt[1]) < tolerance:
                                toleranceYok = False

                            if toleranceXok or toleranceYok:
                                newPoints.append(pt)
                                lastPt = pt
                        else:
                            newPoints.append(pt)
                            lastPt = pt

                    toleranceXok = True
                    toleranceYok = True
                    if abs(newPoints[0][0] - lastPt[0]) < tolerance:
                        toleranceXok = False
                    if abs(newPoints[0][1] - lastPt[1]) < tolerance:
                        toleranceYok = False

                    if not toleranceXok and not toleranceYok:
                        newPoints.pop()
                    # print('starting and ending points too close, removing ending point')

                    ch.parents[0].points = np.array(newPoints)
                    ch.parents[0].poly = Polygon(ch.parents[0].points)

                    ch.parents[0].poly = ch.parents[0].poly.difference(
                        ch.poly
                    )  # Polygon( ch.parents[0].poly, ch.poly)

    returnpolys = []

    for polyi in range(0, len(chunks)):  # export only the booleaned polygons
        ch = chunks[polyi]

        if not ch.poly.is_empty:
            if len(ch.parents) == 0:
                returnpolys.append(ch.poly)

    polys = MultiPolygon(returnpolys)
    return polys


def shapely_to_chunks(p, zlevel):
    chunk_builders = []
    seq = shapely_to_coordinates(p)
    i = 0

    for s in seq:
        if len(s) > 1:
            chunk = CamPathChunkBuilder([])

            for v in s:
                if p.has_z:
                    chunk.points.append((v[0], v[1], v[2]))
                else:
                    chunk.points.append((v[0], v[1], zlevel))

            chunk_builders.append(chunk)
        i += 1
    chunk_builders.reverse()  # this is for smaller shapes first.
    return [c.to_chunk() for c in chunk_builders]
