"""Fabex 'operation_ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

import bpy
from bpy.props import EnumProperty
from bpy.types import (
    Operator,
    PropertyGroup,
)
from mathutils import Euler, Vector

from ..bridges import add_auto_bridges
from ..constants import was_hidden_dict

from ..utilities.simple_utils import add_to_group
from ..utilities.machine_utils import add_machine_area_object
from ..utilities.bounds_utils import get_bounds_worldspace
from ..utilities.addon_utils import fix_units


class CamOperationAdd(Operator):
    """Add New CAM Operation"""

    bl_idname = "scene.cam_operation_add"
    bl_label = "Add New CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM operation based on the active object in the scene.

        This method retrieves the active object from the Blender context and
        performs operations related to CAM settings. It checks if an object
        is selected and retrieves its bounding box dimensions. If no object is
        found, it reports an error and cancels the operation. If an object is
        present, it adds a new CAM operation to the scene, sets its
        properties, and ensures that a machine area object is present.

        Args:
            context: The context in which the operation is executed.
        """
        # Open Sidebar to show Operation Settings
        if context.scene.interface.operation_location == "SIDEBAR":
            view3d = [a for a in context.screen.areas if a.type == "VIEW_3D"][0]
            view3d.spaces[0].show_region_ui = True

        s = bpy.context.scene
        fix_units()

        ob = bpy.context.active_object
        if ob is None:
            self.report({"ERROR_INVALID_INPUT"}, "Please Add an Object to Base the Operation on.")
            return {"CANCELLED"}

        minx, miny, minz, maxx, maxy, maxz = get_bounds_worldspace([ob])
        s.cam_operations.add()
        o = s.cam_operations[-1]
        o.object_name = ob.name
        o.min_z = minz

        s.cam_active_operation = len(s.cam_operations) - 1

        o.name = f"Op_{ob.name}_{s.cam_active_operation + 1}"
        o.filename = o.name

        if s.objects.get("CAM_machine") is None:
            add_machine_area_object()

        return {"FINISHED"}


class CamOperationCopy(Operator):
    """Copy CAM Operation"""

    bl_idname = "scene.cam_operation_copy"
    bl_label = "Copy Active CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM operation in the given context.

        This method handles the execution of CAM operations within the
        Blender scene. It first checks if there are any CAM operations
        available. If not, it returns a cancellation status. If there are
        operations, it copies the active operation, increments the active
        operation index, and updates the name and filename of the new operation.
        The function also ensures that the new operation's name is unique by
        appending a copy suffix or incrementing a numeric suffix.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation,
                either {'CANCELLED'} if no operations are available or
                {'FINISHED'} if the operation was successfully executed.
        """

        scene = context.scene

        fix_units()

        if len(scene.cam_operations) == 0:
            return {"CANCELLED"}

        copyop = scene.cam_operations[scene.cam_active_operation]
        scene.cam_operations.add()
        scene.cam_active_operation += 1
        l = len(scene.cam_operations) - 1
        scene.cam_operations.move(l, scene.cam_active_operation)
        o = scene.cam_operations[scene.cam_active_operation]

        for k in copyop.keys():
            value = copyop[k]
            if isinstance(value, bpy.types.PropertyGroup):
                for subkey in value.keys():
                    o[k][subkey] = value[subkey]
            else:
                o[k] = value

        o.computing = False

        # ###get digits in the end

        isdigit = True
        numdigits = 0
        num = 0
        if o.name[-1].isdigit():
            numdigits = 1
            while isdigit:
                numdigits += 1
                isdigit = o.name[-numdigits].isdigit()
            numdigits -= 1
            o.name = o.name[:-numdigits] + str(int(o.name[-numdigits:]) + 1).zfill(numdigits)
            o.filename = o.name
        else:
            o.name = o.name + "_copy"
            o.filename = o.filename + "_copy"

        return {"FINISHED"}


class CamOperationRemove(Operator):
    """Remove CAM Operation"""

    bl_idname = "scene.cam_operation_remove"
    bl_label = "Remove CAM Operation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM operation in the given context.

        This function performs the active CAM operation by deleting the
        associated object from the scene. It checks if there are any CAM
        operations available and handles the deletion of the active operation's
        object. If the active operation is removed, it updates the active
        operation index accordingly. Additionally, it manages a dictionary that
        tracks hidden objects.

        Args:
            context (bpy.context): The Blender context containing the scene and operations.

        Returns:
            dict: A dictionary indicating the result of the operation, either
                {'CANCELLED'} if no operations are available or {'FINISHED'} if the
                operation was successfully executed.
        """

        scene = context.scene
        try:
            if len(scene.cam_operations) == 0:
                # # Close Sidebar
                # view3d = [a for a in context.screen.areas if a.type == "VIEW_3D"][0]
                # if view3d.regions[5].active_panel_category == "CNC":
                #     view3d.spaces[0].show_region_ui = False
                return {"CANCELLED"}
            active_op = scene.cam_operations[scene.cam_active_operation]
            active_op_object = bpy.data.objects[active_op.name]
            scene.objects.active = active_op_object
            bpy.ops.object.delete(True)
        except:
            pass

        ao = scene.cam_operations[scene.cam_active_operation]
        print(was_hidden_dict)
        if ao.name in was_hidden_dict:
            del was_hidden_dict[ao.name]

        scene.cam_operations.remove(scene.cam_active_operation)
        if scene.cam_active_operation > 0:
            scene.cam_active_operation -= 1

        return {"FINISHED"}


# move cam operation in the list up or down
class CamOperationMove(Operator):
    """Move CAM Operation"""

    bl_idname = "scene.cam_operation_move"
    bl_label = "Move CAM Operation in List"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        name="Direction",
        items=(("UP", "Up", ""), ("DOWN", "Down", "")),
        description="Direction",
        default="DOWN",
    )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute a CAM operation based on the specified direction.

        This method modifies the active CAM operation in the Blender context
        based on the direction specified. If the direction is 'UP', it moves the
        active operation up in the list, provided it is not already at the top.
        Conversely, if the direction is not 'UP', it moves the active operation
        down in the list, as long as it is not at the bottom. The method updates
        the active operation index accordingly.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation has finished, with
            the key 'FINISHED'.
        """

        # main(context)
        a = bpy.context.scene.cam_active_operation
        cops = bpy.context.scene.cam_operations
        if self.direction == "UP":
            if a > 0:
                cops.move(a, a - 1)
                bpy.context.scene.cam_active_operation -= 1

        else:
            if a < len(cops) - 1:
                cops.move(a, a + 1)
                bpy.context.scene.cam_active_operation += 1

        return {"FINISHED"}
