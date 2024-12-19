"""Fabex 'properties.__init__.py' © 2012 Vilem Novak

Import Properties, Register and Unregister Classes
"""

import bpy

# All properties are imported and registered here EXCEPT
# CAM_OPERATION_Properties, which is imported and registered
# in the main ('cam') __init__ file, to allow these and other dependencies
# to register first
from .chain_props import CAM_CHAIN_Properties, CAM_OP_REFERENCE_Properties
from .info_props import CAM_INFO_Properties
from .machine_props import CAM_MACHINE_Properties
from .material_props import CAM_MATERIAL_Properties
from .movement_props import CAM_MOVEMENT_Properties
from .optimisation_props import CAM_OPTIMISATION_Properties

classes = [
    CAM_OP_REFERENCE_Properties,
    CAM_CHAIN_Properties,
    CAM_INFO_Properties,
    CAM_MACHINE_Properties,
    CAM_MATERIAL_Properties,
    CAM_MOVEMENT_Properties,
    CAM_OPTIMISATION_Properties,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
