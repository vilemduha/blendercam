"""Fabex 'movement_props.py'

'CAM Movement Properties'
"""

from math import pi

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from bpy.types import PropertyGroup

from ..utilities.operation_utils import update_operation
from ..constants import (
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
        step=500,
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
    zig_zag_ramp: BoolProperty(
        name="Zigzag_ramp - EXPERIMENTAL",
        description="Ramps down the whole contour, so the cutline looks " "like zigzag_",
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
        step=500,
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

    merge_distance: FloatProperty(
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
        step=100,
        subtype="ANGLE",
        unit="ROTATION",
        update=update_operation,
    )
