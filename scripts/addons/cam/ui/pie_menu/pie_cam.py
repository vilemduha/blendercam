"""Fabex 'pie_cam.py'

'Fabex' Pie Menu - Parent to all other CAM Pie Menus
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_CAM(Menu):
    bl_label = "∴    Fabex    ∴"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == "FABEX_RENDER"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        pie = layout.menu_pie()
        pie.scale_y = 1.5
        pie.emboss = "NONE"

        # Left
        pie.operator(
            "wm.call_panel",
            text="Machine",
            icon="DESKTOP",
        ).name = "FABEX_PT_CAM_MACHINE"

        # Right
        pie.operator(
            "wm.call_panel",
            text="Material",
            icon="META_CUBE",
        ).name = "FABEX_PT_CAM_MATERIAL"

        # Bottom
        if len(scene.cam_operations) < 1:
            pie.operator(
                "scene.cam_operation_add",
                text="Add Operation",
                icon="ADD",
            )
        else:
            pie.operator(
                "wm.call_menu_pie",
                text="Active Operation",
                icon="MOD_ENVELOPE",
            ).name = "VIEW3D_MT_PIE_Operation"

        # Top
        if len(scene.cam_operations) < 1:
            box = pie.box()
            box.label(text="(No Operations)")
        else:
            pie.operator(
                "wm.call_menu_pie",
                text="Operations & Chains",
                icon="LINKED",
            ).name = "VIEW3D_MT_PIE_Chains"

        # Top Left
        box = pie.box()
        if len(scene.cam_operations) > 0:
            operation = scene.cam_operations[scene.cam_active_operation]
            if len(operation.info.warnings) > 1:
                box.alert = True
            else:
                box.alert = False
        box.operator(
            "wm.call_panel",
            text="Info & Warnings",
            icon="INFO",
        ).name = "FABEX_PT_CAM_INFO"

        # Top Right
        box = pie.box()
        box.operator(
            "wm.call_menu_pie",
            text="Pack, Slice, Relief",
            icon="PACKAGE",
        ).name = "VIEW3D_MT_PIE_PackSliceRelief"

        # Bottom Left
        box = pie.box()
        box.operator(
            "wm.call_panel",
            text="Curve Tools",
            icon="TOOL_SETTINGS",
        ).name = "VIEW3D_PT_tools_curvetools"

        # Bottom Right
        box = pie.box()
        box.operator(
            "wm.call_panel",
            text="Curve Creators",
            icon="CURVE_DATA",
        ).name = "VIEW3D_PT_tools_create"
