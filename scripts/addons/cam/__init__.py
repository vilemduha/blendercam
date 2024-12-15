"""Fabex '__init__.py' © 2012 Vilem Novak

Import Modules, Register and Unregister Classes
"""

# Python Standard Library
import subprocess
import sys

# pip Wheels
import shapely
import opencamlib

# Blender Library
import bpy
from bpy.props import (
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy_extras.object_utils import object_data_add

# Relative Imports - from 'cam' module
from .bas_relief import DoBasRelief, ProblemAreas
from .engine import (
    FABEX_ENGINE,
    get_panels,
)
from .operators.curve_cam_create import (
    CamCurveDrawer,
    CamCurveFlatCone,
    CamCurveGear,
    CamCurveHatch,
    CamCurveInterlock,
    CamCurveMortise,
    CamCurvePlate,
    CamCurvePuzzle,
)
from .operators.curve_cam_equation import (
    CamCustomCurve,
    CamHypotrochoidCurve,
    CamLissajousCurve,
    CamSineCurve,
)
from .operators.curve_cam_tools import (
    CamCurveBoolean,
    CamCurveConvexHull,
    CamCurveIntarsion,
    CamCurveOvercuts,
    CamCurveOvercutsB,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,
    CamOffsetSilhouete,
    CamObjectSilhouette,
)
from .operators.position_object import CAM_MATERIAL_PositionObject
from .operators.ops import (
    CalculatePath,
    # bridges related
    CamBridgesAdd,
    CamChainAdd,
    CamChainRemove,
    CamChainOperationAdd,
    CamChainOperationRemove,
    CamChainOperationUp,
    CamChainOperationDown,
    CamOperationAdd,
    CamOperationCopy,
    CamOperationRemove,
    CamOperationMove,
    # 5 axis ops
    CamOrientationAdd,
    # shape packing
    CamPackObjects,
    CamSliceObjects,
    CAMSimulate,
    CAMSimulateChain,
    KillPathsBackground,
    PathsAll,
    PathsBackground,
    PathsChain,
    PathExport,
    PathExportChain,
    timer_update,
)

from .properties.operation_props import CAM_OPERATION_Properties
from properties.chain_props import (
    CAM_CHAIN_Properties,
    CAM_OP_REFERENCE_Properties,
)
from .properties.info_props import CAM_INFO_Properties
from .properties.machine_props import CAM_MACHINE_Properties
from .properties.material_props import CAM_MATERIAL_Properties
from .properties.movement_props import CAM_MOVEMENT_Properties
from .properties.optimisation_props import CAM_OPTIMISATION_Properties
from .preferences import CamAddonPreferences
from .preset_managers import (
    AddPresetCamCutter,
    AddPresetCamMachine,
    AddPresetCamOperation,
    CAM_CUTTER_MT_presets,
    CAM_MACHINE_MT_presets,
    CAM_OPERATION_MT_presets,
)

from .ui import register as ui_register, unregister as ui_unregister

# Import Interface Properties to create a PointerProperty in register()
from .ui.panels.interface import CAM_INTERFACE_Properties
from .utils import (
    check_operations_on_load,
    update_operation,
)


classes = [
    # .basrelief
    DoBasRelief,
    ProblemAreas,
    # .chain
    CAM_OP_REFERENCE_Properties,
    CAM_CHAIN_Properties,
    CAM_INFO_Properties,
    CAM_MATERIAL_Properties,
    CAM_MOVEMENT_Properties,
    CAM_OPTIMISATION_Properties,
    # .curve_cam_create
    CamCurveDrawer,
    CamCurveFlatCone,
    CamCurveGear,
    CamCurveHatch,
    CamCurveInterlock,
    CamCurveMortise,
    CamCurvePlate,
    CamCurvePuzzle,
    # .curve_cam_equation
    CamCustomCurve,
    CamHypotrochoidCurve,
    CamLissajousCurve,
    CamSineCurve,
    # .curve_cam_tools
    CamCurveBoolean,
    CamCurveConvexHull,
    CamCurveIntarsion,
    CamCurveOvercuts,
    CamCurveOvercutsB,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,
    CamOffsetSilhouete,
    CamObjectSilhouette,
    # .engine
    FABEX_ENGINE,
    # .machine_settings
    CAM_MACHINE_Properties,
    # .ops
    CalculatePath,
    CAM_MATERIAL_PositionObject,
    # bridges related
    CamBridgesAdd,
    CamChainAdd,
    CamChainRemove,
    CamChainOperationAdd,
    CamChainOperationRemove,
    CamChainOperationUp,
    CamChainOperationDown,
    CamOperationAdd,
    CamOperationCopy,
    CamOperationRemove,
    CamOperationMove,
    # 5 axis ops
    CamOrientationAdd,
    # shape packing
    CamPackObjects,
    CamSliceObjects,
    CAMSimulate,
    CAMSimulateChain,
    KillPathsBackground,
    PathsAll,
    PathsBackground,
    PathsChain,
    PathExport,
    PathExportChain,
    # .preferences
    CamAddonPreferences,
    # .preset_managers
    CAM_CUTTER_MT_presets,
    CAM_OPERATION_MT_presets,
    CAM_MACHINE_MT_presets,
    AddPresetCamCutter,
    AddPresetCamOperation,
    AddPresetCamMachine,
]


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    ui_register()

    # .cam_operation - last to allow dependencies to register before it
    bpy.utils.register_class(CAM_OPERATION_Properties)

    bpy.app.handlers.frame_change_pre.append(timer_update)
    bpy.app.handlers.load_post.append(check_operations_on_load)
    # bpy.types.INFO_HT_header.append(header_info)

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
    scene.cam_operations = CollectionProperty(
        type=CAM_OPERATION_Properties,
    )
    scene.cam_text = StringProperty()
    scene.interface = PointerProperty(
        type=CAM_INTERFACE_Properties,
    )

    for panel in get_panels():
        panel.COMPAT_ENGINES.add("FABEX_RENDER")

    wm = bpy.context.window_manager
    addon_kc = wm.keyconfigs.addon

    km = addon_kc.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new(
        "wm.call_menu_pie",
        "C",
        "PRESS",
        alt=True,
    )
    kmi.properties.name = "VIEW3D_MT_PIE_CAM"
    kmi.active = True


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)

    ui_unregister()

    bpy.utils.unregister_class(CAM_OPERATION_Properties)

    scene = bpy.types.Scene

    # cam chains are defined hardly now.
    del scene.cam_chains
    del scene.cam_active_chain
    del scene.cam_operations
    del scene.cam_active_operation
    del scene.cam_machine
    del scene.gcode_output_type
    del scene.cam_text

    for panel in get_panels():
        if "FABEX_RENDER" in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove("FABEX_RENDER")

    wm = bpy.context.window_manager
    active_kc = wm.keyconfigs.active

    for key in active_kc.keymaps["Object Mode"].keymap_items:
        if key.idname == "wm.call_menu" and key.properties.name == "VIEW3D_MT_PIE_CAM":
            active_kc.keymaps["Object Mode"].keymap_items.remove(key)
