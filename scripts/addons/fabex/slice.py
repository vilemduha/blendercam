"""Fabex 'slice.py' © 2021 Alain Pelletier

Very simple slicing for 3D meshes, useful for plywood cutting.
Completely rewritten April 2021.
"""

import bpy


def slicing_2d(ob, height):
    """Slice a 3D object at a specified height and convert it to a curve.

    This function applies transformations to the given object, switches to
    edit mode, selects all vertices, and performs a bisect operation to
    slice the object at the specified height. After slicing, it resets the
    object's location and applies transformations again before converting
    the object to a curve. If the conversion fails (for instance, if the
    mesh was empty), the function deletes the mesh and returns False.
    Otherwise, it returns True.

    Args:
        ob (bpy.types.Object): The Blender object to be sliced and converted.
        height (float): The height at which to slice the object.

    Returns:
        bool: True if the conversion to curve was successful, False otherwise.
    """
    # April 2020 Alain Pelletier
    # let's slice things
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.mode_set(mode="EDIT")  # force edit mode
    bpy.ops.mesh.select_all(action="SELECT")  # select all vertices
    # actual slicing here
    bpy.ops.mesh.bisect(
        plane_co=(0.0, 0.0, height),
        plane_no=(0.0, 0.0, 1.0),
        use_fill=True,
        clear_inner=True,
        clear_outer=True,
    )
    # slicing done
    bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
    # bring all the slices to 0 level and reset location transform
    ob.location[2] = -1 * height
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.convert(target="CURVE")  # convert it to curve
    if (
        bpy.context.active_object.type != "CURVE"
    ):  # conversion failed because mesh was empty so delete mesh
        bpy.ops.object.delete(use_global=False, confirm=False)
        return False
    bpy.ops.object.select_all(action="DESELECT")  # deselect everything
    return True


def slicing_3d(ob, start, end):
    """Slice a 3D object along specified planes.

    This function applies transformations to a given object and slices it in
    the Z-axis between two specified values, `start` and `end`. It first
    ensures that the object is in edit mode and selects all vertices before
    performing the slicing operations using the `bisect` method. After
    slicing, it resets the object's location and applies the transformations
    to maintain the changes.

    Args:
        ob (Object): The 3D object to be sliced.
        start (float): The starting Z-coordinate for the slice.
        end (float): The ending Z-coordinate for the slice.

    Returns:
        bool: True if the slicing operation was successful.
    """
    # April 2020 Alain Pelletier
    # let's slice things
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.mode_set(mode="EDIT")  # force edit mode
    bpy.ops.mesh.select_all(action="SELECT")  # select all vertices
    # actual slicing here
    bpy.ops.mesh.bisect(
        plane_co=(0.0, 0.0, start),
        plane_no=(0.0, 0.0, 1.0),
        use_fill=False,
        clear_inner=True,
        clear_outer=False,
    )
    bpy.ops.mesh.select_all(action="SELECT")  # select all vertices which
    bpy.ops.mesh.bisect(
        plane_co=(0.0, 0.0, end),
        plane_no=(0.0, 0.0, 1.0),
        use_fill=True,
        clear_inner=False,
        clear_outer=True,
    )
    # slicing done
    bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
    # bring all the slices to 0 level and reset location transform
    ob.location[2] = -1 * start
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    bpy.ops.object.select_all(action="DESELECT")  # deselect everything
    return True
