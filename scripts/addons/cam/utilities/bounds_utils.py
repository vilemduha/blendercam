"""Fabex 'bounds_utils.py' © 2012 Vilem Novak
"""

import time

import bpy
from mathutils import Vector

from .shapely_utils import shapely_to_curve, shapely_to_multipolygon
from .simple_utils import (
    activate,
    progress,
    unit_value_to_string,
)
from ..exception import CamException


def get_bounds_worldspace(obs, use_modifiers=False):
    """Get the bounding box of a list of objects in world space.

    This function calculates the minimum and maximum coordinates that
    encompass all the specified objects in the 3D world space. It iterates
    through each object, taking into account their transformations and
    modifiers if specified. The function supports different object types,
    including meshes and fonts, and handles the conversion of font objects
    to mesh format for accurate bounding box calculations.

    Args:
        obs (list): A list of Blender objects to calculate bounds for.
        use_modifiers (bool): If True, apply modifiers to the objects
            before calculating bounds. Defaults to False.

    Returns:
        tuple: A tuple containing the minimum and maximum coordinates
            in the format (minx, miny, minz, maxx, maxy, maxz).

    Raises:
        CamException: If an object type does not support CAM operations.
    """

    # progress('getting bounds of object(s)')
    t = time.time()

    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    for ob in obs:
        # bb=ob.bound_box
        mw = ob.matrix_world
        if ob.type == "MESH":
            if use_modifiers:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                mesh_owner = ob.evaluated_get(depsgraph)
                mesh = mesh_owner.to_mesh()
            else:
                mesh = ob.data

            for c in mesh.vertices:
                coord = c.co
                worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                minx = min(minx, worldCoord.x)
                miny = min(miny, worldCoord.y)
                minz = min(minz, worldCoord.z)
                maxx = max(maxx, worldCoord.x)
                maxy = max(maxy, worldCoord.y)
                maxz = max(maxz, worldCoord.z)

            if use_modifiers:
                mesh_owner.to_mesh_clear()

        elif ob.type == "FONT":
            activate(ob)
            bpy.ops.object.duplicate()
            co = bpy.context.active_object
            bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
            bpy.ops.object.convert(target="MESH", keep_original=False)
            mesh = co.data
            for c in mesh.vertices:
                coord = c.co
                worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                minx = min(minx, worldCoord.x)
                miny = min(miny, worldCoord.y)
                minz = min(minz, worldCoord.z)
                maxx = max(maxx, worldCoord.x)
                maxy = max(maxy, worldCoord.y)
                maxz = max(maxz, worldCoord.z)
            bpy.ops.object.delete()
            bpy.ops.outliner.orphans_purge()
        else:
            if not hasattr(ob.data, "splines"):
                raise CamException("Can't do CAM operation on the selected object type")
            # for coord in bb:
            for c in ob.data.splines:
                for p in c.bezier_points:
                    coord = p.co
                    # this can work badly with some imported curves, don't know why...
                    # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
                    worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                    minx = min(minx, worldCoord.x)
                    miny = min(miny, worldCoord.y)
                    minz = min(minz, worldCoord.z)
                    maxx = max(maxx, worldCoord.x)
                    maxy = max(maxy, worldCoord.y)
                    maxz = max(maxz, worldCoord.z)
                for p in c.points:
                    coord = p.co
                    # this can work badly with some imported curves, don't know why...
                    # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
                    worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
                    minx = min(minx, worldCoord.x)
                    miny = min(miny, worldCoord.y)
                    minz = min(minz, worldCoord.z)
                    maxx = max(maxx, worldCoord.x)
                    maxy = max(maxy, worldCoord.y)
                    maxz = max(maxz, worldCoord.z)
    # progress(time.time()-t)
    return minx, miny, minz, maxx, maxy, maxz


def get_spline_bounds(ob, curve):
    """Get the bounding box of a spline object.

    This function calculates the minimum and maximum coordinates (x, y, z)
    of the given spline object by iterating through its bezier points and
    regular points. It transforms the local coordinates to world coordinates
    using the object's transformation matrix. The resulting bounds can be
    used for various purposes, such as collision detection or rendering.

    Args:
        ob (Object): The object containing the spline whose bounds are to be calculated.
        curve (Curve): The curve object that contains the bezier points and regular points.

    Returns:
        tuple: A tuple containing the minimum and maximum coordinates in the
        format (minx, miny, minz, maxx, maxy, maxz).
    """

    # progress('getting bounds of object(s)')
    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    mw = ob.matrix_world

    for p in curve.bezier_points:
        coord = p.co
        # this can work badly with some imported curves, don't know why...
        # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
        worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
        minx = min(minx, worldCoord.x)
        miny = min(miny, worldCoord.y)
        minz = min(minz, worldCoord.z)
        maxx = max(maxx, worldCoord.x)
        maxy = max(maxy, worldCoord.y)
        maxz = max(maxz, worldCoord.z)
    for p in curve.points:
        coord = p.co
        # this can work badly with some imported curves, don't know why...
        # worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
        worldCoord = mw @ Vector((coord[0], coord[1], coord[2]))
        minx = min(minx, worldCoord.x)
        miny = min(miny, worldCoord.y)
        minz = min(minz, worldCoord.z)
        maxx = max(maxx, worldCoord.x)
        maxy = max(maxy, worldCoord.y)
        maxz = max(maxz, worldCoord.z)
    # progress(time.time()-t)
    return minx, miny, minz, maxx, maxy, maxz


def get_bounds(o):
    """Calculate the bounding box for a given object.

    This function determines the minimum and maximum coordinates of an
    object's bounding box based on its geometry source. It handles different
    geometry types such as OBJECT, COLLECTION, and CURVE. The function also
    considers material properties and image cropping if applicable. The
    bounding box is adjusted according to the object's material settings and
    the optimization parameters defined in the object.

    Args:
        o (object): An object containing geometry and material properties, as well as
            optimization settings.

    Returns:
        None: This function modifies the input object in place and does not return a
            value.
    """

    # print('kolikrat sem rpijde')
    if (
        o.geometry_source == "OBJECT"
        or o.geometry_source == "COLLECTION"
        or o.geometry_source == "CURVE"
    ):
        print("Valid Geometry")
        minx, miny, minz, maxx, maxy, maxz = get_bounds_worldspace(o.objects, o.use_modifiers)

        if o.min_z_from == "OBJECT":
            if minz == 10000000:
                minz = 0
            print("Min Z from Object:" + str(minz))
            o.min.z = minz
            o.min_z = o.min.z
        else:
            o.min.z = o.min_z  # max(bb[0][2]+l.z,o.min_z)#
            print("Not Min Z from Object")

        if o.material.estimate_from_model:
            print("Estimate Material from Model")

            o.min.x = minx - o.material.radius_around_model
            o.min.y = miny - o.material.radius_around_model
            o.max.z = max(o.max_z, maxz)

            o.max.x = maxx + o.material.radius_around_model
            o.max.y = maxy + o.material.radius_around_model
        else:
            print("Not Material from Model")
            o.min.x = o.material.origin.x
            o.min.y = o.material.origin.y
            o.min.z = o.material.origin.z - o.material.size.z
            o.max.x = o.min.x + o.material.size.x
            o.max.y = o.min.y + o.material.size.y
            o.max.z = o.material.origin.z

    else:
        i = bpy.data.images[o.source_image_name]
        if o.source_image_crop:
            sx = int(i.size[0] * o.source_image_crop_start_x / 100)
            ex = int(i.size[0] * o.source_image_crop_end_x / 100)
            sy = int(i.size[1] * o.source_image_crop_start_y / 100)
            ey = int(i.size[1] * o.source_image_crop_end_y / 100)
        else:
            sx = 0
            ex = i.size[0]
            sy = 0
            ey = i.size[1]

        o.optimisation.pixsize = o.source_image_size_x / i.size[0]

        o.min.x = o.source_image_offset.x + sx * o.optimisation.pixsize
        o.max.x = o.source_image_offset.x + ex * o.optimisation.pixsize
        o.min.y = o.source_image_offset.y + sy * o.optimisation.pixsize
        o.max.y = o.source_image_offset.y + ey * o.optimisation.pixsize
        o.min.z = o.source_image_offset.z + o.min_z
        o.max.z = o.source_image_offset.z
    s = bpy.context.scene
    m = s.cam_machine

    x_delta_range = o.max.x - o.min.x
    y_delta_range = o.max.y - o.min.y
    z_delta_range = o.max.z - o.min.z

    x_is_exceeded = x_delta_range > m.working_area.x
    y_is_exceeded = y_delta_range > m.working_area.y
    z_is_exceeded = z_delta_range > m.working_area.z

    if x_is_exceeded or y_is_exceeded or z_is_exceeded:
        exceed_msg = "Operation Exceeds Your Machine Limits (range > working area)\n"

        # Do not append more than one such a warning
        if exceed_msg not in o.info.warnings:
            o.info.warnings += exceed_msg

            if x_is_exceeded:
                o.info.warnings += (
                    f"Axis X[ range:{unit_value_to_string(x_delta_range)}"
                    + f", working area:{unit_value_to_string(m.working_area.x)}]\n"
                )
            if y_is_exceeded:
                o.info.warnings += (
                    f"Axis Y[ range:{unit_value_to_string(y_delta_range)}"
                    + f", working area:{unit_value_to_string(m.working_area.y)}]\n"
                )
            if z_is_exceeded:
                o.info.warnings += (
                    f"Axis Z[ range:{unit_value_to_string(z_delta_range)}"
                    + f", working area:{unit_value_to_string(m.working_area.z)}]\n"
                )

    if not o.info.warnings == "":
        addon_prefs = bpy.context.preferences.addons["bl_ext.user_default.fabex"].preferences
        if addon_prefs.show_popups:
            bpy.ops.cam.popup("INVOKE_DEFAULT")


def get_bounds_multiple(operations):
    """Gets bounds of multiple operations for simulations or rest milling.

    This function iterates through a list of operations to determine the
    minimum and maximum bounds in three-dimensional space (x, y, z). It
    initializes the bounds to extreme values and updates them based on the
    bounds of each operation. The function is primarily intended for use in
    simulations or rest milling processes, although it is noted that the
    implementation may not be optimal.

    Args:
        operations (list): A list of operation objects, each containing
            'min' and 'max' attributes with 'x', 'y',
            and 'z' coordinates.

    Returns:
        tuple: A tuple containing the minimum and maximum bounds in the
            order (minx, miny, minz, maxx, maxy, maxz).
    """
    maxx = maxy = maxz = -10000000
    minx = miny = minz = 10000000
    for o in operations:
        get_bounds(o)
        maxx = max(maxx, o.max.x)
        maxy = max(maxy, o.max.y)
        maxz = max(maxz, o.max.z)
        minx = min(minx, o.min.x)
        miny = min(miny, o.min.y)
        minz = min(minz, o.min.z)

    return minx, miny, minz, maxx, maxy, maxz


def position_object(operation):
    """Position an object based on specified operation parameters.

    This function adjusts the location of a Blender object according to the
    provided operation settings. It calculates the bounding box of the
    object in world space and modifies its position based on the material's
    center settings and specified z-positioning (BELOW, ABOVE, or CENTERED).
    The function also applies transformations to the object if it is not of
    type 'CURVE'.

    Args:
        operation (OperationType): An object containing parameters for positioning,
            including object_name, use_modifiers, and material
            settings.
    """

    ob = bpy.data.objects[operation.object_name]
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    minx, miny, minz, maxx, maxy, maxz = get_bounds_worldspace([ob], operation.use_modifiers)
    totx = maxx - minx
    toty = maxy - miny
    totz = maxz - minz
    if operation.material.center_x:
        ob.location.x -= minx + totx / 2
    else:
        ob.location.x -= minx

    if operation.material.center_y:
        ob.location.y -= miny + toty / 2
    else:
        ob.location.y -= miny

    if operation.material.z_position == "BELOW":
        ob.location.z -= maxz
    elif operation.material.z_position == "ABOVE":
        ob.location.z -= minz
    elif operation.material.z_position == "CENTERED":
        ob.location.z -= minz + totz / 2

    if ob.type != "CURVE":
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
