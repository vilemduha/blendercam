"""CNC CAM 'movement.py'

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
                "Conventional / Up milling",
                "Cutter rotates against the direction of the feed",
            ),
            ("CLIMB", "Climb / Down milling", "Cutter rotates with the direction of the feed"),
            (
                "MEANDER",
                "Meander / Zig Zag",
                "Cutting is done both with and against the " "rotation of the spindle",
            ),
        ),
        description="movement type",
        default="CLIMB",
        update=update_operation,
    )

    insideout: EnumProperty(
        name="Direction",
        items=(("INSIDEOUT", "Inside out", "a"), ("OUTSIDEIN", "Outside in", "a")),
        description="Approach to the piece",
        default="INSIDEOUT",
        update=update_operation,
    )

    spindle_rotation: EnumProperty(
        name="Spindle Rotation",
        items=(("CW", "Clockwise", "a"), ("CCW", "Counter clockwise", "a")),
        description="Spindle rotation direction",
        default="CW",
        update=update_operation,
    )

    free_height: FloatProperty(
        name="Free Movement Height",
        default=0.01,
        min=0.0000,
        max=32,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )

    useG64: BoolProperty(
        name="G64 Trajectory",
        description="Use only if your machine supports " "G64 code. LinuxCNC and Mach3 do",
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

    bl_label = "CAM Movement"
    bl_idname = "WORLD_PT_CAM_MOVEMENT"
    panel_interface_level = 0

    prop_level = {
        "draw_cut_type": 1,
        "draw_spindle_rotation": 2,
        "draw_free_height": 0,
        "draw_use_g64": 2,
        "draw_parallel_stepback": 1,
        "draw_helix_enter": 2,
        "draw_ramp": 1,
        "draw_retract_tangential": 2,
        "draw_stay_low": 1,
        "draw_protect_vertical": 1,
    }

    def draw_cut_type(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op.movement, "type")
        if self.op.movement.type in ["BLOCK", "SPIRAL", "CIRCLES"]:
            self.layout.prop(self.op.movement, "insideout")

    def draw_spindle_rotation(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op.movement, "spindle_rotation")

    def draw_free_height(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op.movement, "free_height")
        if self.op.maxz > self.op.movement.free_height:
            self.layout.label(text="Depth Start > Free Movement")
            self.layout.label(text="POSSIBLE COLLISION")

    def draw_use_g64(self):
        if not self.has_correct_level():
            return
        if self.context.scene.cam_machine.post_processor not in G64_INCOMPATIBLE_MACHINES:
            self.layout.prop(self.op.movement, "useG64")
            if self.op.movement.useG64:
                self.layout.prop(self.op.movement, "G64")

    def draw_parallel_stepback(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ["PARALLEL", "CROSS"]:
            if not self.op.movement.ramp:
                self.layout.prop(self.op.movement, "parallel_step_back")

    def draw_helix_enter(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ["POCKET"]:
            self.layout.prop(self.op.movement, "helix_enter")
            if self.op.movement.helix_enter:
                self.layout.prop(self.op.movement, "ramp_in_angle")
                self.layout.prop(self.op.movement, "helix_diameter")

    def draw_ramp(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op.movement, "ramp")
        if self.op.movement.ramp:
            self.layout.prop(self.op.movement, "ramp_in_angle")
            self.layout.prop(self.op.movement, "ramp_out")
            if self.op.movement.ramp_out:
                self.layout.prop(self.op.movement, "ramp_out_angle")

    def draw_retract_tangential(self):
        if not self.has_correct_level():
            return
        if self.op.strategy in ["POCKET"]:
            self.layout.prop(self.op.movement, "retract_tangential")
            if self.op.movement.retract_tangential:
                self.layout.prop(self.op.movement, "retract_radius")
                self.layout.prop(self.op.movement, "retract_height")

    def draw_stay_low(self):
        if not self.has_correct_level():
            return
        self.layout.prop(self.op.movement, "stay_low")
        if self.op.movement.stay_low:
            self.layout.prop(self.op.movement, "merge_dist")

    def draw_protect_vertical(self):
        if not self.has_correct_level():
            return
        if self.op.cutter_type not in ["BALLCONE"]:
            self.layout.prop(self.op.movement, "protect_vertical")
            if self.op.movement.protect_vertical:
                self.layout.prop(self.op.movement, "protect_vertical_limit")

    def draw(self, context):
        self.context = context

        self.draw_cut_type()
        self.draw_spindle_rotation()
        self.draw_free_height()
        self.draw_use_g64()
        self.draw_parallel_stepback()
        self.draw_ramp()
        self.draw_helix_enter()
        self.draw_retract_tangential()
        self.draw_stay_low()
        self.draw_protect_vertical()
