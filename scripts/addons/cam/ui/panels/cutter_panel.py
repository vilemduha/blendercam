"""Fabex 'cutter.py'

'CAM Cutter' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel
from ..icons import preview_collections


class CAM_CUTTER_Panel(CAMParentPanel, Panel):
    """CAM Cutter Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Cutter ]"
    bl_idname = "FABEX_PT_CAM_CUTTER"
    panel_interface_level = 0

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        fabex_icons = preview_collections["FABEX"]
        cutter_icons = {
            "END": "EndMillIcon",
            "BALLNOSE": "BallnoseIcon",
            "BULLNOSE": "BullnoseIcon",
            "VCARVE": "VCarveIcon",
            "BALLCONE": "BallconeIcon",
            "CYLCONE": "CylinderConeIcon",
            "LASER": "LaserPlasmaIcon",
            "PLASMA": "LaserPlasmaIcon",
            "CUSTOM": "FabexCNC_Logo",
        }

        # Cutter Preset Menu
        if self.level >= 1:
            row = layout.row(align=True)
            row.menu("CAM_CUTTER_MT_presets", text=bpy.types.CAM_CUTTER_MT_presets.bl_label)
            row.operator(
                "render.cam_preset_cutter_add",
                text="",
                icon="ADD",
            )
            row.operator(
                "render.cam_preset_cutter_add",
                text="",
                icon="REMOVE",
            ).remove_active = True

        box = layout.box()
        col = box.column(align=True)

        # Cutter Type
        col.prop(
            self.op,
            "cutter_type",
            text="Type",
            icon_value=fabex_icons[cutter_icons[self.op.cutter_type]].icon_id,
        )

        # Ball Radius
        if self.op.cutter_type in ["BALLCONE"]:
            col.prop(self.op, "ball_radius")

        # Bullnose Radius
        if self.op.cutter_type in ["BULLNOSE"]:
            col.prop(self.op, "bull_corner_radius")

        # Cyclone Diameter
        if self.op.cutter_type in ["CYLCONE"]:
            col.prop(self.op, "cylcone_diameter")

        # Cutter Tip Angle
        if self.op.cutter_type in ["VCARVE", "BALLCONE", "BULLNOSE", "CYLCONE"]:
            col.prop(self.op, "cutter_tip_angle")

        # Laser
        if self.op.cutter_type in ["LASER"]:
            col.prop(self.op, "laser_on")
            col.prop(self.op, "laser_off")
            col.prop(self.op, "laser_cmd")
            col.prop(self.op, "laser_delay")

        # Plasma
        if self.op.cutter_type in ["PLASMA"]:
            col.prop(self.op, "plasma_on")
            col.prop(self.op, "plasma_off")
            col.prop(self.op, "plasma_delay")
            col.prop(self.op, "plasma_dwell")
            col.prop(self.op, "lead_in")
            col.prop(self.op, "lead_out")

        # Custom
        if self.op.cutter_type in ["CUSTOM"]:
            if self.op.optimisation.use_exact:
                col.label(text="Warning - only Convex Shapes Are Supported. ", icon="COLOR_RED")
                col.label(text="If Your Custom Cutter Is Concave,")
                col.label(text="Switch Exact Mode Off.")
            col.prop_search(self.op, "cutter_object_name", bpy.data, "objects")

        # Cutter Diameter
        col.prop(self.op, "cutter_diameter", text="Diameter")

        # Cutter Flutes
        if self.level >= 1:
            if self.op.cutter_type not in ["LASER", "PLASMA"]:
                col.prop(self.op, "cutter_flutes", text="Flutes")

        # Cutter ID
        if self.level >= 2:
            col = box.column(align=True)
            col.prop(self.op, "cutter_id")

            # Cutter Description
            col.prop(self.op, "cutter_description", text="Description")

        # Cutter Engagement
        if self.op.cutter_type in ["LASER", "PLASMA"]:
            return
        if self.op.strategy in ["CUTOUT"]:
            return

        # Cutter Engagement
        if self.op is not None:
            box = layout.box()
            col = box.column(align=True)
            # Warns if cutter engagement is greater than 50%
            if self.op.cutter_type in ["BALLCONE"]:
                engagement = round(
                    100 * self.op.distance_between_paths / self.op.ball_radius,
                    1,
                )
            else:
                engagement = round(
                    100 * self.op.distance_between_paths / self.op.cutter_diameter,
                    1,
                )

            if engagement > 50:
                col.alert = True
                col.label(text="Warning: High Engagement", icon="ERROR")

            col.label(text=f"Engagement: {engagement}%", icon="MOD_SHRINKWRAP")
