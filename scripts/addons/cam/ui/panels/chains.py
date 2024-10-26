"""Fabex 'chains.py'

'CAM Chains' panel in Properties > Render
"""

import bpy
from bpy.types import UIList, Panel

from .buttons_panel import CAMButtonsPanel
from ...utils import isChainValid


class CAM_UL_operations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        operation = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:

            layout.label(text=item.name, translate=False, icon_value=icon)
            icon = "LOCKED" if operation.computing else "UNLOCKED"
            if operation.computing:
                layout.label(text=operation.outtext)  # "computing" )
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


class CAM_CHAINS_Panel(CAMButtonsPanel, Panel):
    """CAM Chains Panel"""

    bl_label = "CAM Chains"
    bl_idname = "WORLD_PT_CAM_CHAINS"
    # bl_space_type = "VIEW_3D"
    # bl_region_type = "UI"
    # bl_category = "Fabex"
    panel_interface_level = 1
    always_show_panel = True

    def draw(self, context):
        if self.level >= 1 and self.op is not None:
            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False

            row = layout.row()
            scene = bpy.context.scene

            row.template_list("CAM_UL_chains", "", scene, "cam_chains", scene, "cam_active_chain")
            col = row.column(align=True)
            col.operator("scene.cam_chain_add", icon="ADD", text="")
            col.operator("scene.cam_chain_remove", icon="REMOVE", text="")

            if len(scene.cam_chains) > 0:
                chain = scene.cam_chains[scene.cam_active_chain]
                row = layout.row(align=True)

                if chain:
                    row.template_list(
                        "CAM_UL_operations", "", chain, "operations", chain, "active_operation"
                    )
                    col = row.column(align=True)
                    col.operator("scene.cam_chain_operation_add", icon="ADD", text="")
                    col.operator("scene.cam_chain_operation_remove", icon="REMOVE", text="")
                    if len(chain.operations) > 0:
                        col.operator("scene.cam_chain_operation_up", icon="TRIA_UP", text="")
                        col.operator("scene.cam_chain_operation_down", icon="TRIA_DOWN", text="")

                    col = layout.column(align=True)
                    if not chain.computing:
                        col.operator(
                            "object.calculate_cam_paths_chain",
                            text="Calculate Chain Paths & Export Gcode",
                        )
                        col.operator("object.cam_export_paths_chain", text="Export Chain G-code")
                        col.operator("object.cam_simulate_chain", text="Simulate This Chain")

                        valid, reason = isChainValid(chain, context)
                        if not valid:
                            col.label(icon="ERROR", text=f"Can't Compute Chain - Reason:\n")
                            col.label(text=reason)
                    else:
                        col.label(text="Chain Is Currently Computing")

                    box = layout.box()
                    col = box.column(align=True)
                    col.prop(chain, "name")
                    col.prop(chain, "filename")
