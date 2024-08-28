"""BlenderCAM '__init__.py' © 2012 Vilem Novak

Import Modules, bl_info, Register and Unregister Classes
"""

# Python Standard Library
import subprocess
import sys

# pip Packages
try:
    import shapely
except ModuleNotFoundError:
    # pip install required python stuff
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", " pip"])
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "shapely", "Equation", "opencamlib"]
    )

    # Numba Install temporarily disabled after crash report
    # install numba if available for this platform, ignore failure
    # subprocess.run([sys.executable, "-m", "pip", "install", "numba"])

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
    #CamObjectSilhouete,
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
from .ui import (
    CustomPanel,
    import_settings,
    VIEW3D_PT_tools_curvetools,
    VIEW3D_PT_tools_create,
    WM_OT_gcode_import,
)
from .ui_panels.area import CAM_AREA_Panel
from .ui_panels.chains import (
    CAM_CHAINS_Panel,
    CAM_UL_chains,
    CAM_UL_operations,
)
from .ui_panels.cutter import CAM_CUTTER_Panel
from .ui_panels.feedrate import CAM_FEEDRATE_Panel
from .ui_panels.gcode import CAM_GCODE_Panel
from .ui_panels.info import (
    CAM_INFO_Panel,
    CAM_INFO_Properties,
)
from .ui_panels.interface import (
    CAM_INTERFACE_Panel,
    CAM_INTERFACE_Properties,
)
from .ui_panels.machine import CAM_MACHINE_Panel
from .ui_panels.material import (
    CAM_MATERIAL_Panel,
    CAM_MATERIAL_PositionObject,
    CAM_MATERIAL_Properties,
)
from .ui_panels.movement import (
    CAM_MOVEMENT_Panel,
    CAM_MOVEMENT_Properties,
)
from .ui_panels.op_properties import CAM_OPERATION_PROPERTIES_Panel
from .ui_panels.operations import CAM_OPERATIONS_Panel
from .ui_panels.optimisation import (
    CAM_OPTIMISATION_Panel,
    CAM_OPTIMISATION_Properties,
)
from .ui_panels.pack import CAM_PACK_Panel
from .ui_panels.slice import CAM_SLICE_Panel
from .utils import (
    check_operations_on_load,
    updateOperation,
)


bl_info = {
    "name": "BlenderCAM - G-code Generation Tools",
    "author": "Vilem Novak & Contributors",
    "version":(1,0,32),
    "blender": (3, 6, 0),
    "location": "Properties > render",
    "description": "Generate Machining Paths for CNC",
    "warning": "",
    "doc_url": "https://blendercam.com/",
    "tracker_url": "",
    "category": "Scene",
}


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
    #CamObjectSilhouete,

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

    # .ui and .ui_panels - the order will affect the layout
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

    # .cam_operation - last to allow dependencies to register before it
    camOperation,
]


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

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

    km = addon_kc.keymaps.new(name='Object Mode')
    kmi = km.keymap_items.new(
        "wm.call_menu_pie",
        'C',
        'PRESS',
        alt=True,
    )
    kmi.properties.name = 'VIEW3D_MT_PIE_CAM'
    kmi.active = True


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)

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
        if 'CNCCAM_RENDER' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('CNCCAM_RENDER')

    wm = bpy.context.window_manager
    active_kc = wm.keyconfigs.active

    for key in active_kc.keymaps['Object Mode'].keymap_items:
        if (key.idname == 'wm.call_menu' and key.properties.name == 'VIEW3D_MT_PIE_CAM'):
            active_kc.keymaps['Object Mode'].keymap_items.remove(key)