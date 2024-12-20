"""Fabex 'operators.__init__.py' © 2012 Vilem Novak

Import Properties, Register and Unregister Classes
"""

import bpy

from .bas_relief_ops import DoBasRelief, ProblemAreas
from .bridges_op import CamBridgesAdd
from .chain_ops import (
    CamChainAdd,
    CamChainOperationAdd,
    CamChainOperationDown,
    CamChainOperationRemove,
    CamChainOperationUp,
    CamChainRemove,
)
from .curve_create_ops import (
    CamCurveDrawer,
    CamCurveFlatCone,
    CamCurveGear,
    CamCurveHatch,
    CamCurveInterlock,
    CamCurveMortise,
    CamCurvePlate,
    CamCurvePuzzle,
)
from .curve_equation_ops import (
    CamCustomCurve,
    CamHypotrochoidCurve,
    CamLissajousCurve,
    CamSineCurve,
)
from .curve_tools_ops import (
    CamCurveBoolean,
    CamCurveConvexHull,
    CamCurveIntarsion,
    CamCurveSimpleOvercuts,
    CamCurveBoneFilletOvercuts,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,
    CamObjectSilhouette,
    CamOffsetSilhouete,
)
from .gcode_import_op import WM_OT_gcode_import
from .operation_ops import (
    CamOperationAdd,
    CamOperationCopy,
    CamOperationMove,
    CamOperationRemove,
)
from .orient_op import CamOrientationAdd
from .pack_op import CamPackObjects
from .path_ops import (
    PathExport,
    PathExportChain,
    PathsAll,
    PathsBackground,
    PathsChain,
    KillPathsBackground,
    CalculatePath,
)
from .position_op import CAM_MATERIAL_PositionObject
from .preset_ops import (
    AddPresetCamCutter,
    AddPresetCamMachine,
    AddPresetCamOperation,
)
from .simulation_ops import CAMSimulate, CAMSimulateChain
from .slice_op import CamSliceObjects


classes = [
    DoBasRelief,
    ProblemAreas,
    CamBridgesAdd,
    CamChainAdd,
    CamChainOperationAdd,
    CamChainOperationDown,
    CamChainOperationRemove,
    CamChainOperationUp,
    CamChainRemove,
    CamCurveDrawer,
    CamCurveFlatCone,
    CamCurveGear,
    CamCurveHatch,
    CamCurveInterlock,
    CamCurveMortise,
    CamCurvePlate,
    CamCurvePuzzle,
    CamCustomCurve,
    CamHypotrochoidCurve,
    CamLissajousCurve,
    CamSineCurve,
    CamCurveBoolean,
    CamCurveConvexHull,
    CamCurveIntarsion,
    CamCurveSimpleOvercuts,
    CamCurveBoneFilletOvercuts,
    CamCurveRemoveDoubles,
    CamMeshGetPockets,
    CamObjectSilhouette,
    CamOffsetSilhouete,
    WM_OT_gcode_import,
    CamOperationAdd,
    CamOperationCopy,
    CamOperationMove,
    CamOperationRemove,
    CamOrientationAdd,
    CamPackObjects,
    PathExport,
    PathExportChain,
    PathsAll,
    PathsBackground,
    PathsChain,
    KillPathsBackground,
    CalculatePath,
    CAM_MATERIAL_PositionObject,
    AddPresetCamCutter,
    AddPresetCamMachine,
    AddPresetCamOperation,
    CAMSimulate,
    CAMSimulateChain,
    CamSliceObjects,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
