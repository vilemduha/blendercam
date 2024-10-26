"""Fabex 'pie_chains.py'

'Operations & Chains' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Chains(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operations & Chains    ∴"

    def draw(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column()
        column.label(text="Operations", icon="MOD_ENVELOPE")
        column.menu("CAM_OPERATION_MT_presets", text="Presets", icon="RIGHTARROW")
        row = column.row()
        row.template_list(
            "CAM_UL_operations", "", scene, "cam_operations", scene, "cam_active_operation"
        )

        column = row.column(align=True)
        column.operator("scene.cam_operation_add", icon="ADD", text="")
        column.operator("scene.cam_operation_copy", icon="COPYDOWN", text="")
        column.operator("scene.cam_operation_remove", icon="REMOVE", text="")
        column.separator()
        column.operator("scene.cam_operation_move", icon="TRIA_UP", text="").direction = "UP"
        column.operator("scene.cam_operation_move", icon="TRIA_DOWN", text="").direction = "DOWN"

        column = box.column(align=True)
        if not operation.valid:
            column.label(text="Select a Valid Object to Calculate the Path.")
        # will be disable if not valid
        column.operator("object.calculate_cam_path", text="Calculate Path & Export G-code")
        if operation.valid:
            if operation.name is not None:
                name = f"cam_path_{operation.name}"
                if scene.objects.get(name) is not None:
                    column.operator("object.cam_export", text="Export G-code ")

        if operation.valid:
            column.operator("object.cam_simulate", text="Simulate This Operation")

        column = box.column(align=True)
        column.prop(operation, "name")
        column.prop(operation, "filename")
        column.prop(operation, "geometry_source")
        if operation.strategy == "CURVE":
            if operation.geometry_source == "OBJECT":
                column.prop_search(operation, "object_name", bpy.data, "objects")
            elif operation.geometry_source == "COLLECTION":
                column.prop_search(operation, "collection_name", bpy.data, "collections")
        else:
            if operation.geometry_source == "OBJECT":
                column.prop_search(operation, "object_name", bpy.data, "objects")
                if operation.enable_A:
                    column.prop(operation, "rotation_A")
                if operation.enable_B:
                    column.prop(operation, "rotation_B")

            elif operation.geometry_source == "COLLECTION":
                column.prop_search(operation, "collection_name", bpy.data, "collections")
            else:
                column.prop_search(operation, "source_image_name", bpy.data, "images")

        if operation.strategy in ["CARVE", "PROJECTED_CURVE"]:
            column.prop_search(operation, "curve_object", bpy.data, "objects")
            if operation.strategy == "PROJECTED_CURVE":
                column.prop_search(operation, "curve_object1", bpy.data, "objects")

        # Right
        box = pie.box()
        column = box.column()
        column.label(text="Chains", icon="LINKED")
        row = column.row()
        row.template_list("CAM_UL_chains", "", scene, "cam_chains", scene, "cam_active_chain")

        column = row.column()
        column.operator("scene.cam_chain_add", icon="ADD", text="")
        column.operator("scene.cam_chain_remove", icon="REMOVE", text="")

        column = box.column()

        if len(scene.cam_chains) > 0:
            chain = scene.cam_chains[scene.cam_active_chain]
            row = column.row(align=True)

            if chain:
                row.template_list(
                    "CAM_UL_operations", "", chain, "operations", chain, "active_operation"
                )
                column = row.column(align=True)
                column.operator("scene.cam_chain_operation_add", icon="ADD", text="")
                column.operator("scene.cam_chain_operation_remove", icon="REMOVE", text="")
                if len(chain.operations) > 0:
                    column.operator("scene.cam_chain_operation_up", icon="TRIA_UP", text="")
                    column.operator("scene.cam_chain_operation_down", icon="TRIA_DOWN", text="")

                column = box.column(align=True)
                if not chain.computing:
                    column.operator(
                        "object.calculate_cam_paths_chain",
                        text="Calculate Chain Paths & Export G-code",
                    )
                    column.operator("object.cam_export_paths_chain", text="Export Chain G-code")
                    column.operator("object.cam_simulate_chain", text="Simulate This Chain")

                #                    valid, reason = isChainValid(chain, context)
                #                    if not valid:
                #                        column.label(icon="ERROR", text=f"Can't compute chain - reason:\n")
                #                        column.label(text=reason)
                else:
                    column.label(text="chain is currently computing")

                column = box.column()
                column.prop(chain, "name")
                column.prop(chain, "filename")

        # Bottom
        row = pie.row()
        row.label(text="")

        # Top
        box = pie.box()
        column = box.column(align=True)
        if operation.maxz > operation.movement.free_height:
            column.label(text="!ERROR! COLLISION!")
            column.label(text="Depth Start > Free Movement Height")
            column.label(text="!ERROR! COLLISION!")
            column.prop(operation.movement, "free_height")
            separator = column.separator(factor=1)
        column.scale_x = 2
        column.scale_y = 2
        column.emboss = "NONE"
        column.operator("wm.call_menu_pie", text="", icon="HOME").name = "VIEW3D_MT_PIE_CAM"
