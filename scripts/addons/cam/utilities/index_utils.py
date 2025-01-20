"""Fabex 'index_utils.py' © 2012 Vilem Novak
"""

from pathlib import Path

import shapely

import bpy

from .simple_utils import activate
from .orient_utils import rotation_to_2_axes


def prepare_indexed(o):
    """Prepare and index objects in the given collection.

    This function stores the world matrices and parent relationships of the
    objects in the provided collection. It then clears the parent
    relationships while maintaining their transformations, sets the
    orientation of the objects based on a specified orientation object, and
    finally re-establishes the parent-child relationships with the
    orientation object. The function also resets the location and rotation
    of the orientation object to the origin.

    Args:
        o (ObjectCollection): A collection of objects to be prepared and indexed.
    """

    s = bpy.context.scene
    # first store objects positions/rotations
    o.matrices = []
    o.parents = []
    for ob in o.objects:
        o.matrices.append(ob.matrix_world.copy())
        o.parents.append(ob.parent)

    # then rotate them
    for ob in o.objects:
        ob.select_set(True)
    s.objects.active = ob
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")

    s.cursor.location = (0, 0, 0)
    oriname = o.name + " orientation"
    ori = s.objects[oriname]
    o.orientation_matrix = ori.matrix_world.copy()
    o.rotationaxes = rotation_to_2_axes(ori.rotation_euler, "CA")
    ori.select_set(True)
    s.objects.active = ori
    # we parent all objects to the orientation object
    bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)
    for ob in o.objects:
        ob.select_set(False)
    # then we move the orientation object to 0,0
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    ori.select_set(False)
    for ob in o.objects:
        activate(ob)

        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")


def cleanup_indexed(operation):
    """Clean up indexed operations by updating object orientations and paths.

    This function takes an operation object and updates the orientation of a
    specified object in the scene based on the provided orientation matrix.
    It also sets the location and rotation of a camera path object to match
    the updated orientation. Additionally, it reassigns parent-child
    relationships for the objects involved in the operation and updates
    their world matrices.

    Args:
        operation (OperationType): An object containing the necessary data
    """

    s = bpy.context.scene
    oriname = operation.name + "orientation"

    ori = s.objects[oriname]
    path = s.objects["cam_path_{}{}".format(operation.name)]

    ori.matrix_world = operation.orientation_matrix
    # set correct path location
    path.location = ori.location
    path.rotation_euler = ori.rotation_euler

    print(ori.matrix_world, operation.orientation_matrix)
    # TODO: fix this here wrong order can cause objects out of place
    for i, ob in enumerate(operation.objects):
        ob.parent = operation.parents[i]
    for i, ob in enumerate(operation.objects):
        ob.matrix_world = operation.matrices[i]
