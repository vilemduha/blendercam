"""Fabex 'ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

import bpy
from bpy.types import Operator


class CamChainAdd(Operator):
    """Add New CAM Chain"""

    bl_idname = "scene.cam_chain_add"
    bl_label = "Add New CAM Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM chain creation in the given context.

        This function adds a new CAM chain to the current scene in Blender.
        It updates the active CAM chain index and assigns a name and filename
        to the newly created chain. The function is intended to be called within
        a Blender operator context.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation's completion status,
                specifically returning {'FINISHED'} upon successful execution.
        """

        # main(context)
        s = bpy.context.scene
        s.cam_chains.add()
        chain = s.cam_chains[-1]
        s.cam_active_chain = len(s.cam_chains) - 1
        chain.name = "Chain_" + str(s.cam_active_chain + 1)
        chain.filename = chain.name
        chain.index = s.cam_active_chain

        return {"FINISHED"}


class CamChainRemove(Operator):
    """Remove CAM Chain"""

    bl_idname = "scene.cam_chain_remove"
    bl_label = "Remove CAM Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM chain removal process.

        This function removes the currently active CAM chain from the scene
        and decrements the active CAM chain index if it is greater than zero.
        It modifies the Blender context to reflect these changes.

        Args:
            context: The context in which the function is executed.

        Returns:
            dict: A dictionary indicating the status of the operation,
                specifically {'FINISHED'} upon successful execution.
        """

        bpy.context.scene.cam_chains.remove(bpy.context.scene.cam_active_chain)
        if bpy.context.scene.cam_active_chain > 0:
            bpy.context.scene.cam_active_chain -= 1

        return {"FINISHED"}


class CamChainOperationAdd(Operator):
    """Add Operation to Chain"""

    bl_idname = "scene.cam_chain_operation_add"
    bl_label = "Add Operation to Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute an operation in the active CAM chain.

        This function retrieves the active CAM chain from the current scene
        and adds a new operation to it. It increments the active operation index
        and assigns the name of the currently selected CAM operation to the
        newly added operation. This is typically used in the context of managing
        CAM operations in a 3D environment.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the execution status, typically {'FINISHED'}.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        s = bpy.context.scene
        chain.operations.add()
        chain.active_operation += 1
        chain.operations[-1].name = s.cam_operations[s.cam_active_operation].name
        return {"FINISHED"}


class CamChainOperationUp(Operator):
    """Add Operation to Chain"""

    bl_idname = "scene.cam_chain_operation_up"
    bl_label = "Add Operation to Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the operation to move the active CAM operation in the chain.

        This function retrieves the current scene and the active CAM chain.
        If there is an active operation (i.e., its index is greater than 0), it
        moves the operation one step up in the chain by adjusting the indices
        accordingly. After moving the operation, it updates the active operation
        index to reflect the change.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the result of the operation,
                specifically returning {'FINISHED'} upon successful execution.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        a = chain.active_operation
        if a > 0:
            chain.operations.move(a, a - 1)
            chain.active_operation -= 1
        return {"FINISHED"}


class CamChainOperationDown(Operator):
    """Add Operation to Chain"""

    bl_idname = "scene.cam_chain_operation_down"
    bl_label = "Add Operation to Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the operation to move the active CAM operation in the chain.

        This function retrieves the current scene and the active CAM chain.
        It checks if the active operation can be moved down in the list of
        operations. If so, it moves the active operation one position down and
        updates the active operation index accordingly.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the result of the operation,
                specifically {'FINISHED'} when the operation completes successfully.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        a = chain.active_operation
        if a < len(chain.operations) - 1:
            chain.operations.move(a, a + 1)
            chain.active_operation += 1
        return {"FINISHED"}


class CamChainOperationRemove(Operator):
    """Remove Operation from Chain"""

    bl_idname = "scene.cam_chain_operation_remove"
    bl_label = "Remove Operation from Chain"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the operation to remove the active operation from the CAM
        chain.

        This method accesses the current scene and retrieves the active CAM
        chain. It then removes the currently active operation from that chain
        and adjusts the index of the active operation accordingly. If the active
        operation index becomes negative, it resets it to zero to ensure it
        remains within valid bounds.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the execution status, typically
                containing {'FINISHED'} upon successful completion.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chain.operations.remove(chain.active_operation)
        chain.active_operation -= 1
        if chain.active_operation < 0:
            chain.active_operation = 0
        return {"FINISHED"}
