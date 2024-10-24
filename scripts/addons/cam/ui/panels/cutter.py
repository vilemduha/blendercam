"""CNC CAM 'cutter.py'

'CAM Cutter' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_CUTTER_Panel(CAMButtonsPanel, Panel):
    """CAM Cutter Panel"""

    bl_label = "CAM Cutter"
    bl_idname = "WORLD_PT_CAM_CUTTER"
    panel_interface_level = 0

    def draw(self, context):
        layout = self.layout
        # Cutter Preset Menu
        if self.level >= 1:
            row = layout.row(align=True)
            row.menu("CAM_CUTTER_MT_presets", text=bpy.types.CAM_CUTTER_MT_presets.bl_label)
            row.operator("render.cam_preset_cutter_add", text="", icon="ADD")
            row.operator("render.cam_preset_cutter_add", text="", icon="REMOVE").remove_active = (
                True
            )

        # Cutter ID
        if self.level >= 2:
            layout.prop(self.op, "cutter_id")

        # Cutter Type
        layout.prop(self.op, "cutter_type")

        # Ball Radius
        if self.op.cutter_type in ["BALLCONE"]:
            layout.prop(self.op, "ball_radius")

        # Bullnose Radius
        if self.op.cutter_type in ["BULLNOSE"]:
            layout.prop(self.op, "bull_corner_radius")

        # Cyclone Diameter
        if self.op.cutter_type in ["CYLCONE"]:
            layout.prop(self.op, "cylcone_diameter")

        # Cutter Tip Angle
        if self.op.cutter_type in ["VCARVE", "BALLCONE", "BULLNOSE", "CYLCONE"]:
            layout.prop(self.op, "cutter_tip_angle")

        # Laser
        if self.op.cutter_type in ["LASER"]:
            layout.prop(self.op, "Laser_on")
            layout.prop(self.op, "Laser_off")
            layout.prop(self.op, "Laser_cmd")
            layout.prop(self.op, "Laser_delay")

        # Plasma
        if self.op.cutter_type in ["PLASMA"]:
            layout.prop(self.op, "Plasma_on")
            layout.prop(self.op, "Plasma_off")
            layout.prop(self.op, "Plasma_delay")
            layout.prop(self.op, "Plasma_dwell")
            layout.prop(self.op, "lead_in")
            layout.prop(self.op, "lead_out")

        # Custom
        if self.op.cutter_type in ["CUSTOM"]:
            if self.op.optimisation.use_exact:
                layout.label(text="Warning - only Convex Shapes Are Supported. ", icon="COLOR_RED")
                layout.label(text="If Your Custom Cutter Is Concave,")
                layout.label(text="Switch Exact Mode Off.")
            layout.prop_search(self.op, "cutter_object_name", bpy.data, "objects")

        # Cutter Diameter
        layout.prop(self.op, "cutter_diameter")

        # Cutter Flutes
        if self.level >= 1:
            if self.op.cutter_type not in ["LASER", "PLASMA"]:
                layout.prop(self.op, "cutter_flutes")

            # Cutter Description
            layout.prop(self.op, "cutter_description")

        # Cutter Engagement
        if self.op.cutter_type in ["LASER", "PLASMA"]:
            return
        if self.op.strategy in ["CUTOUT"]:
            return

        if self.op.cutter_type in ["BALLCONE"]:
            engagement = round(100 * self.op.dist_between_paths / self.op.ball_radius, 1)
        else:
            engagement = round(100 * self.op.dist_between_paths / self.op.cutter_diameter, 1)

        layout.label(text=f"Cutter Engagement: {engagement}%")

        if engagement > 50:
            layout.label(text="WARNING: CUTTER ENGAGEMENT > 50%")
