"""Fabex 'orient_utils.py' © 2012 Vilem Novak"""

import bpy
from mathutils import Vector

from .logging_utils import log
from .simple_utils import delete_object


def add_orientation_object(o):
    """Set up orientation for a milling object.

    This function creates an orientation object in the Blender scene for
    4-axis and 5-axis milling operations. It checks if an orientation object
    with the specified name already exists, and if not, it adds a new empty
    object of type 'ARROWS'. The function then configures the rotation locks
    and initial rotation angles based on the specified machine axes and
    rotary axis.

    Args:
        o (object): An object containing properties such as name,
    """
    name = f"{o.name}_Orientation"
    s = bpy.context.scene
    if name not in s.objects:
        bpy.ops.object.empty_add(type="ARROWS", align="WORLD", location=(0, 0, 0))

        ob = bpy.context.active_object
        # ob.empty_draw_size = 0.05
        # ob.show_name = True
        ob.name = name
    ob = s.objects[name]
    if o.machine_axes == "4":
        if o.rotary_axis_1 == "X":
            ob.lock_rotation = [False, True, True]
            ob.rotation_euler[1] = 0
            ob.rotation_euler[2] = 0
        if o.rotary_axis_1 == "Y":
            ob.lock_rotation = [True, False, True]
            ob.rotation_euler[0] = 0
            ob.rotation_euler[2] = 0
        if o.rotary_axis_1 == "Z":
            ob.lock_rotation = [True, True, False]
            ob.rotation_euler[0] = 0
            ob.rotation_euler[1] = 0
    elif o.machine_axes == "5":
        ob.lock_rotation = [False, False, True]

        ob.rotation_euler[2] = 0  # this will be a bit hard to rotate.....


def remove_orientation_object(o):
    """Remove an orientation object from the current Blender scene.

    This function constructs the name of the orientation object based on the
    name of the provided object and attempts to find and delete it from the
    Blender scene. If the orientation object exists, it will be removed
    using the `delob` function.

    Args:
        o (Object): The object whose orientation object is to be removed.
    """
    # not working
    name = o.name + " orientation"
    if bpy.context.scene.objects.find(name) > -1:
        ob = bpy.context.scene.objects[name]
        delete_object(ob)


def rotation_to_2_axes(e, axescombination):
    """Converts an Orientation Object Rotation to Rotation Defined by 2
    Rotational Axes on the Machine.

    This function takes an orientation object and a specified axes
    combination, and computes the angles of rotation around two axes based
    on the provided orientation. It supports different axes combinations for
    indexed machining. The function utilizes vector mathematics to determine
    the angles of rotation and returns them as a tuple.

    Args:
        e (OrientationObject): The orientation object representing the rotation.
        axescombination (str): A string indicating the axes combination ('CA' or 'CB').

    Returns:
        tuple: A tuple containing two angles (float) representing the rotation
        around the specified axes.
    """
    v = Vector((0, 0, 1))
    v.rotate(e)
    # if axes
    if axescombination == "CA":
        v2d = Vector((v.x, v.y))
        # ?is this right?It should be vector defining 0 rotation
        a1base = Vector((0, -1))
        if v2d.length > 0:
            cangle = a1base.angle_signed(v2d)
        else:
            return (0, 0)
        v2d = Vector((v2d.length, v.z))
        a2base = Vector((0, 1))
        aangle = a2base.angle_signed(v2d)
        log.info(f"Angles {cangle}, {aangle}")
        return (cangle, aangle)

    elif axescombination == "CB":
        v2d = Vector((v.x, v.y))
        # ?is this right?It should be vector defining 0 rotation
        a1base = Vector((1, 0))
        if v2d.length > 0:
            cangle = a1base.angle_signed(v2d)
        else:
            return (0, 0)
        v2d = Vector((v2d.length, v.z))
        a2base = Vector((0, 1))

        bangle = a2base.angle_signed(v2d)

        log.info(f"Angles {cangle}, {bangle}")

        return (cangle, bangle)
