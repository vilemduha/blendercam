"""Fabex 'properties.__init__.py' © 2012 Vilem Novak

Import Properties, Register and Unregister Classes
"""

import bpy
from bpy.props import (
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

# All properties are imported and registered here EXCEPT
# CAM_OPERATION_Properties, which is imported and registered
# in the main ('cam') __init__ file, to allow these and other dependencies
# to register first
from .chain_props import CAM_CHAIN_Properties, CAM_OP_REFERENCE_Properties
from .info_props import CAM_INFO_Properties
from .interface_props import CAM_INTERFACE_Properties, draw_interface
from .machine_props import CAM_MACHINE_Properties
from .material_props import CAM_MATERIAL_Properties
from .movement_props import CAM_MOVEMENT_Properties
from .optimisation_props import CAM_OPTIMISATION_Properties

from ..utilities.operation_utils import update_operation

classes = [
    CAM_OP_REFERENCE_Properties,
    CAM_CHAIN_Properties,
    CAM_INFO_Properties,
    CAM_INTERFACE_Properties,
    CAM_MACHINE_Properties,
    CAM_MATERIAL_Properties,
    CAM_MOVEMENT_Properties,
    CAM_OPTIMISATION_Properties,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.RENDER_PT_context.append(draw_interface)

    scene = bpy.types.Scene

    scene.cam_active_chain = IntProperty(
        name="CAM Active Chain",
        description="The selected chain",
    )
    scene.cam_active_operation = IntProperty(
        name="CAM Active Operation",
        description="The selected operation",
        update=update_operation,
    )
    scene.cam_chains = CollectionProperty(
        type=CAM_CHAIN_Properties,
    )
    scene.gcode_output_type = StringProperty(
        name="Gcode Output Type",
        default="",
    )
    scene.cam_machine = PointerProperty(
        type=CAM_MACHINE_Properties,
    )
    scene.cam_text = StringProperty()
    scene.interface = PointerProperty(
        type=CAM_INTERFACE_Properties,
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.RENDER_PT_context.remove(draw_interface)

    scene = bpy.types.Scene

    del scene.cam_chains
    del scene.cam_active_chain
    del scene.cam_active_operation
    del scene.cam_machine
    del scene.gcode_output_type
    del scene.cam_text
