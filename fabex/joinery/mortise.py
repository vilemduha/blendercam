import bpy

from .utilities.simple_utils import (
    active_name,
)


def mortise(length, thickness, finger_play, cx=0, cy=0, rotation=0):
    """Generates a mortise of length, thickness and finger_play tolerance
    cx and cy are the center position and rotation is the angle

    Args:
        length (float): length of the mortise
        thickness (float): thickness of material
        finger_play (float): tolerance for good fit
        cx (float): coordinate for x center of the finger
        cy (float):coordinate for y center of the finger
        rotation (float): angle of rotation
    """

    bpy.ops.curve.simple(
        align="WORLD",
        location=(cx, cy, 0),
        rotation=(0, 0, rotation),
        Simple_Type="Rectangle",
        Simple_width=length + finger_play,
        Simple_length=thickness,
        shape="3D",
        outputType="POLY",
        use_cyclic_u=True,
        handleType="AUTO",
        edit_mode=False,
    )
    active_name("_mortise")
