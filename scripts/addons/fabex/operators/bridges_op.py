"""Fabex 'bridges_op.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

import bpy
from bpy.types import Operator

from ..bridges import add_auto_bridges


class CamBridgesAdd(Operator):
    """Add Bridge Objects to Curve"""

    bl_idname = "scene.cam_bridges_add"
    bl_label = "Add Bridges / Tabs"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM operation in the given context.

        This function retrieves the active CAM operation from the current
        scene and adds automatic bridges to it. It is typically called within
        the context of a Blender operator to perform specific actions related to
        CAM operations.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the result of the operation, typically
            containing the key 'FINISHED' to signify successful completion.
        """

        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        add_auto_bridges(o)
        return {"FINISHED"}
