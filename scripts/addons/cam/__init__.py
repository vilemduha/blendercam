"""CNC CAM '__init__.py' © 2012 Vilem Novak

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
from . import basrelief
from .autoupdate import (
    UpdateChecker,
    Updater,
    UpdateSourceOperator,
)
from .cam_operation import camOperation
from .chain import (
    camChain,
    opReference,
)
from .curvecamcreate import (
    CamCurveDrawer,
    CamCurveFlatCone,
    CamCurveGear,
    CamCurveHatch,
    CamCurveInterlock,
    CamCurveMortise,
    CamCurvePlate,
    CamCurvePuzzle,
)
from .curvecamequation import (
    CamCustomCurve,
    CamHypotrochoidCurve,
    CamLissajousCurve,
    CamSineCurve,
)
from .curvecamtools import (
    CamCurveBoolean,
    CamCurveConvexHull,
    CamCurveIntarsion,
    CamCurveOvercuts,
    CamCurveOvercutsB,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,
    CamOffsetSilhouete,
    CamObjectSilhouete,
)
from .engine import (
    CNCCAM_ENGINE,
    get_panels,
)
from .machine_settings import machineSettings
from .ops import (
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
from .pack import PackObjectsSettings
from .preferences import CamAddonPreferences
from .preset_managers import (
    AddPresetCamCutter,
    AddPresetCamMachine,
    AddPresetCamOperation,
    CAM_CUTTER_MT_presets,
    CAM_MACHINE_MT_presets,
    CAM_OPERATION_MT_presets,
)
from .slice import SliceObjectsSettings
from .ui import register as ui_register, unregister as ui_unregister
from .utils import (
    check_operations_on_load,
    updateOperation,
)


classes = [
    # CamBackgroundMonitor
    # .autoupdate
    UpdateSourceOperator,
    Updater,
    UpdateChecker,
    # .chain
    opReference,
    camChain,
    # .curvecamcreate
    CamCurveDrawer,
    CamCurveFlatCone,
    CamCurveGear,
    CamCurveHatch,
    CamCurveInterlock,
    CamCurveMortise,
    CamCurvePlate,
    CamCurvePuzzle,
    # .curvecamequation
    CamCustomCurve,
    CamHypotrochoidCurve,
    CamLissajousCurve,
    CamSineCurve,
    # .curvecamtools
    CamCurveBoolean,
    CamCurveConvexHull,
    CamCurveIntarsion,
    CamCurveOvercuts,
    CamCurveOvercutsB,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,
    CamOffsetSilhouete,
    CamObjectSilhouete,
    # .engine
    CNCCAM_ENGINE,
    # .machine_settings
    machineSettings,
    # .ops
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
    # .pack
    PackObjectsSettings,
    # .preferences
    CamAddonPreferences,
    # .preset_managers
    CAM_CUTTER_MT_presets,
    CAM_OPERATION_MT_presets,
    CAM_MACHINE_MT_presets,
    AddPresetCamCutter,
    AddPresetCamOperation,
    AddPresetCamMachine,
    # .slice
    SliceObjectsSettings,
    # .cam_operation - last to allow dependencies to register before it
    camOperation,
]


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    ui_register()
    basrelief.register()

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
        update=updateOperation,
    )
    scene.cam_chains = CollectionProperty(
        type=camChain,
    )
    scene.cam_import_gcode = PointerProperty(
        type=import_settings,
    )
    scene.cam_machine = PointerProperty(
        type=machineSettings,
    )
    scene.cam_operations = CollectionProperty(
        type=camOperation,
    )
    scene.cam_pack = PointerProperty(
        type=PackObjectsSettings,
    )
    scene.cam_slice = PointerProperty(
        type=SliceObjectsSettings,
    )
    scene.cam_text = StringProperty()
    scene.interface = PointerProperty(
        type=CAM_INTERFACE_Properties,
    )

    for panel in get_panels():
        panel.COMPAT_ENGINES.add("CNCCAM_RENDER")

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
    basrelief.unregister()

    scene = bpy.types.Scene

    # cam chains are defined hardly now.
    del scene.cam_chains
    del scene.cam_active_chain
    del scene.cam_operations
    del scene.cam_active_operation
    del scene.cam_machine
    del scene.cam_import_gcode
    del scene.cam_text
    del scene.cam_pack
    del scene.cam_slice

    for panel in get_panels():
        if "CNCCAM_RENDER" in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove("CNCCAM_RENDER")

    wm = bpy.context.window_manager
    active_kc = wm.keyconfigs.active

    for key in active_kc.keymaps["Object Mode"].keymap_items:
        if key.idname == "wm.call_menu" and key.properties.name == "VIEW3D_MT_PIE_CAM":
            active_kc.keymaps["Object Mode"].keymap_items.remove(key)
