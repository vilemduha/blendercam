from shapely.geometry import (
    MultiPoint,
    MultiPolygon,
)

import bpy


from .shapely_utils import shapely_to_curve
from .simple_utils import select_multiple


def polygon_boolean(context, boolean_type):
    """Perform a boolean operation on selected polygons.

    This function takes the active object and applies a specified boolean
    operation (UNION, DIFFERENCE, or INTERSECT) with respect to other
    selected objects in the Blender context. It first converts the polygons
    of the active object and the selected objects into a Shapely
    MultiPolygon. Depending on the boolean type specified, it performs the
    corresponding boolean operation and then converts the result back into a
    Blender curve.

    Args:
        context (bpy.context): The Blender context containing scene and object data.
        boolean_type (str): The type of boolean operation to perform.
            Must be one of 'UNION', 'DIFFERENCE', or 'INTERSECT'.

    Returns:
        dict: A dictionary indicating the operation result, typically {'FINISHED'}.
    """

    bpy.context.scene.cursor.location = (0, 0, 0)
    ob = bpy.context.active_object
    obs = []

    for ob1 in bpy.context.selected_objects:
        if ob1 != ob:
            obs.append(ob1)

    plist = curve_to_shapely(ob)
    p1 = MultiPolygon(plist)
    polys = []

    for o in obs:
        plist = curve_to_shapely(o)
        p2 = MultiPolygon(plist)
        polys.append(p2)

    if boolean_type == "UNION":
        for p2 in polys:
            p1 = p1.union(p2)
    elif boolean_type == "DIFFERENCE":
        for p2 in polys:
            p1 = p1.difference(p2)
    elif boolean_type == "INTERSECT":
        for p2 in polys:
            p1 = p1.intersection(p2)

    shapely_to_curve("boolean", p1, ob.location.z)

    return {"FINISHED"}


def polygon_convex_hull(context):
    """Generate the convex hull of a polygon from the given context.

    This function duplicates the current object, joins it, and converts it
    into a 3D mesh. It then extracts the X and Y coordinates of the vertices
    to create a MultiPoint data structure using Shapely. Finally, it
    computes the convex hull of these points and converts the result back
    into a curve named 'ConvexHull'. Temporary objects created during this
    process are deleted to maintain a clean workspace.

    Args:
        context: The context in which the operation is performed, typically
            related to Blender's current state.

    Returns:
        dict: A dictionary indicating the operation's completion status.
    """

    bpy.ops.object.duplicate()
    bpy.ops.object.join()
    # force curve to be a 3D curve
    bpy.context.object.data.dimensions = "3D"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.name = "_tmp"
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.view_layer.objects.active

    # extract X,Y coordinates from the vertices data
    coords = [(v.co.x, v.co.y) for v in obj.data.vertices]

    select_multiple("_tmp")  # delete temporary mesh
    select_multiple("ConvexHull")  # delete old hull
    # convert coordinates to shapely MultiPoint datastructure
    points = MultiPoint(coords)
    hull = points.convex_hull
    shapely_to_curve("ConvexHull", hull, 0.0)

    return {"FINISHED"}
