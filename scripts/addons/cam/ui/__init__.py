"""Fabex 'ui.__init__.py' © 2012 Vilem Novak

Import UI, Register and Unregister Classes
"""

import bpy
from bpy.props import PointerProperty

from .menus.import_gcode import TOPBAR_MT_import_gcode
from .menus.curve_creators import VIEW3D_MT_tools_add, VIEW3D_MT_tools_create
from .menus.curve_tools import VIEW3D_MT_tools_curvetools
from .menus.preset_menus import (
    CAM_CUTTER_MT_presets,
    CAM_MACHINE_MT_presets,
    CAM_OPERATION_MT_presets,
)
from .menus.viewport import Fabex_SubMenu, Fabex_Menu

from .panels.area_panel import CAM_AREA_Panel
from .panels.blank_panel import CAM_BLANK_Panel
from .panels.chains_panel import (
    CAM_CHAINS_Panel,
    CAM_UL_chains,
    CAM_UL_operations,
)
from .panels.curve_create_panel import VIEW3D_PT_tools_create
from .panels.curve_tools_panel import VIEW3D_PT_tools_curvetools
from .panels.cutter_panel import CAM_CUTTER_Panel
from .panels.feedrate_panel import CAM_FEEDRATE_Panel
from .panels.gcode_panel import CAM_GCODE_Panel
from .panels.info_panel import CAM_INFO_Panel
from .panels.machine_panel import CAM_MACHINE_Panel
from .panels.material_panel import CAM_MATERIAL_Panel
from .panels.movement_panel import CAM_MOVEMENT_Panel
from .panels.op_properties_panel import CAM_OPERATION_PROPERTIES_Panel
from .panels.operations_panel import CAM_OPERATIONS_Panel
from .panels.optimisation_panel import CAM_OPTIMISATION_Panel
from .panels.popup_panel import CAM_Popup_Panel

from .pie_menu.pie_cam import VIEW3D_MT_PIE_CAM
from .pie_menu.pie_chains import VIEW3D_MT_PIE_Chains
from .pie_menu.pie_pack_slice_relief import VIEW3D_MT_PIE_PackSliceRelief
from .pie_menu.pie_operation import VIEW3D_MT_PIE_Operation


classes = [
    # .menus
    TOPBAR_MT_import_gcode,
    VIEW3D_MT_tools_add,
    VIEW3D_MT_tools_create,
    VIEW3D_MT_tools_curvetools,
    Fabex_SubMenu,
    Fabex_Menu,
    CAM_CUTTER_MT_presets,
    CAM_OPERATION_MT_presets,
    CAM_MACHINE_MT_presets,
    # .viewport_ui and .panels - the order will affect the layout
    CAM_BLANK_Panel,
    CAM_UL_operations,
    CAM_UL_chains,
    CAM_CHAINS_Panel,
    CAM_OPERATIONS_Panel,
    CAM_INFO_Panel,
    CAM_MATERIAL_Panel,
    CAM_OPERATION_PROPERTIES_Panel,
    CAM_OPTIMISATION_Panel,
    CAM_AREA_Panel,
    CAM_MOVEMENT_Panel,
    CAM_FEEDRATE_Panel,
    CAM_CUTTER_Panel,
    CAM_GCODE_Panel,
    CAM_MACHINE_Panel,
    CAM_Popup_Panel,
    VIEW3D_PT_tools_curvetools,
    VIEW3D_PT_tools_create,
    # .pie_menu
    VIEW3D_MT_PIE_CAM,
    VIEW3D_MT_PIE_Operation,
    VIEW3D_MT_PIE_Chains,
    VIEW3D_MT_PIE_PackSliceRelief,
]


def progress_bar(self, context):
    progress = context.window_manager.progress
    percent = int(progress * 100)
    if progress > 0:
        layout = self.layout
        row = layout.row()
        row.scale_x = 2
        row.progress(
            factor=progress,
            text=f"Processing... {percent}%",
        )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_HT_header.append(progress_bar)
    bpy.types.TOPBAR_MT_file_import.append(TOPBAR_MT_import_gcode.draw)
    bpy.types.VIEW3D_MT_curve_add.append(VIEW3D_MT_tools_add.draw)
    bpy.types.VIEW3D_MT_editor_menus.append(Fabex_Menu.draw)

    bpy.types.WindowManager.progress = bpy.props.FloatProperty(default=0)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_HT_header.remove(progress_bar)
    bpy.types.TOPBAR_MT_file_import.remove(TOPBAR_MT_import_gcode.draw)
    bpy.types.VIEW3D_MT_curve_add.remove(VIEW3D_MT_tools_add.draw)
    bpy.types.VIEW3D_MT_editor_menus.remove(Fabex_Menu.draw)
