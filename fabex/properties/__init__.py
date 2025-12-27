"""Fabex 'properties.__init__.py' © 2012 Vilem Novak

Import Properties, Register and Unregister Classes
"""

import bpy
from bpy.props import (
    CollectionProperty,
    EnumProperty,
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
from .name_props import CAM_NAME_Properties
from .optimisation_props import CAM_OPTIMISATION_Properties
from .preset_props import (
    # Machine Presets
    avidcnc_presets,
    carbide3d_presets,
    cnc4all_presets,
    inventables_presets,
    millright_presets,
    onefinity_presets,
    ooznest_presets,
    sienci_presets,
    user_machine_presets,
    update_avidcnc,
    update_carbide3d,
    update_cnc4all,
    update_inventables,
    update_millright,
    update_onefinity,
    update_ooznest,
    update_sienci,
    update_user_machine,
    # Cutter Presets
    idcwoodcraft_presets,
    cadence_presets,
    user_cutter_presets,
    update_idcwoodcraft,
    update_cadence,
    update_user_cutter,
    # Operation Presets
    finishing_presets,
    update_finishing,
    roughing_presets,
    update_roughing,
    user_operation_presets,
    update_user_operation,
)

from ..utilities.operation_utils import update_operation


classes = [
    CAM_OP_REFERENCE_Properties,
    CAM_CHAIN_Properties,
    CAM_INFO_Properties,
    CAM_INTERFACE_Properties,
    CAM_MACHINE_Properties,
    CAM_MATERIAL_Properties,
    CAM_MOVEMENT_Properties,
    CAM_NAME_Properties,
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
    scene.cam_material = PointerProperty(
        type=CAM_MATERIAL_Properties,
    )
    scene.cam_text = StringProperty()
    scene.interface = PointerProperty(
        type=CAM_INTERFACE_Properties,
    )
    scene.cam_names = PointerProperty(
        type=CAM_NAME_Properties,
    )

    # Machine Presets
    scene.avidcnc = EnumProperty(
        items=avidcnc_presets,
        update=update_avidcnc,
    )
    scene.carbide3d = EnumProperty(
        items=carbide3d_presets,
        update=update_carbide3d,
    )
    scene.cnc4all = EnumProperty(
        items=cnc4all_presets,
        update=update_cnc4all,
    )
    scene.inventables = EnumProperty(
        items=inventables_presets,
        update=update_inventables,
    )
    scene.millright = EnumProperty(
        items=millright_presets,
        update=update_millright,
    )
    scene.onefinity = EnumProperty(
        items=onefinity_presets,
        update=update_onefinity,
    )
    scene.ooznest = EnumProperty(
        items=ooznest_presets,
        update=update_ooznest,
    )
    scene.sienci = EnumProperty(
        items=sienci_presets,
        update=update_sienci,
    )
    scene.user_machine = EnumProperty(
        items=user_machine_presets,
        update=update_user_machine,
    )

    # Cutter Presets
    scene.idcwoodcraft = EnumProperty(
        items=idcwoodcraft_presets,
        update=update_idcwoodcraft,
    )
    scene.cadence = EnumProperty(
        items=cadence_presets,
        update=update_cadence,
    )
    scene.user_cutter = EnumProperty(
        items=user_cutter_presets,
        update=update_user_cutter,
    )

    # Operation Presets
    scene.finishing = EnumProperty(
        items=finishing_presets,
        update=update_finishing,
    )
    scene.roughing = EnumProperty(
        items=roughing_presets,
        update=update_roughing,
    )
    scene.user_operation = EnumProperty(
        items=user_operation_presets,
        update=update_user_operation,
    )

    scene.operation_preset = StringProperty()


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

    del scene.avidcnc
    del scene.carbide3d
    del scene.cnc4all
    del scene.inventables
    del scene.millright
    del scene.onefinity
    del scene.ooznest
    del scene.sienci
    del scene.user_machine

    del scene.idcwoodcraft
    del scene.cadence
    del scene.user_cutter

    del scene.finishing
    del scene.roughing
    del scene.user_operation

    del scene.operation_preset
