"""Fabex 'position_object.py'

'CAM Material' properties and panel in Properties > Render
"""

import bpy

from bpy.types import Operator
from ..utilities.bounds_utils import position_object


# Position object for CAM operation. Tests object bounds and places them so the object
# is aligned to be positive from x and y and negative from z."""
class CAM_MATERIAL_PositionObject(Operator):
    bl_idname = "object.material_cam_position"
    bl_label = "Position Object for CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            position_object(operation)
        else:
            print("No Object Assigned")
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", context.scene, "cam_operations")
