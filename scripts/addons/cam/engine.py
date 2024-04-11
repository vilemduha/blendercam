from bl_ui.properties_material import (
    EEVEE_MATERIAL_PT_context_material,
    EEVEE_MATERIAL_PT_settings,
    EEVEE_MATERIAL_PT_surface,
)
import bpy
from bpy.types import RenderEngine

from .ui_panels.area import CAM_AREA_Panel
from .ui_panels.chains import CAM_CHAINS_Panel
from .ui_panels.cutter import CAM_CUTTER_Panel
from .ui_panels.feedrate import CAM_FEEDRATE_Panel
from .ui_panels.gcode import CAM_GCODE_Panel
from .ui_panels.info import CAM_INFO_Panel
from .ui_panels.interface import CAM_INTERFACE_Panel
from .ui_panels.machine import CAM_MACHINE_Panel
from .ui_panels.material import CAM_MATERIAL_Panel
from .ui_panels.movement import CAM_MOVEMENT_Panel
from .ui_panels.op_properties import CAM_OPERATION_PROPERTIES_Panel
from .ui_panels.operations import CAM_OPERATIONS_Panel
from .ui_panels.optimisation import CAM_OPTIMISATION_Panel
from .ui_panels.pack import CAM_PACK_Panel
from .ui_panels.slice import CAM_SLICE_Panel


class BLENDERCAM_ENGINE(RenderEngine):
    bl_idname = "BLENDERCAM_RENDER"
    bl_label = "BlenderCAM"
    bl_use_eevee_viewport = True


def get_panels():
    exclude_panels = {
        'RENDER_PT_eevee_performance',
        'RENDER_PT_opengl_sampling',
        'RENDER_PT_opengl_lighting',
        'RENDER_PT_opengl_color',
        'RENDER_PT_opengl_options',
        'RENDER_PT_simplify',
        'RENDER_PT_gpencil',
        'RENDER_PT_freestyle',
        'RENDER_PT_color_management',
        'MATERIAL_PT_viewport',
        'MATERIAL_PT_lineart',
    }

    panels = [
        EEVEE_MATERIAL_PT_context_material,
        EEVEE_MATERIAL_PT_surface,
        EEVEE_MATERIAL_PT_settings,

        CAM_INTERFACE_Panel,
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
        CAM_PACK_Panel,
        CAM_SLICE_Panel,
    ]

    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels
