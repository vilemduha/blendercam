"""Fabex 'movement.py'

'CAM Movement' properties and panel in Properties > Render
"""

from math import pi

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_MOVEMENT_Panel(CAMParentPanel, Panel):
    """CAM Movement Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Movement ]"
    bl_idname = "FABEX_PT_CAM_MOVEMENT"
    panel_interface_level = 0

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Milling Type
        if self.level >= 1:
            col = layout.column()
            col.scale_y = 1.2
            movement = self.op.movement.type
            if movement == "MEANDER":
                icon = "ANIM"
            elif movement == "CLIMB":
                icon = "SORT_ASC"
            else:
                icon = "SORT_DESC"
            col.prop(self.op.movement, "type", text="Milling Type", icon=icon)
            if self.op.movement.type in ["BLOCK", "SPIRAL", "CIRCLES"]:
                col.prop(self.op.movement, "insideout")

        # Spindle Rotation
        if self.level >= 2:
            rotation = self.op.movement.spindle_rotation
            icon = "LOOP_FORWARDS" if rotation == "CW" else "LOOP_BACK"
            col.prop(self.op.movement, "spindle_rotation", text="Cutter Spin", icon=icon)

        # Free Height
        box = layout.box()
        boxcol = box.column(align=True)
        boxcol.label(text="Z Clearance", icon="CON_FLOOR")
        boxcol.prop(self.op.movement, "free_height")
        if self.op.max_z > self.op.movement.free_height:
            box = boxcol.box()
            subcol = box.column(align=True)
            subcol.alert = True
            subcol.label(text="! POSSIBLE COLLISION !", icon="ERROR")
            subcol.label(text="Depth Start > Free Movement")

        # Stay Low
        row = layout.row()
        row.use_property_split = False
        row.prop(self.op.movement, "stay_low", text="Stay Low (if possible)")
        row.prop(self.op.movement, "merge_distance")

        # Parallel Stepback
        if self.level >= 1:
            if self.op.strategy in ["PARALLEL", "CROSS"]:
                if not self.op.movement.ramp:
                    row = layout.row()
                    row.use_property_split = False
                    row.prop(self.op.movement, "parallel_step_back")

            if self.level >= 2:
                # Use G64
                # Currently checking against a hard-coded value here,
                # Consider moving this to a scene property
                if context.scene.cam_machine.post_processor not in ["GRBL"]:
                    layout.use_property_split = False
                    header, panel = layout.panel("g64", default_closed=True)
                    header.prop(self.op.movement, "useG64", text="G64 Trajectory")
                    if panel:
                        panel.enabled = self.op.movement.useG64
                        col = panel.column(align=True)
                        col.use_property_split = True
                        col.prop(self.op.movement, "G64", text="Tolerance")

            # Retract Tangential
            if self.op.strategy in ["POCKET"]:
                layout.use_property_split = False
                header, panel = layout.panel("tengential", default_closed=True)
                header.prop(self.op.movement, "retract_tangential", text="Retract Tangential")
                if panel:
                    panel.enabled = self.op.movement.retract_tangential
                    col = panel.column(align=True)
                    col.use_property_split = True
                    col.prop(self.op.movement, "retract_radius", text="Arc Radius")
                    col.prop(self.op.movement, "retract_height", text="Arc Height")

        # Protect Vertical
        if self.level >= 1:
            if self.op.cutter_type not in ["BALLCONE"]:
                layout.use_property_split = False
                header, panel = layout.panel("vertical", default_closed=False)
                header.prop(self.op.movement, "protect_vertical", text="Protect Vertical")
                if panel:
                    panel.enabled = self.op.movement.protect_vertical
                    col = panel.column(align=True)
                    col.use_property_split = True
                    col.prop(self.op.movement, "protect_vertical_limit", text="Angle Limit")

        if self.level >= 3:
            header, parent_panel = layout.panel("experiment", default_closed=True)
            header.label(text="╼ EXPERIMENTAL ╾", icon="EXPERIMENTAL")
            if parent_panel:
                col = parent_panel.column(align=True)

                # Merge Distance
                if self.op.movement.stay_low:
                    row = col.row()
                    row.use_property_split = True
                    row.prop(self.op.movement, "merge_distance", text="Merge Distance")

                # Helix Enter
                if self.op.strategy in ["POCKET"]:
                    header, panel = col.panel("helix", default_closed=True)
                    header.prop(self.op.movement, "helix_enter", text="Helix Enter")
                    if panel:
                        subcol = panel.column(align=True)
                        subcol.use_property_split = True
                        subcol.enabled = self.op.movement.helix_enter
                        subcol.prop(self.op.movement, "ramp_in_angle")
                        subcol.prop(self.op.movement, "helix_diameter")

                # Ramp
                header, panel = col.panel("ramps", default_closed=True)
                header.prop(self.op.movement, "ramp", text="Ramp")
                if panel:
                    subcol = panel.column(align=True)
                    subcol.enabled = self.op.movement.ramp
                    row = subcol.row()
                    row.prop(self.op.movement, "zig_zag_ramp", text="Zigzag Ramp")
                    row = subcol.row()
                    row.use_property_split = True
                    row.prop(self.op.movement, "ramp_in_angle", text="In Angle")
                    subheader, subpanel = subcol.panel("ramps_o", default_closed=True)
                    subheader.prop(self.op.movement, "ramp_out", text="Ramp Out")
                    if subpanel:
                        row = subcol.row()
                        row.use_property_split = True
                        row.enabled = self.op.movement.ramp_out
                        row.prop(self.op.movement, "ramp_out_angle", text="Out Angle")
