from math import pi

from shapely.geometry import Point

import bpy

from .mortise import mortise

from ..constants import DT  # DT = Bit diameter tolerance

from ..utilities.compare_utils import angle
from ..utilities.logging_utils import log
from ..utilities.simple_utils import (
    active_name,
    duplicate,
    mirror_x,
    union,
    move,
    join_multiple,
    duplicate,
    difference,
    make_active,
    remove_multiple,
    rename,
    difference,
)


def finger(diameter, stem=2):
    """Create a joint shape based on the specified diameter and stem.

    This function generates a 3D joint shape using Blender's curve
    operations. It calculates the dimensions of a rectangle and an ellipse
    based on the provided diameter and stem parameters. The function then
    creates these shapes, duplicates and mirrors them, and performs boolean
    operations to form the final joint shape. The resulting object is named
    and cleaned up to ensure no overlapping vertices remain.

    Args:
        diameter (float): The diameter of the tool for joint creation.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 2.

    Returns:
        None: This function does not return any value.
    """

    RESOLUTION = 12  # Data resolution
    cube_sx = diameter * DT * (2 + stem - 1)
    cube_ty = diameter * DT
    cube_sy = 2 * diameter * DT
    circle_radius = diameter * DT / 2
    c1x = cube_sx / 2
    c2x = cube_sx / 2
    c2y = 3 * circle_radius
    c1y = circle_radius

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, cube_ty, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=cube_sx,
        Simple_length=cube_sy,
        use_cyclic_u=True,
        edit_mode=False,
    )
    bpy.context.active_object.name = "ftmprect"

    bpy.ops.curve.simple(
        align="WORLD",
        location=(c2x, c2y, 0),
        rotation=(0, 0, 0),
        Simple_Type="Ellipse",
        Simple_a=circle_radius,
        Simple_b=circle_radius,
        Simple_sides=4,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )

    bpy.context.active_object.name = "ftmpcirc_add"
    bpy.context.object.data.resolution_u = RESOLUTION

    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    duplicate()
    mirror_x()

    union("ftmp")
    rename("ftmp", "_sum")

    rc1 = circle_radius

    bpy.ops.curve.simple(
        align="WORLD",
        location=(c1x, c1y, 0),
        rotation=(0, 0, 0),
        Simple_Type="Ellipse",
        Simple_a=circle_radius,
        Simple_b=rc1,
        Simple_sides=4,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )

    bpy.context.active_object.name = "_circ_delete"
    bpy.context.object.data.resolution_u = RESOLUTION
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    duplicate()
    mirror_x()
    union("_circ")

    difference("_", "_sum")
    bpy.ops.object.curve_remove_doubles()
    rename("_sum", "_puzzle")


def fingers(diameter, inside, amount=1, stem=1):
    """Create a specified number of fingers for a joint tool.

    This function generates a set of fingers based on the provided diameter
    and tolerance values. It calculates the necessary translations for
    positioning the fingers and duplicates them if more than one is
    required. Additionally, it creates a receptacle using a silhouette
    offset from the fingers, allowing for precise joint creation.

    Args:
        diameter (float): The diameter of the tool used for joint creation.
        inside (float): The tolerance in the joint receptacle.
        amount (int?): The number of fingers to create. Defaults to 1.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 1.
    """

    xtranslate = -(4 + 2 * (stem - 1)) * (amount - 1) * diameter * DT / 2
    finger(diameter, stem=stem)  # generate male finger
    active_name("puzzlem")
    move(x=xtranslate, y=-0.00002)

    if amount > 1:
        # duplicate translate the amount needed (faster than generating new)
        for i in range(amount - 1):
            bpy.ops.object.duplicate_move(
                OBJECT_OT_duplicate={"linked": False, "mode": "TRANSLATION"},
                TRANSFORM_OT_translate={"value": ((4 + 2 * (stem - 1)) * diameter * DT, 0, 0.0)},
            )
        union("puzzle")

    active_name("fingers")
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    # Receptacle is made using the silhouette offset from the fingers
    if inside > 0:
        bpy.ops.object.silhouette_offset(offset=inside, style="1")
        active_name("receptacle")
        move(y=-inside)


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
    log.info(f"Joinery Loop Length {round(loop_length * 1000)}mm")
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
    log.info(f"Joinery Loop Length {round(loop_length * 1000)}mm")
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
        log.info("Placeholder")
        join_multiple("_mort")
        active_name("variable_mortise")
    return hpos
