"""BlenderCAM 'slice.py' © 2021 Alain Pelletier

Very simple slicing for 3D meshes, useful for plywood cutting.
Completely rewritten April 2021.
"""

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
)
from bpy.types import PropertyGroup

from . import (
    constants,
    utils,
)


def slicing2d(ob, height):
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
    bpy.ops.object.mode_set(mode='EDIT')  # force edit mode
    bpy.ops.mesh.select_all(action='SELECT')  # select all vertices
    # actual slicing here
    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, height), plane_no=(0.0, 0.0, 1.0), use_fill=True, clear_inner=True,
                        clear_outer=True)
    # slicing done
    bpy.ops.object.mode_set(mode='OBJECT')  # force object mode
    # bring all the slices to 0 level and reset location transform
    ob.location[2] = -1 * height
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.convert(target='CURVE')  # convert it to curve
    if bpy.context.active_object.type != 'CURVE':  # conversion failed because mesh was empty so delete mesh
        bpy.ops.object.delete(use_global=False, confirm=False)
        return False
    bpy.ops.object.select_all(action='DESELECT')  # deselect everything
    return True


def slicing3d(ob, start, end):
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
    bpy.ops.object.mode_set(mode='EDIT')  # force edit mode
    bpy.ops.mesh.select_all(action='SELECT')  # select all vertices
    # actual slicing here
    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, start), plane_no=(0.0, 0.0, 1.0), use_fill=False, clear_inner=True,
                        clear_outer=False)
    bpy.ops.mesh.select_all(action='SELECT')  # select all vertices which
    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, end), plane_no=(0.0, 0.0, 1.0), use_fill=True, clear_inner=False,
                        clear_outer=True)
    # slicing done
    bpy.ops.object.mode_set(mode='OBJECT')  # force object mode
    # bring all the slices to 0 level and reset location transform
    ob.location[2] = -1 * start
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    bpy.ops.object.select_all(action='DESELECT')  # deselect everything
    return True


def sliceObject(ob):
    """Slice a 3D object into layers based on a specified thickness.

    This function takes a 3D object and slices it into multiple layers
    according to the specified thickness. It creates a new collection for
    the slices and optionally creates text labels for each slice if the
    indexes parameter is set. The slicing can be done in either 2D or 3D
    based on the user's selection. The function also handles the positioning
    of the slices based on the object's bounding box.

    Args:
        ob (bpy.types.Object): The 3D object to be sliced.
    """
  # April 2020 Alain Pelletier
    # get variables from menu
    thickness = bpy.context.scene.cam_slice.slice_distance
    slice3d = bpy.context.scene.cam_slice.slice_3d
    indexes = bpy.context.scene.cam_slice.indexes
    above0 = bpy.context.scene.cam_slice.slice_above0
    # setup the collections
    scollection = bpy.data.collections.new("Slices")
    bpy.context.scene.collection.children.link(scollection)
    if indexes:
        tcollection = bpy.data.collections.new("Text")
        bpy.context.scene.collection.children.link(tcollection)

    bpy.ops.object.mode_set(mode='OBJECT')  # force object mode
    minx, miny, minz, maxx, maxy, maxz = utils.getBoundsWorldspace([ob])

    start_height = minz
    if above0 and minz < 0:
        start_height = 0

    # calculate amount of layers needed
    layeramt = 1 + int((maxz - start_height) // thickness)

    for layer in range(layeramt):
        height = round(layer * thickness, 6)  # height of current layer
        t = str(layer) + "-" + str(height * 1000)
        slicename = "slice_" + t  # name for the current slice
        tslicename = "t_" + t  # name for the current slice text
        height += start_height
        print(slicename)

        ob.select_set(True)  # select object to be sliced
        bpy.context.view_layer.objects.active = ob  # make object to be sliced active
        bpy.ops.object.duplicate()  # make a copy of object to be sliced
        bpy.context.view_layer.objects.active.name = slicename  # change the name of object

        # attribute active object to obslice
        obslice = bpy.context.view_layer.objects.active
        scollection.objects.link(obslice)  # link obslice to scollecton
        if slice3d:
            # slice 3d at desired height and stop at desired height
            slicesuccess = slicing3d(obslice, height, height + thickness)
        else:
            # slice object at desired height
            slicesuccess = slicing2d(obslice, height)

        if indexes and slicesuccess:
            # text objects
            bpy.ops.object.text_add()  # new text object
            textob = bpy.context.active_object
            textob.data.size = 0.006  # change size of object
            textob.data.body = t  # text content
            textob.location = (0, 0, 0)  # text location
            textob.name = tslicename  # change the name of object
            bpy.ops.object.select_all(action='DESELECT')  # deselect everything
            tcollection.objects.link(textob)  # add to text collection
            textob.parent = obslice  # make textob child of obslice

    # select all slices
    for obj in bpy.data.collections['Slices'].all_objects:
        obj.select_set(True)


class SliceObjectsSettings(PropertyGroup):
    """Stores All Data for Machines"""

    slice_distance: FloatProperty(
        name="Slicing Distance",
        description="Slices distance in z, should be most often "
        "thickness of plywood sheet.",
        min=0.001,
        max=10,
        default=0.005,
        precision=constants.PRECISION,
        unit="LENGTH",
    )
    slice_above0: BoolProperty(
        name="Slice Above 0",
        description="only slice model above 0",
        default=False,
    )
    slice_3d: BoolProperty(
        name="3D Slice",
        description="For 3D carving",
        default=False,
    )
    indexes: BoolProperty(
        name="Add Indexes",
        description="Adds index text of layer + index",
        default=True,
    )
