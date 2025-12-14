from math import (
    pi,
)


import bpy

from .finger import finger_pair
from .mortise import mortise

from ..utilities.simple_utils import (
    active_name,
    make_active,
    remove_multiple,
    join_multiple,
)


def create_base_plate(height, width, depth):
    """Creates blank plates for a box.

    Args:
        height (float): height size for box
        width (float): width size for box
        depth (float): depth size for box
    """

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, height / 2, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=width,
        Simple_length=height,
        shape="3D",
        outputType="POLY",
        use_cyclic_u=True,
        handleType="AUTO",
        edit_mode=False,
    )
    active_name("_back")
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, height / 2, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=depth,
        Simple_length=height,
        shape="3D",
        outputType="POLY",
        use_cyclic_u=True,
        handleType="AUTO",
        edit_mode=False,
    )
    active_name("_side")
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=width,
        Simple_length=depth,
        shape="3D",
        outputType="POLY",
        use_cyclic_u=True,
        handleType="AUTO",
        edit_mode=False,
    )
    active_name("_bottom")


def make_flex_pocket(length, height, finger_thick, finger_width, pocket_width):
    """creates pockets using mortise function for kerf bending

    Args:
        length (float): Length of pocket
        height (float): height of pocket
        finger_thick (float): thickness of finger
        finger_width (float): width of finger
        pocket_width (float): width of pocket
    """

    dist = 3 * finger_width / 2
    while dist < length:
        mortise(height - 2 * finger_thick, pocket_width, 0, dist, 0, pi / 2)
        active_name("_flex_pocket")
        dist += finger_width * 2

    join_multiple("_flex_pocket")
    active_name("flex_pocket")


def make_variable_flex_pocket(height, finger_thick, pocket_width, locations):
    """creates pockets pocket using mortise function for kerf bending

    Args:
        height (float): height of the side
        finger_thick (float): thickness of the finger
        pocket_width (float): width of pocket
        locations (tuple): coordinates for pocket
    """

    for dist in locations:
        mortise(height + 2 * finger_thick, pocket_width, 0, dist, 0, pi / 2)
        active_name("_flex_pocket")

    join_multiple("_flex_pocket")
    active_name("flex_pocket")


def create_flex_side(length, height, finger_thick, top_bottom=False):
    """crates a flex side for mortise on curve. Assumes the base fingers were created and exist

    Args:
        length (float): length of curve
        height (float): height of side
        finger_thick (float): finger thickness or thickness of material
        top_bottom (bool): fingers on top and bottom if true, just on bottom if false
    """
    if top_bottom:
        fingers = finger_pair("base", 0, height - finger_thick)
    else:
        make_active("base")
        fingers = bpy.context.active_object
        bpy.ops.transform.translate(value=(0.0, height / 2 - finger_thick / 2 + 0.0003, 0.0))

    bpy.ops.curve.simple(
        align="WORLD",
        location=(length / 2 + 0.00025, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=length,
        Simple_length=height,
        shape="3D",
        outputType="POLY",
        use_cyclic_u=True,
        handleType="AUTO",
        edit_mode=False,
    )
    active_name("no_fingers")

    bpy.ops.curve.simple(
        align="WORLD",
        location=(length / 2 + 0.00025, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=length,
        Simple_length=height,
        shape="3D",
        outputType="POLY",
        use_cyclic_u=True,
        handleType="AUTO",
        edit_mode=False,
    )
    active_name("_side")

    make_active("_side")
    fingers.select_set(True)
    bpy.ops.object.curve_boolean(boolean_type="DIFFERENCE")

    active_name("side")
    remove_multiple("_")
    remove_multiple("base")
