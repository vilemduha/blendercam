"""Fabex 'engine.py'

Engine definition, options and panels.
"""

from bl_ui.properties_material import (
    EEVEE_MATERIAL_PT_context_material,
    EEVEE_MATERIAL_PT_settings,
    EEVEE_MATERIAL_PT_surface,
)
import bpy
from bpy.types import RenderEngine

from .ui.panels.area import CAM_AREA_Panel
from .ui.panels.chains import CAM_CHAINS_Panel
from .ui.panels.cutter import CAM_CUTTER_Panel
from .ui.panels.feedrate import CAM_FEEDRATE_Panel
from .ui.panels.gcode import CAM_GCODE_Panel

# from .ui.panels.info import CAM_INFO_Panel

# from .ui.panels.interface import CAM_INTERFACE_Panel
from .ui.panels.machine import CAM_MACHINE_Panel
from .ui.panels.material import CAM_MATERIAL_Panel
from .ui.panels.movement import CAM_MOVEMENT_Panel
from .ui.panels.op_properties import CAM_OPERATION_PROPERTIES_Panel
from .ui.panels.operations import CAM_OPERATIONS_Panel
from .ui.panels.optimisation import CAM_OPTIMISATION_Panel
from .ui.panels.pack import CAM_PACK_Panel
from .ui.panels.slice import CAM_SLICE_Panel


class FABEX_ENGINE(RenderEngine):
    bl_idname = "FABEX_RENDER"
    bl_label = "Fabex CNC/CAM"
    bl_use_eevee_viewport = True


def get_panels():
    """Retrieve a list of panels for the Blender UI.

    This function compiles a list of UI panels that are compatible with the
    Blender rendering engine. It excludes certain predefined panels that are
    not relevant for the current context. The function checks all subclasses
    of the `bpy.types.Panel` and includes those that have the
    `COMPAT_ENGINES` attribute set to include 'BLENDER_RENDER', provided
    they are not in the exclusion list.

    Returns:
        list: A list of panel classes that are compatible with the
        Blender rendering engine, excluding specified panels.
    """

    exclude_panels = {
        "RENDER_PT_eevee_performance",
        "RENDER_PT_opengl_sampling",
        "RENDER_PT_opengl_lighting",
        "RENDER_PT_opengl_color",
        "RENDER_PT_opengl_options",
        "RENDER_PT_simplify",
        "RENDER_PT_gpencil",
        "RENDER_PT_freestyle",
        "RENDER_PT_color_management",
        "MATERIAL_PT_viewport",
        "MATERIAL_PT_lineart",
    }

    panels = [
        EEVEE_MATERIAL_PT_context_material,
        EEVEE_MATERIAL_PT_surface,
        EEVEE_MATERIAL_PT_settings,
        # CAM_INTERFACE_Panel,
        CAM_CHAINS_Panel,
        CAM_OPERATIONS_Panel,
        # CAM_INFO_Panel,
        CAM_MATERIAL_Panel,
        CAM_OPERATION_PROPERTIES_Panel,
        CAM_OPTIMISATION_Panel,
        CAM_AREA_Panel,
        CAM_MOVEMENT_Panel,
        CAM_FEEDRATE_Panel,
        CAM_CUTTER_Panel,
        CAM_GCODE_Panel,
        CAM_MACHINE_Panel,
        CAM_PACK_Panel,
        CAM_SLICE_Panel,
    ]

    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, "COMPAT_ENGINES") and "BLENDER_RENDER" in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels
