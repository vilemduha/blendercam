from math import (
    asin,
    degrees,
    hypot,
    pi,
)

import bpy

from shapely.geometry import Point

from ..constants import DT

from .finger import fingers
from .mortise import mortise

from ..utilities.logging_utils import log
from ..utilities.simple_utils import (
    duplicate,
    mirror_y,
    union,
    difference,
    active_name,
    move,
    rotate,
    make_active,
    join_multiple,
    remove_doubles,
    add_rectangle,
)


def interlock_groove(length, thickness, finger_play, cx=0, cy=0, rotation=0):
    """Generates an interlocking groove.

    Args:
        length (float): Length of groove
        thickness (float): thickness of groove
        finger_play (float): tolerance for proper fit
        cx (float): center offset x
        cy (float): center offset y
        rotation (float): angle of rotation
    """
    mortise(length, thickness, finger_play, 0, 0, 0)
    bpy.ops.transform.translate(value=(length / 2 - finger_play / 2, 0.0, 0.0))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.context.active_object.rotation_euler.z = rotation
    bpy.ops.transform.translate(value=(cx, cy, 0.0))
    active_name("_groove")


def interlock_twist(length, thickness, finger_play, cx=0, cy=0, rotation=0, percentage=0.5):
    """Generates an interlocking twist.

    Args:
        length (float): Length of groove
        thickness (float): thickness of groove
        finger_play (float): tolerance for proper fit
        cx (float): center offset x
        cy (float): center offset y
        rotation (float): angle of rotation
        percentage (float): percentage amount the twist will take (between 0 and 1)
    """

    mortise(length, thickness, finger_play, 0, 0, 0)
    active_name("_tmp")
    mortise(length * percentage, thickness, finger_play, 0, 0, pi / 2)
    active_name("_tmp")
    h = hypot(thickness, length * percentage)
    oangle = degrees(asin(length * percentage / h))
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Sector",
        Simple_startangle=90 + oangle,
        Simple_endangle=180 - oangle,
        Simple_radius=h / 2,
        use_cyclic_u=True,
        edit_mode=False,
    )
    active_name("_tmp")

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Sector",
        Simple_startangle=270 + oangle,
        Simple_endangle=360 - oangle,
        Simple_radius=h / 2,
        use_cyclic_u=True,
        edit_mode=False,
    )
    active_name("_tmp")

    union("_tmp")
    rotate(rotation)
    move(x=cx, y=cy)
    active_name("_groove")
    remove_doubles()


def twist_line(length, thickness, finger_play, percentage, amount, distance, center=True):
    """Generates a multiple interlocking twist.

    Args:
        length (float): Length of groove
        thickness (float): thickness of groove
        finger_play (float): tolerance for proper fit
        percentage (float): percentage amount the twist will take (between 0 and 1)
        amount (int):amount of twists generated
        distance (float): distance between twists
        center (bool): center or not from origin
    """

    spacing = distance / amount
    while amount > 0:
        position = spacing * amount
        interlock_twist(length, thickness, finger_play, percentage=percentage, cx=position)
        log.info(f"Twistline {amount}, {distance}, {position}")
        amount -= 1

    join_multiple("_groove")
    active_name("twist_line")
    if center:
        move(x=(-distance - spacing) / 2)


def twist_separator_slot(length, thickness, finger_play=0.00005, percentage=0.5):
    """Generates a slot for interlocking twist separator.

    Args:
        length (float): Length of slot
        thickness (float): thickness of slot
        finger_play (float): tolerance for proper fit
        percentage (float): percentage amount the twist will take (between 0 and 1)
    """

    add_rectangle(thickness + finger_play / 2, length, center_y=False)
    move(y=((length * percentage - finger_play / 2) / 2))
    duplicate()
    mirror_y()
    join_multiple("simple_rectangle")
    active_name("_separator_slot")


def interlock_twist_separator(
    length,
    thickness,
    amount,
    spacing,
    edge_distance,
    finger_play=0.00005,
    percentage=0.5,
    start="rounded",
    end="rounded",
):
    """Generates a interlocking twist separator.

    Args:
        length (float): Length of separator
        thickness (float): thickness of separator
        amount (int): quantity of separation grooves
        spacing (float): distance between slots
        edge_distance (float): distance of the first slots close to the edge
        finger_play (float): tolerance for proper fit
        percentage (float): percentage amount the twist will take (between 0 and 1)
        start (string): type of start wanted (rounded, flat or other) not implemented
        start (string): type of end wanted (rounded, flat or other) not implemented
    """

    amount -= 1
    base_width = 2 * edge_distance + spacing * amount + thickness
    add_rectangle(base_width, length - finger_play * 2, center_x=False)
    active_name("_base")
    twist_separator_slot(length, thickness, finger_play, percentage)
    while amount > 0:
        duplicate(x=spacing)
        amount -= 1
    join_multiple("_separator_slot")
    move(x=edge_distance + thickness / 2)
    difference("_", "_base")
    active_name("twist_separator")


def single_interlock(
    finger_depth,
    finger_thick,
    finger_tolerance,
    x,
    y,
    groove_angle,
    type,
    amount=1,
    twist_percentage=0.5,
):
    """Generates a single interlock at coodinate x,y.

    Args:
        finger_depth (float): depth of finger
        finger_thick (float): thickness of finger
        finger_tolerance (float): tolerance for proper fit
        x (float): offset x
        y (float): offset y
        groove_angle (float): angle of rotation
        type (str): GROOVE, TWIST, PUZZLE are the valid choices
        twist_percentage: percentage of thickness for twist (not used in puzzle or groove)
    """
    if type == "GROOVE":
        interlock_groove(finger_depth, finger_thick, finger_tolerance, x, y, groove_angle)
    elif type == "TWIST":
        interlock_twist(
            finger_depth,
            finger_thick,
            finger_tolerance,
            x,
            y,
            groove_angle,
            percentage=twist_percentage,
        )
    elif type == "PUZZLE":
        fingers(finger_thick, finger_tolerance)


def distributed_interlock(
    loop,
    loop_length,
    finger_depth,
    finger_thick,
    finger_tolerance,
    finger_amount,
    tangent=0,
    fixed_angle=0,
    start=0.01,
    end=0.01,
    closed=True,
    type="GROOVE",
    twist_percentage=0.5,
):
    """Distributes interlocking joints of a fixed amount.
     Dynamically changes the finger tolerance with the angle differences

    Args:
        loop (list of tuples): coordinates curve
        loop_length (float): length of the curve
        finger_depth (float): depth of the mortise
        finger_thick (float) thickness of the material
        finger_tolerance (float): minimum finger tolerance
        finger_amount (int): quantity of fingers
        tangent (int):
        fixed_angle (float): 0 will be variable, desired angle for the finger
        closed (bool): False:open curve  -  True:closed curved
        twist_percentage = portion of twist finger which is the stem (for twist joint only)
        type (str): GROOVE, TWIST, PUZZLE are the valid choices
        start (float): start distance from first point
        end (float): end distance from last point
    """
    coords = list(loop.coords)
    log.info(closed)
    if not closed:
        spacing = (loop_length - start - end) / (finger_amount - 1)
        distance = start
        end_distance = loop_length - end
    else:
        spacing = loop_length / finger_amount
        distance = 0
        end_distance = loop_length

    j = 0
    log.info(f"Joinery Loop Length {round(loop_length * 1000)}mm")
    log.info(f"Distance Between Joints {round(spacing * 1000)}mm")

    for i, p in enumerate(coords):
        if i == 0:
            p_start = p

        if p != p_start:
            not_start = True
        else:
            not_start = False
        pd = loop.project(Point(p))

        if not_start:
            while distance <= pd and end_distance >= distance:
                if fixed_angle == 0:
                    groove_angle = angle(oldp, p) + pi / 2 + tangent
                else:
                    groove_angle = fixed_angle

                groove_point = loop.interpolate(distance)

                log.info(
                    f"{j} groove_angle {round(180 * groove_angle / pi)} distance {round(distance * 1000)}mm"
                )
                single_interlock(
                    finger_depth,
                    finger_thick,
                    finger_tolerance,
                    groove_point.x,
                    groove_point.y,
                    groove_angle,
                    type,
                    twist_percentage=twist_percentage,
                )

                j += 1
                distance = j * spacing + start
        oldp = p

    join_multiple("_groove")
    active_name("interlock")


def twist_female(name, length, diameter, tolerance, twist, tneck, tthick, twist_keep=False):
    """Add a twist lock to a receptacle.

    This function modifies the receptacle by adding a twist lock feature if
    the `twist` parameter is set to True. It performs several operations
    including interlocking the twist, rotating the object, and moving it to
    the correct position. If `twist_keep` is True, it duplicates the twist
    lock for further modifications. The function utilizes parameters such as
    length, diameter, tolerance, and thickness to accurately create the
    twist lock.

    Args:
        name (str): The name of the receptacle to be modified.
        length (float): The length of the receptacle.
        diameter (float): The diameter of the receptacle.
        tolerance (float): The tolerance value for the twist lock.
        twist (bool): A flag indicating whether to add a twist lock.
        tneck (float): The neck thickness for the twist lock.
        tthick (float): The thickness of the twist lock.
        twist_keep (bool?): A flag indicating whether to keep the twist
            lock after duplication. Defaults to False.
    """

    # add twist lock to receptacle
    if twist:
        interlock_twist(length, tthick, tolerance, cx=0, cy=0, rotation=0, percentage=tneck)
        rotate(pi / 2)
        move(y=-tthick / 2 + 2 * diameter + 2 * tolerance)
        active_name("xtemptwist")
        if twist_keep:
            duplicate()
            active_name("twist_keep_f")
        make_active(name)
        active_name("xtemp")
        union("xtemp")
        active_name(name)


def twist_male(
    name, length, diameter, tolerance, twist, tneck, tthick, angle, twist_keep=False, x=0, y=0
):
    """Add a twist lock to a male connector.

    This function modifies the geometry of a male connector by adding a
    twist lock feature. It utilizes various parameters to determine the
    dimensions and positioning of the twist lock. If the `twist_keep`
    parameter is set to True, it duplicates the twist lock for further
    modifications. The function also allows for adjustments in position
    through the `x` and `y` parameters.

    Args:
        name (str): The name of the connector to be modified.
        length (float): The length of the connector.
        diameter (float): The diameter of the connector.
        tolerance (float): The tolerance level for the twist lock.
        twist (bool): A flag indicating whether to add a twist lock.
        tneck (float): The neck thickness for the twist lock.
        tthick (float): The thickness of the twist lock.
        angle (float): The angle at which to rotate the twist lock.
        twist_keep (bool?): A flag indicating whether to keep the twist lock duplicate. Defaults to
            False.
        x (float?): The x-coordinate for positioning. Defaults to 0.
        y (float?): The y-coordinate for positioning. Defaults to 0.

    Returns:
        None: This function modifies the state of the connector but does not return a
            value.
    """

    # add twist lock to male connector
    if twist:
        interlock_twist(length, tthick, tolerance, cx=0, cy=0, rotation=0, percentage=tneck)
        rotate(pi / 2)
        move(y=-tthick / 2 + 2 * diameter * DT)
        rotate(angle)
        move(x=x, y=y)
        active_name("_twist")
        if twist_keep:
            duplicate()
            active_name("twist_keep_m")
        make_active(name)
        active_name("_tmp")
        difference("_", "_tmp")
        active_name(name)
