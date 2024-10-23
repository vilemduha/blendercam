"""Fabex 'ui.__init__.py' © 2012 Vilem Novak

Import UI, Register and Unregister Classes
"""

import bpy

from .panels.area import CAM_AREA_Panel
from .panels.chains import (
    CAM_CHAINS_Panel,
    CAM_UL_chains,
    CAM_UL_operations,
)
from .panels.cutter import CAM_CUTTER_Panel
from .panels.feedrate import CAM_FEEDRATE_Panel
from .panels.gcode import CAM_GCODE_Panel
from .panels.info import (
    CAM_INFO_Panel,
    CAM_INFO_Properties,
)
from .panels.interface import (
    CAM_INTERFACE_Panel,
    CAM_INTERFACE_Properties,
)
from .panels.machine import CAM_MACHINE_Panel
from .panels.material import (
    CAM_MATERIAL_Panel,
    CAM_MATERIAL_PositionObject,
    CAM_MATERIAL_Properties,
)
from .panels.movement import (
    CAM_MOVEMENT_Panel,
    CAM_MOVEMENT_Properties,
)
from .panels.op_properties import CAM_OPERATION_PROPERTIES_Panel
from .panels.operations import CAM_OPERATIONS_Panel
from .panels.optimisation import (
    CAM_OPTIMISATION_Panel,
    CAM_OPTIMISATION_Properties,
)
from .panels.pack import CAM_PACK_Panel
from .panels.slice import CAM_SLICE_Panel
from .pie_menu.pie_cam import VIEW3D_MT_PIE_CAM
from .pie_menu.pie_chains import VIEW3D_MT_PIE_Chains
from .pie_menu.pie_curvecreators import VIEW3D_MT_PIE_CurveCreators
from .pie_menu.pie_curvetools import VIEW3D_MT_PIE_CurveTools
from .pie_menu.pie_info import VIEW3D_MT_PIE_Info
from .pie_menu.pie_machine import VIEW3D_MT_PIE_Machine
from .pie_menu.pie_material import VIEW3D_MT_PIE_Material
from .pie_menu.pie_pack_slice_relief import VIEW3D_MT_PIE_PackSliceRelief
from .pie_menu.active_op.pie_area import VIEW3D_MT_PIE_Area
from .pie_menu.active_op.pie_cutter import VIEW3D_MT_PIE_Cutter
from .pie_menu.active_op.pie_feedrate import VIEW3D_MT_PIE_Feedrate
from .pie_menu.active_op.pie_gcode import VIEW3D_MT_PIE_Gcode
from .pie_menu.active_op.pie_movement import VIEW3D_MT_PIE_Movement
from .pie_menu.active_op.pie_operation import VIEW3D_MT_PIE_Operation
from .pie_menu.active_op.pie_optimisation import VIEW3D_MT_PIE_Optimisation
from .pie_menu.active_op.pie_setup import VIEW3D_MT_PIE_Setup
from .legacy_ui import (
    CustomPanel,
    import_settings,
    VIEW3D_PT_tools_curvetools,
    VIEW3D_PT_tools_create,
    WM_OT_gcode_import,
)

classes = [
    # .viewport_ui and .panels - the order will affect the layout
    import_settings,
    CAM_UL_operations,
    CAM_UL_chains,
    CAM_INTERFACE_Panel,
    CAM_INTERFACE_Properties,
    CAM_CHAINS_Panel,
    CAM_OPERATIONS_Panel,
    CAM_INFO_Properties,
    CAM_INFO_Panel,
    CAM_MATERIAL_Panel,
    CAM_MATERIAL_Properties,
    CAM_MATERIAL_PositionObject,
    CAM_OPERATION_PROPERTIES_Panel,
    CAM_OPTIMISATION_Panel,
    CAM_OPTIMISATION_Properties,
    CAM_AREA_Panel,
    CAM_MOVEMENT_Panel,
    CAM_MOVEMENT_Properties,
    CAM_FEEDRATE_Panel,
    CAM_CUTTER_Panel,
    CAM_GCODE_Panel,
    CAM_MACHINE_Panel,
    CAM_PACK_Panel,
    CAM_SLICE_Panel,
    VIEW3D_PT_tools_curvetools,
    VIEW3D_PT_tools_create,
    CustomPanel,
    WM_OT_gcode_import,
    # .pie_menu and .pie_menu.active_op - placed after .ui in case inheritance is possible
    VIEW3D_MT_PIE_CAM,
    VIEW3D_MT_PIE_Machine,
    VIEW3D_MT_PIE_Material,
    VIEW3D_MT_PIE_Operation,
    VIEW3D_MT_PIE_Chains,
    VIEW3D_MT_PIE_Setup,
    VIEW3D_MT_PIE_Optimisation,
    VIEW3D_MT_PIE_Area,
    VIEW3D_MT_PIE_Movement,
    VIEW3D_MT_PIE_Feedrate,
    VIEW3D_MT_PIE_Cutter,
    VIEW3D_MT_PIE_Gcode,
    VIEW3D_MT_PIE_Info,
    VIEW3D_MT_PIE_PackSliceRelief,
    VIEW3D_MT_PIE_CurveCreators,
    VIEW3D_MT_PIE_CurveTools,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
