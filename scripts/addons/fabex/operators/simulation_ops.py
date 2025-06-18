"""Fabex 'simulation_ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

import os

import shapely
from shapely import geometry as sgeometry
from shapely import affinity, prepared, speedups

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from .async_op import (
    AsyncCancelledException,
    AsyncOperatorMixin,
)

from ..simulation import do_simulation
from ..utilities.operation_utils import (
    chain_valid,
    get_chain_operations,
)


class CAMSimulate(Operator, AsyncOperatorMixin):
    """Simulate CAM Operation
    This Is Performed by: Creating an Image, Painting Z Depth of the Brush Subtractively.
    Works only for Some Operations, Can Not Be Used for 4-5 Axis."""

    bl_idname = "object.cam_simulate"
    bl_label = "CAM Simulation"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    operation: StringProperty(
        name="Operation",
        description="Specify the operation to calculate",
        default="Operation",
    )

    def __init__(self, *args, **kwargs):
        Operator.__init__(self, *args, **kwargs)
        AsyncOperatorMixin.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    async def execute_async(self, context):
        """Execute an asynchronous simulation operation based on the active CAM
        operation.

        This method retrieves the current scene and the active CAM operation.
        It constructs the operation name and checks if the corresponding object
        exists in the Blender data. If it does, it attempts to run the
        simulation asynchronously. If the simulation is cancelled, it returns a
        cancellation status. If the object does not exist, it reports an error
        and returns a finished status.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation, either
                {'CANCELLED'} or {'FINISHED'}.
        """

        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]

        operation_name = "cam_path_{}".format(operation.name)

        if operation_name in bpy.data.objects:
            try:
                await do_simulation(operation_name, [operation])
            except AsyncCancelledException as e:
                return {"CANCELLED"}
        else:
            self.report({"ERROR"}, "No Computed Path to Simulate")
            return {"FINISHED"}
        return {"FINISHED"}

    def draw(self, context):
        """Draws the user interface for selecting CAM operations.

        This method creates a layout element in the user interface that allows
        users to search and select a specific CAM operation from a list of
        available operations defined in the current scene. It utilizes the
        Blender Python API to integrate with the UI.

        Args:
            context: The context in which the drawing occurs, typically
                provided by Blender's UI system.
        """

        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CAMSimulateChain(Operator, AsyncOperatorMixin):
    """Simulate CAM Chain, Compared to Single Op Simulation Just Writes Into One Image and Thus Enables
    to See how Ops Work Together."""

    bl_idname = "object.cam_simulate_chain"
    bl_label = "CAM Simulation"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    def __init__(self, *args, **kwargs):
        Operator.__init__(self, *args, **kwargs)
        AsyncOperatorMixin.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    @classmethod
    def poll(cls, context):
        """Check the validity of the active CAM chain in the scene.

        This method retrieves the currently active CAM chain from the scene's
        CAM chains and checks its validity using the `isChainValid` function.
        It returns a boolean indicating whether the active CAM chain is
        valid.

        Args:
            context (object): The context containing the scene and its properties.

        Returns:
            bool: True if the active CAM chain is valid, False otherwise.
        """

        s = context.scene
        if len(s.cam_chains) > 0:
            chain = s.cam_chains[s.cam_active_chain]
            return chain_valid(chain, context)[0]
        else:
            return False

    operation: StringProperty(
        name="Operation",
        description="Specify the operation to calculate",
        default="Operation",
    )

    async def execute_async(self, context):
        """Execute an asynchronous simulation for a specified CAM chain.

        This method retrieves the active CAM chain from the current Blender
        scene and determines the operations associated with that chain. It
        checks if all operations are valid and can be simulated. If valid, it
        proceeds to execute the simulation asynchronously. If any operation is
        invalid, it logs a message and returns a finished status without
        performing the

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation, either
            operation completed successfully.
        """

        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chainops = get_chain_operations(chain)

        canSimulate = True
        for operation in chainops:
            if operation.name not in bpy.data.objects:
                canSimulate = True  # force true
            print("Operation Name " + str(operation.name))
        if canSimulate:
            try:
                await do_simulation(chain.name, chainops)
            except AsyncCancelledException as e:
                return {"CANCELLED"}
        else:
            print("No Computed Path to Simulate")
            return {"FINISHED"}
        return {"FINISHED"}

    def draw(self, context):
        """Draw the user interface for selecting CAM operations.

        This function creates a user interface element that allows the user to
        search and select a specific CAM operation from a list of available
        operations in the current scene. It utilizes the Blender Python API to
        create a property search layout.

        Args:
            context: The context in which the drawing occurs, typically containing
                information about the current scene and UI elements.
        """

        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")
