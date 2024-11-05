"""Fabex 'movement.py'

'CAM Movement' properties and panel in Properties > Render
"""

from math import pi

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from bpy.types import Panel, PropertyGroup

from .buttons_panel import CAMButtonsPanel
from ...utils import update_operation
from ...constants import (
    PRECISION,
    G64_INCOMPATIBLE_MACHINES,
)


class CAM_MOVEMENT_Properties(PropertyGroup):
    # movement parallel_step_back
    type: EnumProperty(
        name="Movement Type",
        items=(
            (
                "CONVENTIONAL",
                "Conventional (Up)",
                "Cutter rotates against the direction of the feed",
            ),
            (
                "CLIMB",
                "Climb (Down)",
                "Cutter rotates with the direction of the feed",
            ),
            (
                "MEANDER",
                "Meander (Zig Zag)",
                "Cutting is done both with and against the rotation of the spindle",
            ),
        ),
        description="movement type",
        default="CLIMB",
        update=update_operation,
    )

    insideout: EnumProperty(
        name="Direction",
        items=(
            ("INSIDEOUT", "Inside out", "a"),
            ("OUTSIDEIN", "Outside in", "a"),
        ),
        description="Approach to the piece",
        default="INSIDEOUT",
        update=update_operation,
    )

    spindle_rotation: EnumProperty(
        name="Spindle Rotation",
        items=(
            ("CW", "Clockwise", "a"),
            ("CCW", "Counter clockwise", "a"),
        ),
        description="Spindle rotation direction",
        default="CW",
        update=update_operation,
    )

    free_height: FloatProperty(
        name="Safe Height",
        description="Height where the machine can freely move without hitting the workpiece",
        default=0.01,
        min=0.0000,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )

    useG64: BoolProperty(
        name="G64 Trajectory",
        description="Use only if your machine supports G64 code. LinuxCNC and Mach3 do",
        default=False,
        update=update_operation,
    )

    G64: FloatProperty(
        name="Path Control Mode with Optional Tolerance",
        default=0.0001,
        min=0.0000,
        max=0.005,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )

    parallel_step_back: BoolProperty(
        name="Parallel Step Back",
        description="For roughing and finishing in one pass: mills "
        "material in climb mode, then steps back and goes "
        "between 2 last chunks back",
        default=False,
        update=update_operation,
    )

    helix_enter: BoolProperty(
        name="Helix Enter - EXPERIMENTAL",
        description="Enter material in helix",
        default=False,
        update=update_operation,
    )

    ramp_in_angle: FloatProperty(
        name="Ramp-in Angle",
        default=pi / 6,
        min=0,
        max=pi * 0.4999,
        precision=1,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_operation,
    )

    helix_diameter: FloatProperty(
        name="Helix Diameter - % of Cutter Diameter",
        default=90,
        min=10,
        max=100,
        precision=1,
        subtype="PERCENTAGE",
        update=update_operation,
    )

    ramp: BoolProperty(
        name="Ramp-in - EXPERIMENTAL",
        description="Ramps down the whole contour, so the cutline looks " "like helix",
        default=False,
        update=update_operation,
    )

    ramp_out: BoolProperty(
        name="Ramp-out - EXPERIMENTAL",
        description="Ramp out to not leave mark on surface",
        default=False,
        update=update_operation,
    )

    ramp_out_angle: FloatProperty(
        name="Ramp-out Angle",
        default=pi / 6,
        min=0,
        max=pi * 0.4999,
        precision=1,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_operation,
    )

    retract_tangential: BoolProperty(
        name="Retract Tangential - EXPERIMENTAL",
        description="Retract from material in circular motion",
        default=False,
        update=update_operation,
    )

    retract_radius: FloatProperty(
        name="Retract Arc Radius",
        default=0.001,
        min=0.000001,
        max=100,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )

    retract_height: FloatProperty(
        name="Retract Arc Height",
        default=0.001,
        min=0.00000,
        max=100,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )

    stay_low: BoolProperty(
        name="Stay Low if Possible",
        default=True,
        update=update_operation,
    )

    merge_dist: FloatProperty(
        name="Merge Distance - EXPERIMENTAL",
        default=0.0,
        min=0.0000,
        max=0.1,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )

    protect_vertical: BoolProperty(
        name="Protect Vertical",
        description="The path goes only vertically next to steep areas",
        default=True,
        update=update_operation,
    )

    protect_vertical_limit: FloatProperty(
        name="Verticality Limit",
        description="What angle is already considered vertical",
        default=pi / 45,
        min=0,
        max=pi * 0.5,
        precision=0,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_operation,
    )


class CAM_MOVEMENT_Panel(CAMButtonsPanel, Panel):
    """CAM Movement Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "╠ Movement ╣"
    bl_idname = "WORLD_PT_CAM_MOVEMENT"
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
        if self.op.maxz > self.op.movement.free_height:
            box = boxcol.box()
            subcol = box.column(align=True)
            subcol.alert = True
            subcol.label(text="! POSSIBLE COLLISION !", icon="ERROR")
            subcol.label(text="Depth Start > Free Movement")

        # Stay Low
        row = layout.row()
        row.use_property_split = False
        row.prop(self.op.movement, "stay_low", text="Stay Low (if possible)")

        # Parallel Stepback
        if self.level >= 1:
            if self.op.strategy in ["PARALLEL", "CROSS"]:
                if not self.op.movement.ramp:
                    row = layout.row()
                    row.use_property_split = False
                    row.prop(self.op.movement, "parallel_step_back")

        if self.level >= 2:
            # Use G64
            if context.scene.cam_machine.post_processor not in G64_INCOMPATIBLE_MACHINES:
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
                    row.prop(self.op.movement, "merge_dist", text="Merge Distance")

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
                    row.use_property_split = True
                    row.prop(self.op.movement, "ramp_in_angle", text="In Angle")
                    subheader, subpanel = subcol.panel("ramps_o", default_closed=True)
                    subheader.prop(self.op.movement, "ramp_out", text="Ramp Out")
                    if subpanel:
                        row = subcol.row()
                        row.use_property_split = True
                        row.enabled = self.op.movement.ramp_out
                        row.prop(self.op.movement, "ramp_out_angle", text="Out Angle")
