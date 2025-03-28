"""Fabex 'slice_op.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    FloatProperty,
)
from bpy.types import Operator

from ..constants import PRECISION
from ..slice import slicing_2d, slicing_3d
from ..utilities.bounds_utils import get_bounds_worldspace


class CamSliceObjects(Operator):
    """Slice a Mesh Object Horizontally"""

    # warning, this is a separate and neglected feature, it's a mess - by now it just slices up the object.
    bl_idname = "object.cam_slice_objects"
    bl_label = "Slice Object - Useful for Lasercut Puzzles etc"
    bl_options = {"REGISTER", "UNDO"}

    slice_distance: FloatProperty(
        name="Slicing Distance",
        description="Slices distance in z, should be most often " "thickness of plywood sheet.",
        min=0.001,
        max=10,
        default=0.005,
        precision=PRECISION,
        unit="LENGTH",
    )
    slice_above_0: BoolProperty(
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

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
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

        ob = bpy.context.active_object

        # April 2020 Alain Pelletier
        # get variables from menu
        thickness = self.slice_distance
        slice3d = self.slice_3d
        indexes = self.indexes
        above0 = self.slice_above_0
        # setup the collections
        scollection = bpy.data.collections.new("Slices")
        bpy.context.scene.collection.children.link(scollection)
        if indexes:
            tcollection = bpy.data.collections.new("Text")
            bpy.context.scene.collection.children.link(tcollection)

        bpy.ops.object.mode_set(mode="OBJECT")  # force object mode
        minx, miny, minz, maxx, maxy, maxz = get_bounds_worldspace([ob])

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
                slicesuccess = slicing_3d(obslice, height, height + thickness)
            else:
                # slice object at desired height
                slicesuccess = slicing_2d(obslice, height)

            if indexes and slicesuccess:
                # text objects
                bpy.ops.object.text_add()  # new text object
                textob = bpy.context.active_object
                textob.data.size = 0.006  # change size of object
                textob.data.body = t  # text content
                textob.location = (0, 0, 0)  # text location
                textob.name = tslicename  # change the name of object
                bpy.ops.object.select_all(action="DESELECT")  # deselect everything
                tcollection.objects.link(textob)  # add to text collection
                textob.parent = obslice  # make textob child of obslice

        # select all slices
        for obj in bpy.data.collections["Slices"].all_objects:
            obj.select_set(True)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "slice_distance")
        col.prop(self, "slice_above_0")
        col.prop(self, "slice_3d")
        col.prop(self, "indexes")
