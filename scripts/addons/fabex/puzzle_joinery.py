"""Fabex 'puzzle_joinery.py' © 2021 Alain Pelletier

Functions to add various puzzle joints as curves.
"""

from math import (
    cos,
    degrees,
    pi,
    sin,
    sqrt,
    tan,
)

import bpy

from .constants import DT
from . import joinery

from .utilities.shapely_utils import shapely_to_curve
from .utilities.simple_utils import (
    duplicate,
    mirror_x,
    mirror_y,
    union,
    intersect,
    rename,
    difference,
    active_name,
    move,
    rotate,
    make_active,
    remove_multiple,
    select_multiple,
    join_multiple,
    remove_doubles,
    add_rectangle,
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

    # DT = Bit diameter tolerance
    global DT
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

    global DT  # Bit diameter tolerance

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
        joinery.interlock_twist(length, tthick, tolerance, cx=0, cy=0, rotation=0, percentage=tneck)
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
    global DT
    if twist:
        joinery.interlock_twist(length, tthick, tolerance, cx=0, cy=0, rotation=0, percentage=tneck)
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


def bar(
    width,
    thick,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    twist_keep=False,
    twist_line=False,
    twist_line_amount=2,
    which="MF",
):
    """Create a bar with specified dimensions and joint features.

    This function generates a bar with customizable parameters such as
    width, thickness, and joint characteristics. It can automatically
    determine the number of fingers in the joint if the amount is set to
    zero. The function also supports various options for twisting and neck
    dimensions, allowing for flexible design of the bar according to the
    specified parameters. The resulting bar can be manipulated further based
    on the provided options.

    Args:
        width (float): The length of the bar.
        thick (float): The thickness of the bar.
        diameter (float): The diameter of the tool used for joint creation.
        tolerance (float): The tolerance in the joint.
        amount (int?): The number of fingers in the joint; 0 means auto-generate. Defaults to
            0.
        stem (float?): The radius of the stem or neck of the joint. Defaults to 1.
        twist (bool?): Whether to add a twist lock. Defaults to False.
        tneck (float?): The percentage the twist neck will have compared to thickness. Defaults
            to 0.5.
        tthick (float?): The thickness of the twist material. Defaults to 0.01.
        twist_keep (bool?): Whether to keep the twist feature. Defaults to False.
        twist_line (bool?): Whether to add a twist line. Defaults to False.
        twist_line_amount (int?): The amount for the twist line. Defaults to 2.
        which (str?): Specifies the type of joint; options are 'M', 'F', 'MF', 'MM', 'FF'.
            Defaults to 'MF'.

    Returns:
        None: This function does not return a value but modifies the state of the 3D
            model in Blender.
    """

    global DT
    if amount == 0:
        amount = round(thick / ((4 + 2 * (stem - 1)) * diameter * DT)) - 1
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=width,
        Simple_length=thick,
        use_cyclic_u=True,
        edit_mode=False,
    )
    active_name("tmprect")

    fingers(diameter, tolerance, amount, stem=stem)

    if which == "MM" or which == "M" or which == "MF":
        rename("fingers", "_tmpfingers")
        rotate(-pi / 2)
        move(x=width / 2)
        rename("tmprect", "_tmprect")
        union("_tmp")
        active_name("tmprect")
        twist_male(
            "tmprect",
            thick,
            diameter,
            tolerance,
            twist,
            tneck,
            tthick,
            -pi / 2,
            x=width / 2,
            twist_keep=twist_keep,
        )

    twist_female(
        "receptacle", thick, diameter, tolerance, twist, tneck, tthick, twist_keep=twist_keep
    )
    rename("receptacle", "_tmpreceptacle")
    if which == "FF" or which == "F" or which == "MF":
        rotate(-pi / 2)
        move(x=-width / 2)
        rename("tmprect", "_tmprect")
        difference("_tmp", "_tmprect")
        active_name("tmprect")
        if twist_keep:
            make_active("twist_keep_f")
            rotate(-pi / 2)
            move(x=-width / 2)

    remove_multiple("_")  # Remove temporary base and holes
    remove_multiple("fingers")  # Remove temporary base and holes

    if twist_line:
        joinery.twist_line(thick, tthick, tolerance, tneck, twist_line_amount, width)
        if twist_keep:
            duplicate()
        active_name("tmptwist")
        difference("tmp", "tmprect")
    rename("tmprect", "Puzzle_bar")
    remove_multiple("tmp")  # Remove temporary base and holes
    make_active("Puzzle_bar")


def arc(
    radius,
    thick,
    angle,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    twist_keep=False,
    which="MF",
):
    """Generate an arc with specified parameters.

    This function creates a 3D arc based on the provided radius, thickness,
    angle, and other parameters. It handles the generation of fingers for
    the joint and applies twisting features if specified. The function also
    manages the orientation and positioning of the generated arc in a 3D
    space.

    Args:
        radius (float): The radius of the curve.
        thick (float): The thickness of the bar.
        angle (float): The angle of the arc (must not be zero).
        diameter (float): The diameter of the tool for joint creation.
        tolerance (float): Tolerance in the joint.
        amount (int?): The amount of fingers in the joint; 0 means auto-generate. Defaults to
            0.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 1.
        twist (bool?): Whether to add a twist lock. Defaults to False.
        tneck (float?): Percentage the twist neck will have compared to thickness. Defaults to
            0.5.
        tthick (float?): Thickness of the twist material. Defaults to 0.01.
        twist_keep (bool?): Whether to keep the twist. Defaults to False.
        which (str?): Specifies which joint to generate ('M', 'F', 'MF'). Defaults to 'MF'.

    Returns:
        None: This function does not return a value but modifies the 3D scene
            directly.
    """

    global DT  # diameter tolerance for diameter of finger creation

    if angle == 0:  # angle cannot be 0
        angle = 0.01

    negative = False
    if angle < 0:  # if angle < 0 then negative is true
        angle = -angle
        negative = True

    if amount == 0:
        amount = round(thick / ((4 + 2 * (stem - 1)) * diameter * DT)) - 1

    fingers(diameter, tolerance, amount, stem=stem)
    twist_female(
        "receptacle", thick, diameter, tolerance, twist, tneck, tthick, twist_keep=twist_keep
    )
    twist_female("testing", thick, diameter, tolerance, twist, tneck, tthick, twist_keep=twist_keep)
    print("Generating Arc")
    # generate arc
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Segment",
        Simple_a=radius - thick / 2,
        Simple_b=radius + thick / 2,
        Simple_startangle=-0.0001,
        Simple_endangle=degrees(angle),
        Simple_radius=radius,
        use_cyclic_u=False,
        edit_mode=False,
    )
    bpy.context.active_object.name = "tmparc"

    rename("fingers", "_tmpfingers")

    rotate(pi)
    move(x=radius)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    rename("tmparc", "_tmparc")
    if which == "MF" or which == "M":
        union("_tmp")
        active_name("base")
        twist_male("base", thick, diameter, tolerance, twist, tneck, tthick, pi, x=radius)
        rename("base", "_tmparc")

    rename("receptacle", "_tmpreceptacle")
    mirror_y()
    move(x=radius)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    rotate(angle)
    make_active("_tmparc")

    if which == "MF" or which == "F":
        difference("_tmp", "_tmparc")
    bpy.context.active_object.name = "PUZZLE_arc"
    bpy.ops.object.curve_remove_doubles()
    remove_multiple("_")  # Remove temporary base and holes
    make_active("PUZZLE_arc")
    if which == "M":
        rotate(-angle)
        mirror_y()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        rotate(-pi / 2)
        move(y=radius)
        rename("PUZZLE_arc", "PUZZLE_arc_male")
    elif which == "F":
        mirror_x()
        move(x=radius)
        rotate(pi / 2)
        rename("PUZZLE_arc", "PUZZLE_arc_receptacle")
    else:
        move(x=-radius)
    # bpy.ops.object.transform_apply(location=True, rotation=False, scale=False, properties=False)
    #
    if negative:  # mirror if angle is negative
        mirror_y()
    #
    # bpy.ops.object.curve_remove_doubles()


def arc_bar_arc(
    length,
    radius,
    thick,
    angle,
    angleb,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    which="MF",
    twist_keep=False,
    twist_line=False,
    twist_line_amount=2,
):
    """Generate an arc bar joint with specified parameters.

    This function creates a joint consisting of male and female sections
    based on the provided parameters. It adjusts the length to account for
    the radius and thickness, generates a base rectangle, and then
    constructs the male and/or female sections as specified. Additionally,
    it can create a twist lock feature if required. The function utilizes
    Blender's bpy operations to manipulate 3D objects.

    Args:
        length (float): The total width of the segments including 2 * radius and thickness.
        radius (float): The radius of the curve.
        thick (float): The thickness of the bar.
        angle (float): The angle of the female part.
        angleb (float): The angle of the male part.
        diameter (float): The diameter of the tool for joint creation.
        tolerance (float): Tolerance in the joint.
        amount (int?): The number of fingers in the joint; 0 means auto-generate. Defaults to
            0.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 1.
        twist (bool?): Whether to add a twist lock feature. Defaults to False.
        tneck (float?): Percentage the twist neck will have compared to thickness. Defaults to
            0.5.
        tthick (float?): Thickness of the twist material. Defaults to 0.01.
        which (str?): Specifies which joint to generate ('M', 'F', or 'MF'). Defaults to 'MF'.
        twist_keep (bool?): Whether to keep the twist after creation. Defaults to False.
        twist_line (bool?): Whether to create a twist line feature. Defaults to False.
        twist_line_amount (int?): Amount for the twist line feature. Defaults to 2.

    Returns:
        None: This function does not return a value but modifies the Blender scene
            directly.
    """

    # adjust length to include 2x radius + thick
    length -= radius * 2 + thick

    # generate base rectangle
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=length * 1.005,
        Simple_length=thick,
        use_cyclic_u=True,
        edit_mode=False,
    )
    active_name("tmprect")

    #  Generate male section and join to the base
    if which == "M" or which == "MF":
        arc(
            radius,
            thick,
            angleb,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="M",
        )
        move(x=length / 2)
        active_name("tmp_male")
        select_multiple("tmp")
        bpy.ops.object.curve_boolean(boolean_type="UNION")
        active_name("male")
        remove_multiple("tmp")
        rename("male", "tmprect")

    # Generate female section and join to base
    if which == "F" or which == "MF":
        arc(
            radius,
            thick,
            angle,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="F",
        )
        move(x=-length / 2)
        active_name("tmp_receptacle")
        union("tmp")
        active_name("tmprect")

    if twist_line:
        joinery.twist_line(thick, tthick, tolerance, tneck, twist_line_amount, length)
        if twist_keep:
            duplicate()
        active_name("tmptwist")
        difference("tmp", "tmprect")

    active_name("arcBarArc")
    make_active("arcBarArc")


def arc_bar(
    length,
    radius,
    thick,
    angle,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    twist_keep=False,
    which="MF",
    twist_line=False,
    twist_line_amount=2,
):
    """Generate an arc bar joint based on specified parameters.

    This function constructs an arc bar joint by generating male and female
    sections according to the specified parameters such as length, radius,
    thickness, and joint type. The function adjusts the length to account
    for the radius and thickness of the bar and creates the appropriate
    geometric shapes for the joint. It also includes options for twisting
    and adjusting the neck thickness of the joint.

    Args:
        length (float): The total width of the segments including 2 * radius and thickness.
        radius (float): The radius of the curve.
        thick (float): The thickness of the bar.
        angle (float): The angle of the female part.
        diameter (float): The diameter of the tool for joint creation.
        tolerance (float): Tolerance in the joint.
        amount (int?): The number of fingers in the joint; 0 means auto-generate. Defaults to
            0.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 1.
        twist (bool?): Whether to add a twist lock. Defaults to False.
        tneck (float?): Percentage the twist neck will have compared to thickness. Defaults to
            0.5.
        tthick (float?): Thickness of the twist material. Defaults to 0.01.
        twist_keep (bool?): Whether to keep the twist. Defaults to False.
        which (str?): Specifies which joint to generate ('M', 'F', 'MF'). Defaults to 'MF'.
        twist_line (bool?): Whether to include a twist line. Defaults to False.
        twist_line_amount (int?): Amount of twist line. Defaults to 2.
    """

    if which == "M":
        which = "MM"
    elif which == "F":
        which = "FF"
    # adjust length to include 2x radius + thick
    length -= radius * 2 + thick

    # generate base rectangle
    #  Generate male section and join to the base
    if which == "MM" or which == "MF":
        bar(
            length,
            thick,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="M",
            twist_keep=twist_keep,
            twist_line=twist_line,
            twist_line_amount=twist_line_amount,
        )
        active_name("tmprect")

    if which == "FF" or which == "FM":
        bar(
            length,
            thick,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="F",
            twist_keep=twist_keep,
            twist_line=twist_line,
            twist_line_amount=twist_line_amount,
        )
        rotate(pi)
        active_name("tmprect")

    # Generate female section and join to base
    if which == "FF" or which == "MF":
        arc(
            radius,
            thick,
            angle,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="F",
        )
        move(x=-length / 2 * 0.998)
        active_name("tmp_receptacle")
        union("tmp")
        active_name("arcBar")
        remove_multiple("tmp")

    if which == "MM":
        arc(
            radius,
            thick,
            angle,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="M",
        )
        bpy.ops.transform.mirror(
            orient_type="GLOBAL",
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type="GLOBAL",
            constraint_axis=(True, False, False),
        )
        move(x=-length / 2 * 0.998)
        active_name("tmp_receptacle")
        union("tmp")
        active_name("arcBar")
        remove_multiple("tmp")

    make_active("arcBar")


def multiangle(
    radius,
    thick,
    angle,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    combination="MFF",
):
    """Generate a multi-angle joint based on specified parameters.

    This function creates a multi-angle joint by generating various
    geometric shapes using the provided parameters such as radius,
    thickness, angle, diameter, and tolerance. It utilizes Blender's
    operations to create and manipulate curves, resulting in a joint that
    can be customized with different combinations of male and female parts.
    The function also allows for automatic generation of the number of
    fingers in the joint and includes options for twisting and neck
    dimensions.

    Args:
        radius (float): The radius of the curve.
        thick (float): The thickness of the bar.
        angle (float): The angle of the female part.
        diameter (float): The diameter of the tool for joint creation.
        tolerance (float): Tolerance in the joint.
        amount (int?): The amount of fingers in the joint; 0 means auto-generate. Defaults to
            0.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 1.
        twist (bool?): Indicates if a twist lock addition is required. Defaults to False.
        tneck (float?): Percentage the twist neck will have compared to thickness. Defaults to
            0.5.
        tthick (float?): Thickness of the twist material. Defaults to 0.01.
        combination (str?): Specifies which joint to generate ('M', 'F', 'MF', 'MFF', 'MMF').
            Defaults to 'MFF'.

    Returns:
        None: This function does not return a value but performs operations in
            Blender.
    """

    r_exterior = radius + thick / 2
    r_interior = radius - thick / 2

    height = sqrt(r_exterior * r_exterior - radius * radius) + r_interior / 4

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, height, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=r_interior,
        Simple_length=r_interior / 2,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    active_name("tmp_rect")

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Circle",
        Simple_sides=4,
        Simple_radius=r_interior,
        shape="3D",
        use_cyclic_u=True,
        edit_mode=False,
    )
    move(y=radius * tan(angle))
    active_name("tmpCircle")

    arc(
        radius,
        thick,
        angle,
        diameter,
        tolerance,
        amount=amount,
        stem=stem,
        twist=twist,
        tneck=tneck,
        tthick=tthick,
        which="MF",
    )
    active_name("tmp_arc")
    if combination == "MFF":
        duplicate()
        mirror_x()
    elif combination == "MMF":
        arc(
            radius,
            thick,
            angle,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="M",
        )
        active_name("tmp_arc")
        mirror_y()
        rotate(pi / 2)
    union("tmp_")
    difference("tmp", "tmp_")
    active_name("multiAngle60")


def t(
    length,
    thick,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    combination="MF",
    base_gender="M",
    corner=False,
):
    """Generate a 3D model based on specified parameters.

    This function creates a 3D model by manipulating geometric shapes based
    on the provided parameters. It handles different combinations of shapes
    and orientations based on the specified gender and corner options. The
    function utilizes several helper functions to perform operations such as
    moving, duplicating, and uniting shapes to form the final model.

    Args:
        length (float): The length of the model.
        thick (float): The thickness of the model.
        diameter (float): The diameter of the model.
        tolerance (float): The tolerance level for the model dimensions.
        amount (int?): The amount of material to use. Defaults to 0.
        stem (int?): The stem value for the model. Defaults to 1.
        twist (bool?): Whether to apply a twist to the model. Defaults to False.
        tneck (float?): The neck thickness. Defaults to 0.5.
        tthick (float?): The thickness for the neck. Defaults to 0.01.
        combination (str?): The combination type ('MF', 'F', 'M'). Defaults to 'MF'.
        base_gender (str?): The base gender for the model ('M' or 'F'). Defaults to 'M'.
        corner (bool?): Whether to apply corner adjustments. Defaults to False.

    Returns:
        None: This function does not return a value but modifies the 3D model
            directly.
    """

    if corner:
        if combination == "MF":
            base_gender = "M"
            combination = "f"
        elif combination == "F":
            base_gender = "F"
            combination = "f"
        elif combination == "M":
            base_gender = "M"
            combination = "m"

    bar(
        length,
        thick,
        diameter,
        tolerance,
        amount=amount,
        stem=stem,
        twist=twist,
        tneck=tneck,
        tthick=tthick,
        which=base_gender,
    )
    active_name("tmp")
    fingers(diameter, tolerance, amount=amount, stem=stem)
    if combination == "MF" or combination == "M" or combination == "m":
        make_active("fingers")
        move(y=thick / 2)
        duplicate()
        active_name("tmp")
        union("tmp")

    if combination == "M":
        make_active("fingers")
        mirror_y()
        active_name("tmp")
        union("tmp")

    if combination == "MF" or combination == "F" or combination == "f":
        make_active("receptacle")
        move(y=-thick / 2)
        duplicate()
        active_name("tmp")
        difference("tmp", "tmp")

    if combination == "F":
        make_active("receptacle")
        mirror_y()
        active_name("tmp")
        difference("tmp", "tmp")

    remove_multiple("receptacle")
    remove_multiple("fingers")

    rename("tmp", "t")
    make_active("t")


def curved_t(
    length,
    thick,
    radius,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    combination="MF",
    base_gender="M",
):
    """Create a curved shape based on specified parameters.

    This function generates a 3D curved shape using the provided dimensions
    and characteristics. It utilizes the `bar` and `arc` functions to create
    the desired geometry and applies transformations such as mirroring and
    union operations to achieve the final shape. The function also allows
    for customization based on the gender specification, which influences
    the shape's design.

    Args:
        length (float): The length of the bar.
        thick (float): The thickness of the bar.
        radius (float): The radius of the arc.
        diameter (float): The diameter used in arc creation.
        tolerance (float): The tolerance level for the shape.
        amount (int?): The amount parameter for the shape generation. Defaults to 0.
        stem (int?): The stem parameter for the shape generation. Defaults to 1.
        twist (bool?): A flag indicating whether to apply a twist to the shape. Defaults to
            False.
        tneck (float?): The neck thickness parameter. Defaults to 0.5.
        tthick (float?): The thickness parameter for the neck. Defaults to 0.01.
        combination (str?): The combination type for the shape. Defaults to 'MF'.
        base_gender (str?): The base gender for the shape design. Defaults to 'M'.

    Returns:
        None: This function does not return a value but modifies the 3D model in the
            environment.
    """

    bar(
        length,
        thick,
        diameter,
        tolerance,
        amount=amount,
        stem=stem,
        twist=twist,
        tneck=tneck,
        tthick=tthick,
        which=combination,
    )
    active_name("tmpbar")

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=3 * radius,
        Simple_length=thick,
        use_cyclic_u=True,
        edit_mode=False,
    )
    active_name("tmp_rect")

    if base_gender == "MF":
        arc(
            radius,
            thick,
            pi / 2,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="M",
        )
        move(-radius)
        active_name("tmp_arc")
        arc(
            radius,
            thick,
            pi / 2,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which="F",
        )
        move(radius)
        mirror_y()
        active_name("tmp_arc")
        union("tmp_arc")
        duplicate()
        mirror_x()
        union("tmp_arc")
        difference("tmp_", "tmp_arc")
    else:
        arc(
            radius,
            thick,
            pi / 2,
            diameter,
            tolerance,
            amount=amount,
            stem=stem,
            twist=twist,
            tneck=tneck,
            tthick=tthick,
            which=base_gender,
        )
        active_name("tmp_arc")
        difference("tmp_", "tmp_arc")
        if base_gender == "M":
            move(-radius)
        else:
            move(radius)
        duplicate()
        mirror_x()

    union("tmp")
    active_name("curved_t")


def mitre(
    length,
    thick,
    angle,
    angleb,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    tneck=0.5,
    tthick=0.01,
    which="MF",
):
    """Generate a mitre joint based on specified parameters.

    This function creates a 3D representation of a mitre joint using
    Blender's bpy.ops.curve.simple operations. It generates a base rectangle
    and cutout shapes, then constructs male and female sections of the joint
    based on the provided angles and dimensions. The function allows for
    customization of various parameters such as thickness, diameter,
    tolerance, and the number of fingers in the joint. The resulting joint
    can be either male, female, or a combination of both.

    Args:
        length (float): The total width of the segments including 2 * radius and thickness.
        thick (float): The thickness of the bar.
        angle (float): The angle of the female part.
        angleb (float): The angle of the male part.
        diameter (float): The diameter of the tool for joint creation.
        tolerance (float): Tolerance in the joint.
        amount (int?): Amount of fingers in the joint; 0 means auto-generate. Defaults to 0.
        stem (float?): Amount of radius the stem or neck of the joint will have. Defaults to 1.
        twist (bool?): Indicates if a twist lock addition is required. Defaults to False.
        tneck (float?): Percentage the twist neck will have compared to thickness. Defaults to
            0.5.
        tthick (float?): Thickness of the twist material. Defaults to 0.01.
        which (str?): Specifies which joint to generate ('M', 'F', 'MF'). Defaults to 'MF'.
    """

    # generate base rectangle
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, -thick / 2, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=length * 1.005 + 4 * thick,
        Simple_length=thick,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    active_name("tmprect")

    # generate cutout shapes
    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=4 * thick,
        Simple_length=6 * thick,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    move(x=2 * thick)
    rotate(angle)
    move(x=length / 2)
    active_name("tmpmitreright")

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=4 * thick,
        Simple_length=6 * thick,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    move(x=2 * thick)
    rotate(angleb)
    move(x=length / 2)
    mirror_x()
    active_name("tmpmitreleft")
    difference("tmp", "tmprect")
    make_active("tmprect")

    fingers(diameter, tolerance, amount, stem=stem)

    #  Generate male section and join to the base
    if which == "M" or which == "MF":
        make_active("fingers")
        duplicate()
        active_name("tmpfingers")
        rotate(angle - pi / 2)
        h = thick / cos(angle)
        h /= 2
        move(x=length / 2 + h * sin(angle), y=-thick / 2)
        if which == "M":
            rename("fingers", "tmpfingers")
            rotate(angleb - pi / 2)
            h = thick / cos(angleb)
            h /= 2
            move(x=length / 2 + h * sin(angleb), y=-thick / 2)
            mirror_x()

        union("tmp")
        active_name("tmprect")

    # Generate female section and join to base
    if which == "MF" or which == "F":
        make_active("receptacle")
        mirror_y()
        duplicate()
        active_name("tmpreceptacle")
        rotate(angleb - pi / 2)
        h = thick / cos(angleb)
        h /= 2
        move(x=length / 2 + h * sin(angleb), y=-thick / 2)
        mirror_x()
        if which == "F":
            rename("receptacle", "tmpreceptacle2")
            rotate(angle - pi / 2)
            h = thick / cos(angle)
            h /= 2
            move(x=length / 2 + h * sin(angle), y=-thick / 2)
        difference("tmp", "tmprect")

    remove_multiple("receptacle")
    remove_multiple("fingers")
    rename("tmprect", "mitre")


def open_curve(
    line,
    thick,
    diameter,
    tolerance,
    amount=0,
    stem=1,
    twist=False,
    t_neck=0.5,
    t_thick=0.01,
    twist_amount=1,
    which="MF",
    twist_keep=False,
):
    """Open a curve and add puzzle connectors with optional twist lock
    connectors.

    This function takes a shapely LineString and creates an open curve with
    specified parameters such as thickness, diameter, tolerance, and twist
    options. It generates puzzle connectors at the ends of the curve and can
    optionally add twist lock connectors along the curve. The function also
    handles the creation of the joint based on the provided parameters,
    ensuring that the resulting geometry meets the specified design
    requirements.

    Args:
        line (LineString): A shapely LineString representing the path of the curve.
        thick (float): The thickness of the bar used in the joint.
        diameter (float): The diameter of the tool for joint creation.
        tolerance (float): The tolerance in the joint.
        amount (int?): The number of fingers in the joint; 0 means auto-generate. Defaults to
            0.
        stem (float?): The amount of radius the stem or neck of the joint will have. Defaults
            to 1.
        twist (bool?): Whether to add twist lock connectors. Defaults to False.
        t_neck (float?): The percentage the twist neck will have compared to thickness. Defaults
            to 0.5.
        t_thick (float?): The thickness of the twist material. Defaults to 0.01.
        twist_amount (int?): The amount of twist distributed on the curve, not counting joint twists.
            Defaults to 1.
        which (str?): Specifies the type of joint; options include 'M', 'F', 'MF', 'MM', 'FF'.
            Defaults to 'MF'.
        twist_keep (bool?): Whether to keep the twist lock connectors. Defaults to False.

    Returns:
        None: This function does not return a value but modifies the geometry in the
            Blender context.
    """

    coords = list(line.coords)

    start_angle = joinery.angle(coords[0], coords[1]) + pi / 2
    end_angle = joinery.angle(coords[-1], coords[-2]) + pi / 2
    p_start = coords[0]
    p_end = coords[-1]

    print("Start Angle", start_angle)
    print("End Angle", end_angle)

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Rectangle",
        Simple_width=thick * 2,
        Simple_length=thick * 2,
        use_cyclic_u=True,
        edit_mode=False,
        shape="3D",
    )
    active_name("tmprect")
    move(y=thick)
    duplicate()
    rotate(start_angle)
    move(x=p_start[0], y=p_start[1])
    make_active("tmprect")
    rotate(end_angle)
    move(x=p_end[0], y=p_end[1])
    union("tmprect")
    dilated = line.buffer(thick / 2)  # expand shapely object to thickness
    shapely_to_curve("tmp_curve", dilated, 0.0)
    # truncate curve at both ends with the rectangles
    difference("tmp", "tmp_curve")

    fingers(diameter, tolerance, amount, stem=stem)
    make_active("fingers")
    rotate(end_angle)
    move(x=p_end[0], y=p_end[1])
    active_name("tmp_fingers")
    union("tmp_")
    active_name("tmp_curve")
    twist_male(
        "tmp_curve",
        thick,
        diameter,
        tolerance,
        twist,
        t_neck,
        t_thick,
        end_angle,
        x=p_end[0],
        y=p_end[1],
        twist_keep=twist_keep,
    )

    twist_female(
        "receptacle", thick, diameter, tolerance, twist, t_neck, t_thick, twist_keep=twist_keep
    )
    rename("receptacle", "tmp")
    rotate(start_angle + pi)
    move(x=p_start[0], y=p_start[1])
    difference("tmp", "tmp_curve")
    if twist_keep:
        make_active("twist_keep_f")
        rotate(start_angle + pi)
        move(x=p_start[0], y=p_start[1])

    if twist_amount > 0 and twist:
        twist_start = line.length / (twist_amount + 1)
        joinery.distributed_interlock(
            line,
            line.length,
            thick,
            t_thick,
            tolerance,
            twist_amount,
            tangent=pi / 2,
            fixed_angle=0,
            start=twist_start,
            end=twist_start,
            closed=False,
            type="TWIST",
            twist_percentage=t_neck,
        )
        if twist_keep:
            duplicate()
            active_name("twist_keep")
            join_multiple("twist_keep")
            make_active("interlock")

        active_name("tmp_twist")
        difference("tmp", "tmp_curve")
        active_name("puzzle_curve")


def tile(diameter, tolerance, tile_x_amount, tile_y_amount, stem=1):
    """Create a tile shape based on specified dimensions and parameters.

    This function calculates the dimensions of a tile based on the provided
    diameter and tolerance, as well as the number of tiles in the x and y
    directions. It constructs the tile shape by creating a base and adding
    features such as fingers for interlocking. The function also handles
    transformations such as moving, rotating, and performing boolean
    operations to achieve the desired tile geometry.

    Args:
        diameter (float): The diameter of the tile.
        tolerance (float): The tolerance to be applied to the tile dimensions.
        tile_x_amount (int): The number of tiles along the x-axis.
        tile_y_amount (int): The number of tiles along the y-axis.
        stem (int?): A parameter affecting the tile's features. Defaults to 1.

    Returns:
        None: This function does not return a value but modifies global state.
    """

    global DT
    diameter = diameter * DT
    width = ((tile_x_amount) * (4 + 2 * (stem - 1)) + 1) * diameter
    height = ((tile_y_amount) * (4 + 2 * (stem - 1)) + 1) * diameter

    print("Size:", width, height)
    fingers(diameter, tolerance, amount=tile_x_amount, stem=stem)
    add_rectangle(width, height)
    active_name("_base")

    make_active("fingers")
    active_name("_fingers")
    intersect("_")
    remove_multiple("_fingers")
    rename("intersection", "_fingers")
    move(y=height / 2)
    union("_")
    active_name("_base")
    remove_doubles()
    rename("receptacle", "_receptacle")
    move(y=-height / 2)
    difference("_", "_base")
    active_name("base")
    fingers(diameter, tolerance, amount=tile_y_amount, stem=stem)
    rename("base", "_base")
    remove_doubles()
    rename("fingers", "_fingers")
    rotate(pi / 2)
    move(x=-width / 2)
    union("_")
    active_name("_base")
    rename("receptacle", "_receptacle")
    rotate(pi / 2)
    move(x=width / 2)
    difference("_", "_base")
    active_name("tile_ " + str(tile_x_amount) + "_" + str(tile_y_amount))
