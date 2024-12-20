"""Fabex 'joinery.py' © 2021 Alain Pelletier

Functions to create various woodworking joints - mortise, finger etc.
"""

from math import (
    asin,
    atan2,
    degrees,
    hypot,
    pi,
)

from shapely.geometry import (
    LineString,
    Point,
)

import bpy

from . import puzzle_joinery

from .utilities.shapely_utils import shapely_to_curve
from .utilities.simple_utils import (
    active_name,
    union,
    rotate,
    move,
    remove_doubles,
    join_multiple,
    duplicate,
    add_rectangle,
    mirror_y,
    difference,
    make_active,
    remove_multiple,
)


# boolean operations for curve objects


def finger_amount(space, size):
    """Calculates the amount of fingers needed from the available space vs the size of the finger

    Args:
        space (float):available distance to cover
        size (float): size of the finger
    """
    finger_amt = space / size
    if (finger_amt % 1) != 0:
        finger_amt = round(finger_amt) + 1
    if (finger_amt % 2) != 0:
        finger_amt = round(finger_amt) + 1
    return finger_amt


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
        print("Twistline", amount, distance, position)
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


def horizontal_finger(length, thickness, finger_play, amount, center=True):
    """Generates an interlocking horizontal finger pair _wfa and _wfb.

    _wfa is centered at 0,0
    _wfb is _wfa offset by one length

    Args:
        length (float): Length of mortise
        thickness (float): thickness of material
        amount (int): quantity of fingers
        finger_play (float): tolerance for proper fit
        center (bool): centered of not
    """

    if center:
        for i in range(amount):
            if i == 0:
                mortise(length, thickness, finger_play, 0, thickness / 2)
                active_name("_width_finger")
            else:
                mortise(length, thickness, finger_play, i * 2 * length, thickness / 2)
                active_name("_width_finger")
                mortise(length, thickness, finger_play, -i * 2 * length, thickness / 2)
                active_name("_width_finger")
    else:
        for i in range(amount):
            mortise(length, thickness, finger_play, length / 2 + 2 * i * length, 0)
            active_name("_width_finger")

    join_multiple("_width_finger")

    active_name("_wfa")
    bpy.ops.object.duplicate_move(
        OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
        TRANSFORM_OT_translate={"value": (length, 0.0, 0.0)},
    )
    active_name("_wfb")


def vertical_finger(length, thickness, finger_play, amount):
    """Generates an interlocking horizontal finger pair _vfa and _vfb.

    _vfa is starts at 0,0
    _vfb is _vfa offset by one length

    Args:
        length (float): Length of mortise
        thickness (float): thickness of material
        amount (int): quantity of fingers
        finger_play (float): tolerance for proper fit
    """

    for i in range(amount):
        mortise(length, thickness, finger_play, 0, i * 2 * length + length / 2, rotation=pi / 2)
        active_name("_height_finger")

    join_multiple("_height_finger")
    active_name("_vfa")
    bpy.ops.object.duplicate_move(
        OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
        TRANSFORM_OT_translate={"value": (0, -length, 0.0)},
    )
    active_name("_vfb")


def finger_pair(name, dx=0, dy=0):
    """Creates a duplicate set of fingers.

    Args:
        name (str): name of original finger
        dx (float): x offset
        dy (float): y offset
    """

    make_active(name)
    xpos = (dx / 2) * 1.006
    ypos = 1.006 * dy / 2

    bpy.ops.object.duplicate_move(
        OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
        TRANSFORM_OT_translate={"value": (xpos, ypos, 0.0)},
    )
    active_name("_finger_pair")

    make_active(name)

    bpy.ops.object.duplicate_move(
        OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
        TRANSFORM_OT_translate={"value": (-xpos, -ypos, 0.0)},
    )
    active_name("_finger_pair")
    join_multiple("_finger_pair")
    bpy.ops.object.select_all(action="DESELECT")
    return bpy.context.active_object


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


def angle(a, b):
    """returns angle of a vector

    Args:
        a (tuple): point a x,y coordinates
        b (tuple): point b x,y coordinates
    """

    return atan2(b[1] - a[1], b[0] - a[0])


def angle_difference(a, b, c):
    """returns the difference between two lines with three points

    Args:
        a (tuple): point a x,y coordinates
        b (tuple): point b x,y coordinates
        c (tuple): point c x,y coordinates
    """
    return angle(a, b) - angle(b, c)


def fixed_finger(loop, loop_length, finger_size, finger_thick, finger_tolerance, base=False):
    """distributes mortises of a fixed distance.  Dynamically changes the finger tolerance with the angle differences

    Args:
        loop (list of tuples): takes in a shapely shape
        loop_length (float): length of loop
        finger_size (float): size of the mortise
        finger_thick (float): thickness of the material
        finger_tolerance (float): minimum finger tolerance
        base (bool): if base exists, it will join with it
    """

    coords = list(loop.coords)
    old_mortise_angle = 0
    distance = finger_size / 2
    j = 0
    print("Joinery Loop Length", round(loop_length * 1000), "mm")
    for i, p in enumerate(coords):
        if i == 0:
            p_start = p

        if p != p_start:
            not_start = True
        else:
            not_start = False
        pd = loop.project(Point(p))

        if not_start:
            while distance <= pd:
                mortise_angle = angle(oldp, p)
                mortise_angle_difference = abs(mortise_angle - old_mortise_angle)
                mad = 1 + 6 * min(mortise_angle_difference, pi / 4) / (
                    pi / 4
                )  # factor for tolerance for the finger

                if base:
                    mortise(finger_size, finger_thick, finger_tolerance * mad, distance, 0, 0)
                    active_name("_base")
                else:
                    mortise_point = loop.interpolate(distance)
                    mortise(
                        finger_size,
                        finger_thick,
                        finger_tolerance * mad,
                        mortise_point.x,
                        mortise_point.y,
                        mortise_angle,
                    )

                j += 1
                distance = j * 2 * finger_size + finger_size / 2
                old_mortise_angle = mortise_angle
        oldp = p
    if base:
        join_multiple("_base")
        active_name("base")
        move(x=finger_size)
    else:
        join_multiple("_mort")
        active_name("mortise")


def find_slope(p1, p2):
    """returns slope of a vector

    Args:
        p1 (tuple): point 1 x,y coordinates
        p2 (tuple): point 2 x,y coordinates
    """
    return (p2[1] - p1[1]) / max(p2[0] - p1[0], 0.00001)


def slope_array(loop):
    """Returns an array of slopes from loop coordinates.

    Args:
        loop (list of tuples): list of coordinates for a curve
    """

    remove_multiple("-")
    coords = list(loop.coords)
    #    pnt_amount = round(length / resolution)
    sarray = []
    dsarray = []
    for i, p in enumerate(coords):
        distance = loop.project(Point(p))
        if i != 0:
            slope = find_slope(p, oldp)
            sarray.append((distance, slope * -0.001))
        oldp = p
    for i, p in enumerate(sarray):
        distance = p[0]
        if i != 0:
            slope = find_slope(p, oldp)
            if abs(slope) > 10:
                print(distance)
            dsarray.append((distance, slope * -0.00001))
        oldp = p
    derivative = LineString(sarray)
    dderivative = LineString(dsarray)
    shapely_to_curve("-derivative", derivative, 0.0)
    shapely_to_curve("-doublederivative", dderivative, 0.0)
    return sarray


def d_slope_array(loop, resolution=0.001):
    """Returns a double derivative array or slope of the slope

    Args:
        loop (list of tuples): list of coordinates for a curve
        resolution (float): granular resolution of the array
    """
    length = loop.length
    pnt_amount = round(length / resolution)
    sarray = []
    dsarray = []
    for i in range(pnt_amount):
        distance = i * resolution
        pt = loop.interpolate(distance)
        p = (pt.x, pt.y)
        if i != 0:
            slope = abs(angle(p, oldp))
            sarray.append((distance, slope * -0.01))
        oldp = p
    for i, p in enumerate(sarray):
        distance = p[0]
        if i != 0:
            slope = find_slope(p, oldp)
            if abs(slope) > 10:
                print(distance)
            dsarray.append((distance, slope * -0.1))
        oldp = p
    dderivative = LineString(dsarray)
    shapely_to_curve("doublederivative", dderivative, 0.0)
    return sarray


def variable_finger(
    loop,
    loop_length,
    min_finger,
    finger_size,
    finger_thick,
    finger_tolerance,
    adaptive,
    base=False,
    double_adaptive=False,
):
    """Distributes mortises of a fixed distance. Dynamically changes the finger tolerance with the angle differences

    Args:
        loop (list of tuples): takes in a shapely shape
        loop_length (float): length of loop
        finger_size (float): size of the mortise
        finger_thick (float): thickness of the material
        min_finger (float): minimum finger size
        finger_tolerance (float): minimum finger tolerance
        adaptive (float): angle threshold to reduce finger size
        base (bool): join with base if true
        double_adaptive (bool): uses double adaptive algorithm if true
    """
    coords = list(loop.coords)
    old_mortise_angle = 0
    distance = min_finger / 2
    finger_sz = min_finger
    oldfinger_sz = min_finger
    hpos = []  # hpos is the horizontal positions of the middle of the mortise
    # slope_array(loop)
    print("Joinery Loop Length", round(loop_length * 1000), "mm")
    for i, p in enumerate(coords):
        if i == 0:
            p_start = p

        if p != p_start:
            not_start = True
        else:
            not_start = False
        pd = loop.project(Point(p))

        if not_start:
            while distance <= pd:
                mortise_angle = angle(oldp, p)
                mortise_angle_difference = abs(mortise_angle - old_mortise_angle)
                mad = 1 + 6 * min(mortise_angle_difference, pi / 4) / (
                    pi / 4
                )  # factor for tolerance for the finger
                # move finger by the factor mad greater with larger angle difference
                distance += mad * finger_tolerance
                mortise_point = loop.interpolate(distance)
                if mad > 2 and double_adaptive:
                    hpos.append(distance)  # saves the mortise center

                hpos.append(distance + finger_sz)  # saves the mortise center
                if base:
                    mortise(
                        finger_sz, finger_thick, finger_tolerance * mad, distance + finger_sz, 0, 0
                    )
                    active_name("_base")
                else:
                    mortise(
                        finger_sz,
                        finger_thick,
                        finger_tolerance * mad,
                        mortise_point.x,
                        mortise_point.y,
                        mortise_angle,
                    )
                    if i == 1:
                        #  put a mesh cylinder at the first coordinates to indicate start
                        remove_multiple("start_here")
                        bpy.ops.mesh.primitive_cylinder_add(
                            radius=finger_thick / 2,
                            depth=0.025,
                            enter_editmode=False,
                            align="WORLD",
                            location=(mortise_point.x, mortise_point.y, 0),
                            scale=(1, 1, 1),
                        )
                        active_name("start_here_mortise")

                old_distance = distance
                old_mortise_point = mortise_point
                finger_sz = finger_size
                next_angle_difference = pi

                #   adaptive finger length start
                while finger_sz > min_finger and next_angle_difference > adaptive:
                    #                while finger_sz > min_finger and next_angle_difference > adaptive:
                    # reduce the size of finger by a percentage... the closer to 1.0, the slower
                    finger_sz *= 0.95
                    distance = old_distance + 3 * oldfinger_sz / 2 + finger_sz / 2
                    mortise_point = loop.interpolate(distance)  # get the next mortise point
                    next_mortise_angle = angle(
                        (old_mortise_point.x, old_mortise_point.y),
                        (mortise_point.x, mortise_point.y),
                    )  # calculate next angle
                    next_angle_difference = abs(next_mortise_angle - mortise_angle)

                oldfinger_sz = finger_sz
                old_mortise_angle = mortise_angle
        oldp = p
    if base:
        join_multiple("_base")
        active_name("base")
    else:
        print("Placeholder")
        join_multiple("_mort")
        active_name("variable_mortise")
    return hpos


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
        puzzle_joinery.fingers(finger_thick, finger_tolerance)


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
    print(closed)
    if not closed:
        spacing = (loop_length - start - end) / (finger_amount - 1)
        distance = start
        end_distance = loop_length - end
    else:
        spacing = loop_length / finger_amount
        distance = 0
        end_distance = loop_length

    j = 0
    print("Joinery Loop Length", round(loop_length * 1000), "mm")
    print("Distance Between Joints", round(spacing * 1000), "mm")

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

                print(
                    j,
                    "groove_angle",
                    round(180 * groove_angle / pi),
                    "distance",
                    round(distance * 1000),
                    "mm",
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
