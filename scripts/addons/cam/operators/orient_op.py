"""Fabex 'ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

import bpy
from bpy.types import Operator

from ..utilities.simple_utils import add_to_group


class CamOrientationAdd(Operator):
    """Add Orientation to CAM Operation, for Multiaxis Operations"""

    bl_idname = "scene.cam_orientation_add"
    bl_label = "Add Orientation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM orientation operation in Blender.

        This function retrieves the active CAM operation from the current
        scene, creates an empty object to represent the CAM orientation, and
        adds it to a specified group. The empty object is named based on the
        operation's name and the current count of objects in the group. The size
        of the empty object is set to a predefined value for visibility.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation's completion status,
                typically {'FINISHED'}.
        """

        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        gname = o.name + "_orientations"
        bpy.ops.object.empty_add(type="ARROWS")

        oriob = bpy.context.active_object
        oriob.empty_draw_size = 0.02  # 2 cm

        add_to_group(oriob, gname)
        oriob.name = "ori_" + o.name + "." + str(len(bpy.data.collections[gname].objects)).zfill(3)

        return {"FINISHED"}
