"""Fabex 'bridges.py' © 2012 Vilem Novak

Functions to add Bridges / Tabs to meshes or curves.
Called with Operators defined in 'ops.py'
"""

from math import (
    hypot,
    pi,
)

from shapely import ops as sops
from shapely import geometry as sgeometry
from shapely import prepared

import bpy
from bpy_extras.object_utils import object_data_add
from mathutils import Vector

from .cam_chunk import (
    curve_to_shapely,
    get_object_silhouette,
    get_operation_silhouette,
)

from .utilities.operation_utils import get_operation_sources
from .utilities.simple_utils import join_multiple, remove_doubles


def add_bridge(x, y, rot, size_x, size_y):
    """Add a bridge mesh object to the scene.

    This function creates a bridge by adding a primitive plane to the
    Blender scene, adjusting its dimensions, and then converting it into a
    curve. The bridge is positioned based on the provided coordinates and
    rotation. The size of the bridge is determined by the `sizex` and
    `sizey` parameters.

    Args:
        x (float): The x-coordinate for the bridge's location.
        y (float): The y-coordinate for the bridge's location.
        rot (float): The rotation angle around the z-axis in radians.
        sizex (float): The width of the bridge.
        sizey (float): The height of the bridge.

    Returns:
        bpy.types.Object: The created bridge object.
    """

    bpy.ops.mesh.primitive_plane_add(
        size=size_y * 2,
        calc_uvs=True,
        enter_editmode=False,
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
    )
    b = bpy.context.active_object
    b.name = "bridge"
    # b.show_name=True
    b.dimensions.x = size_x
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.object.editmode_toggle()
    bpy.ops.transform.translate(
        value=(0, size_y / 2, 0),
        constraint_axis=(False, True, False),
        orient_type="GLOBAL",
        mirror=False,
        use_proportional_edit=False,
        proportional_edit_falloff="SMOOTH",
        proportional_size=1,
    )
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.convert(target="CURVE")

    b.location = x, y, 0
    b.rotation_euler.z = rot
    return b


def add_auto_bridges(o):
    """Attempt to add auto bridges as a set of curves.

    This function creates a collection of bridges based on the provided
    object. It checks if a collection for bridges already exists; if not, it
    creates a new one. The function then iterates through the objects in the
    input object, processing curves and meshes to generate bridge
    geometries. For each geometry, it calculates the necessary points and
    adds bridges at various orientations based on the geometry's bounds.

    Args:
        o (object): An object containing properties such as
            bridges_collection_name, bridges_width, and cutter_diameter,
            along with a list of objects to process.

    Returns:
        None: This function does not return a value but modifies the
            Blender context by adding bridge objects to the specified
            collection.
    """
    get_operation_sources(o)
    bridgecollectionname = o.bridges_collection_name
    if bridgecollectionname == "" or bpy.data.collections.get(bridgecollectionname) is None:
        bridgecollectionname = "bridges_" + o.name
        bpy.data.collections.new(bridgecollectionname)
        bpy.context.collection.children.link(bpy.data.collections[bridgecollectionname])
    g = bpy.data.collections[bridgecollectionname]
    o.bridges_collection_name = bridgecollectionname
    for ob in o.objects:
        if ob.type == "CURVE" or ob.type == "TEXT":
            curve = curve_to_shapely(ob)
        if ob.type == "MESH":
            curve = get_object_silhouette("OBJECTS", [ob])
        for c in curve.geoms:
            c = c.exterior
            minx, miny, maxx, maxy = c.bounds

            d1 = c.project(sgeometry.Point(maxx + 1000, (maxy + miny) / 2.0))
            p = c.interpolate(d1)
            bo = add_bridge(p.x, p.y, -pi / 2, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)

            d1 = c.project(sgeometry.Point(minx - 1000, (maxy + miny) / 2.0))
            p = c.interpolate(d1)
            bo = add_bridge(p.x, p.y, pi / 2, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)

            d1 = c.project(sgeometry.Point((minx + maxx) / 2.0, maxy + 1000))
            p = c.interpolate(d1)
            bo = add_bridge(p.x, p.y, 0, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)

            d1 = c.project(sgeometry.Point((minx + maxx) / 2.0, miny - 1000))
            p = c.interpolate(d1)
            bo = add_bridge(p.x, p.y, pi, o.bridges_width, o.cutter_diameter * 1)
            g.objects.link(bo)
            bpy.context.collection.objects.unlink(bo)


def get_bridges_poly(o):
    """Generate and prepare bridge polygons from a Blender object.

    This function checks if the provided object has an attribute for bridge
    polygons. If not, it retrieves the bridge collection, selects all curve
    objects within that collection, duplicates them, and joins them into a
    single object. The resulting shape is then converted to a Shapely
    geometry. The function buffers the resulting polygon to account for the
    cutter diameter and prepares the boundary and polygon for further
    processing.

    Args:
        o (object): An object containing properties related to bridge
    """

    if not hasattr(o, "bridgespolyorig"):
        bridgecollectionname = o.bridges_collection_name
        bridgecollection = bpy.data.collections[bridgecollectionname]
        bpy.ops.object.select_all(action="DESELECT")

        for ob in bridgecollection.objects:
            if ob.type == "CURVE":
                ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.duplicate()
        bpy.ops.object.join()
        ob = bpy.context.active_object
        shapes = curve_to_shapely(ob, o.use_bridge_modifiers)
        ob.select_set(state=True)
        bpy.ops.object.delete(use_global=False)
        bridgespoly = sops.unary_union(shapes)

        # buffer the poly, so the bridges are not actually milled...
        o.bridgespolyorig = bridgespoly.buffer(distance=o.cutter_diameter / 2.0)
        o.bridgespoly_boundary = o.bridgespolyorig.boundary
        o.bridgespoly_boundary_prep = prepared.prep(o.bridgespolyorig.boundary)
        o.bridgespoly = prepared.prep(o.bridgespolyorig)


def use_bridges(ch, o):
    """Add bridges to chunks using a collection of bridge objects.

    This function takes a collection of bridge objects and uses the curves
    within it to create bridges over the specified chunks. It calculates the
    necessary points for the bridges based on the height and geometry of the
    chunks and the bridge objects. The function also handles intersections
    with the bridge polygon and adjusts the points accordingly. Finally, it
    generates a mesh for the bridges and converts it into a curve object in
    Blender.

    Args:
        ch (Chunk): The chunk object to which bridges will be added.
        o (ObjectOptions): An object containing options such as bridge height,
            collection name, and other parameters.

    Returns:
        None: The function modifies the chunk object in place and does not return a
            value.
    """
    bridgecollectionname = o.bridges_collection_name
    if bridgecollectionname == "":
        bridgecollection = bpy.data.collections.new(bridgecollectionname)
    else:
        bridgecollection = bpy.data.collections[bridgecollectionname]
    if len(bridgecollection.objects) > 0:
        # get bridgepoly
        get_bridges_poly(o)

        ####

        bridgeheight = min(o.max.z, o.min.z + abs(o.bridges_height))

        vi = 0
        newpoints = []
        ch_points = ch.get_points_np()
        p1 = sgeometry.Point(ch_points[0])
        startinside = o.bridgespoly.contains(p1)
        interrupted = False
        verts = []
        edges = []
        faces = []
        while vi < len(ch_points):
            i1 = vi
            i2 = vi
            chp1 = ch_points[i1]
            # Vector(v1)#this is for case of last point and not closed chunk..
            chp2 = ch_points[i1]
            if vi + 1 < len(ch_points):
                i2 = vi + 1
                chp2 = ch_points[vi + 1]  # Vector(ch_points[vi+1])
            v1 = Vector(chp1)
            v2 = Vector(chp2)
            if v1.z < bridgeheight or v2.z < bridgeheight:
                v = v2 - v1
                p2 = sgeometry.Point(chp2)

                if interrupted:
                    p1 = sgeometry.Point(chp1)
                    startinside = o.bridgespoly.contains(p1)
                    interrupted = False

                endinside = o.bridgespoly.contains(p2)
                l = sgeometry.LineString([chp1, chp2])
                if o.bridgespoly_boundary_prep.intersects(l):
                    intersections = o.bridgespoly_boundary.intersection(l)

                else:
                    intersections = sgeometry.GeometryCollection()

                itpoint = intersections.geom_type == "Point"
                itmpoint = intersections.geom_type == "MultiPoint"

                if not startinside:
                    newpoints.append(chp1)
                elif startinside:
                    newpoints.append((chp1[0], chp1[1], max(chp1[2], bridgeheight)))
                cpoints = []
                if itpoint:
                    pt = Vector((intersections.x, intersections.y, intersections.z))
                    cpoints = [pt]

                elif itmpoint:
                    cpoints = []
                    for p in intersections.geoms:
                        pt = Vector((p.x, p.y, p.z))
                        cpoints.append(pt)
                # ####sort collisions here :(
                ncpoints = []
                while len(cpoints) > 0:
                    mind = 10000000
                    mini = -1
                    for i, p in enumerate(cpoints):
                        if min(mind, (p - v1).length) < mind:
                            mini = i
                            mind = (p - v1).length
                    ncpoints.append(cpoints.pop(mini))
                cpoints = ncpoints
                # endsorting

                if startinside:
                    isinside = True
                else:
                    isinside = False
                for cp in cpoints:
                    v3 = cp
                    # print(v3)
                    if v.length == 0:
                        ratio = 1
                    else:
                        fractvect = v3 - v1
                        ratio = fractvect.length / v.length

                    collisionz = v1.z + v.z * ratio
                    np1 = (v3.x, v3.y, collisionz)
                    np2 = (v3.x, v3.y, max(collisionz, bridgeheight))
                    if not isinside:
                        newpoints.extend((np1, np2))
                    else:
                        newpoints.extend((np2, np1))
                    isinside = not isinside

                startinside = endinside
                vi += 1
            else:
                newpoints.append(chp1)
                vi += 1
                interrupted = True
        ch.set_points(newpoints)

    # create bridge cut curve here
    count = 0
    isedge = 0
    x2, y2 = 0, 0
    for pt in newpoints:
        x = pt[0]
        y = pt[1]
        z = pt[2]
        if z == bridgeheight:  # find all points with z = bridge height
            count += 1
            if (
                isedge == 1
            ):  # This is to subdivide  edges which are longer than the width of the bridge
                edgelength = hypot(x - x2, y - y2)
                if edgelength > o.bridges_width:
                    # make new vertex
                    verts.append(((x + x2) / 2, (y + y2) / 2, o.min_z))

                    isedge += 1
                    edge = [count - 2, count - 1]
                    edges.append(edge)
                    count += 1
            else:
                x2 = x
                y2 = y
            verts.append((x, y, o.min_z))  # make new vertex
            isedge += 1
            if isedge > 1:  # Two points make an edge
                edge = [count - 2, count - 1]
                edges.append(edge)

        else:
            isedge = 0

    #  verify if vertices have been generated and generate a mesh
    if verts:
        mesh = bpy.data.meshes.new(name=o.name + "_cut_bridges")  # generate new mesh
        # integrate coordinates and edges
        mesh.from_pydata(verts, edges, faces)
        object_data_add(bpy.context, mesh)  # create object
        bpy.ops.object.convert(target="CURVE")  # convert mesh to curve
        # join all the new cut bridges curves
        join_multiple(o.name + "_cut_bridges")
        remove_doubles()  # remove overlapping vertices


def auto_cut_bridge(o):
    """Automatically processes a bridge collection.

    This function retrieves a bridge collection by its name from the
    provided object and checks if there are any objects within that
    collection. If there are objects present, it prints "bridges" to the
    console. This function is useful for managing and processing bridge
    collections in a 3D environment.

    Args:
        o (object): An object that contains the attribute

    Returns:
        None: This function does not return any value.
    """

    bridgecollectionname = o.bridges_collection_name
    bridgecollection = bpy.data.collections[bridgecollectionname]
    if len(bridgecollection.objects) > 0:
        print("bridges")
