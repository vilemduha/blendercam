"""Fabex 'chains.py'

'CAM Chains' panel in Properties > Render
"""

import bpy
from bpy.types import UIList, Panel

from .parent_panel import CAMParentPanel


class CAM_UL_operations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        operation = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name, translate=False, icon_value=icon)
            icon = "LOCKED" if operation.computing else "UNLOCKED"
            if operation.computing:
                layout.label(text=operation.out_text)  # "computing" )
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class CAM_UL_chains(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        chain = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name, translate=False, icon_value=icon)
            icon = "LOCKED" if chain.computing else "UNLOCKED"
            if chain.computing:
                layout.label(text="computing")
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class CAM_CHAINS_Panel(CAMParentPanel, Panel):
    """CAM Chains Panel"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bl_label = "[ Chains ]"
    bl_idname = "FABEX_PT_CAM_CHAINS"
    bl_options = {"DEFAULT_CLOSED"}
    panel_interface_level = 1
    always_show_panel = True

    def __init__(self, *args, **kwargs):
        Panel.__init__(self, *args, **kwargs)
        CAMParentPanel.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    def draw(self, context):
        if self.level >= 1 and self.op is not None:
            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False

            row = layout.row()
            scene = bpy.context.scene

            row.template_list(
                "CAM_UL_chains",
                "id_list_chains",
                scene,
                "cam_chains",
                scene,
                "cam_active_chain",
            )
            box = row.box()
            col = box.column(align=True)
            col.scale_x = col.scale_y = 1.05
            col.operator(
                "scene.cam_chain_add",
                icon="ADD",
                text="",
            )
            col.operator(
                "scene.cam_chain_remove",
                icon="REMOVE",
                text="",
            )

            if len(scene.cam_chains) > 0:
                chain = scene.cam_chains[scene.cam_active_chain]
                row = layout.row()

                if chain:
                    row.template_list(
                        "CAM_UL_operations",
                        "id_list_chain_operations",
                        chain,
                        "operations",
                        chain,
                        "active_operation",
                    )
                    box = row.box()
                    col = box.column(align=True)
                    col.scale_x = col.scale_y = 1.05
                    col.operator(
                        "scene.cam_chain_operation_add",
                        icon="ADD",
                        text="",
                    )
                    col.operator(
                        "scene.cam_chain_operation_remove",
                        icon="REMOVE",
                        text="",
                    )
                    if len(chain.operations) > 0:
                        col.separator()
                        col.operator(
                            "scene.cam_chain_operation_up",
                            icon="TRIA_UP",
                            text="",
                        )
                        col.operator(
                            "scene.cam_chain_operation_down",
                            icon="TRIA_DOWN",
                            text="",
                        )

                    box = layout.box()
                    col = box.column(align=True)
                    col.scale_y = 1.2
                    if not chain.computing:
                        col.operator(
                            "object.calculate_cam_paths_chain",
                            text="Calculate Chain Paths & Export Gcode",
                            icon="FILE_CACHE",
                        )
                        col.operator(
                            "object.cam_export_paths_chain",
                            text="Export Chain G-code",
                            icon="EXPORT",
                        )
                        col.operator(
                            "object.cam_simulate_chain",
                            text="Simulate This Chain",
                            icon="RESTRICT_INSTANCED_OFF",
                        )

                        if not chain.valid:
                            col.alert = True
                            col.label(icon="ERROR", text="Can't Compute Chain!")
                            col.label(text=chain.invalid_reason)
                    else:
                        col.label(text="Chain Is Currently Computing")

                    box = layout.box()
                    col = box.column(align=True)
                    col.prop(chain, "name")
                    col.prop(chain, "filename")
