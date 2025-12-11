"""Fabex 'curve_tools.py' © 2012 Vilem Novak

Panels displayed in the 3D Viewport - Curve Tools, Creators and Import G-code
"""

from bpy.types import Panel


# panel containing all tools
class VIEW3D_PT_tools_curvetools(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "[ Curve Tools ]"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        col = layout.column()
        col.operator("object.curve_boolean", icon="MOD_BOOLEAN")
        col.operator("object.convex_hull", icon="MOD_SOLIDIFY")
        col.operator("object.curve_intarsion", icon="OUTLINER_DATA_META")
        column = col.column(align=True)
        column.operator("object.curve_overcuts", icon="CON_SIZELIKE")
        column.operator("object.curve_overcuts_b", icon="GROUP_BONE")
        column = col.column(align=True)
        column.operator(
            "object.silhouette",
            icon="USER",
            text="Object Silhouette",
        )
        column.operator(
            "object.silhouette_offset",
            icon="COMMUNITY",
            text="Silhouette Offset",
        )
        col.operator(
            "object.curve_remove_doubles",
            icon="FORCE_CHARGE",
            text="Remove Curve Doubles",
        )
        col.operator(
            "object.mesh_get_pockets",
            icon="HOLDOUT_ON",
            text="Get Pocket Surfaces",
        )

        column = col.column(align=True)
        column.operator(
            "object.cam_pack_objects",
            icon="STICKY_UVS_LOC",
            text="Pack Curves on Sheet",
        )
        column.operator(
            "object.cam_slice_objects",
            icon="ALIGN_FLUSH",
            text="Slice Model to Sheet",
        )

        col.operator(
            "scene.calculate_bas_relief",
            icon="RNDCURVE",
            text="Bas Relief",
        )
