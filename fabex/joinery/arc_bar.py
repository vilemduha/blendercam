from math import (
    degrees,
    pi,
)


import bpy

from .finger import fingers
from .interlock_twist import (
    twist_female,
    twist_male,
)

from ..constants import DT  # Bit Diameter Tolerance

from ..utilities.logging_utils import log
from ..utilities.simple_utils import (
    duplicate,
    mirror_x,
    mirror_y,
    union,
    rename,
    difference,
    active_name,
    move,
    rotate,
    make_active,
    remove_multiple,
    select_multiple,
)


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
        twist_line(thick, tthick, tolerance, tneck, twist_line_amount, width)
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

    #  Use bit diameter tolerance (DT) for diameter of finger creation

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
    log.info("Generating Arc")
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
        twist_line(thick, tthick, tolerance, tneck, twist_line_amount, length)
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
