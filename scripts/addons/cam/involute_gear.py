"""Fabex 'involute_gear.py' Ported by Alain Pelletier Jan 2022

from:
Public Domain Parametric Involute Spur Gear (and involute helical gear and involute rack)
version 1.1
by Leemon Baird, 2011, Leemon@Leemon.com
http:www.thingiverse.com/thing:5505

This file is public domain.  Use it for any purpose, including commercial
applications.  Attribution would be nice, but is not required.  There is
no warranty of any kind, including its correctness, usefulness, or safety.

This is parameterized involute spur (or helical) gear.  It is much simpler and less powerful than
others on Thingiverse.  But it is public domain.  I implemented it from scratch from the
descriptions and equations on Wikipedia and the web, using Mathematica for calculations and testing,
and I now release it into the public domain.

    http:en.wikipedia.org/wiki/Involute_gear
    http:en.wikipedia.org/wiki/Gear
    http:en.wikipedia.org/wiki/List_of_gear_nomenclature
    http:gtrebaol.free.fr/doc/catia/spur_gear.html
    http:www.cs.cmu.edu/~rapidproto/mechanisms/chpt7.html

The module gear() gives an involute spur gear, with reasonable defaults for all the parameters.
Normally, you should just choose the first 4 parameters, and let the rest be default values.
The module gear() gives a gear in the XY plane, centered on the origin, with one tooth centered on
the positive Y axis.  The various functions below it take the same parameters, and return various
measurements for the gear.  The most important is pitch_radius, which tells how far apart to space
gears that are meshing, and adendum_radius, which gives the size of the region filled by the gear.
A gear has a "pitch circle", which is an invisible circle that cuts through the middle of each
tooth (though not the exact center). In order for two gears to mesh, their pitch circles should
just touch.  So the distance between their centers should be pitch_radius() for one, plus pitch_radius()
for the other, which gives the radii of their pitch circles.

In order for two gears to mesh, they must have the same mm_per_tooth and pressure_angle parameters.
mm_per_tooth gives the number of millimeters of arc around the pitch circle covered by one tooth and one
space between teeth.  The pitch angle controls how flat or bulged the sides of the teeth are.  Common
values include 14.5 degrees and 20 degrees, and occasionally 25.  Though I've seen 28 recommended for
plastic gears. Larger numbers bulge out more, giving stronger teeth, so 28 degrees is the default here.

The ratio of number_of_teeth for two meshing gears gives how many times one will make a full
revolution when the the other makes one full revolution.  If the two numbers are coprime (i.e.
are not both divisible by the same number greater than 1), then every tooth on one gear
will meet every tooth on the other, for more even wear.  So coprime numbers of teeth are good.

The module rack() gives a rack, which is a bar with teeth.  A rack can mesh with any
gear that has the same mm_per_tooth and pressure_angle.

Some terminology:
The outline of a gear is a smooth circle (the "pitch circle") which has mountains and valleys
added so it is toothed.  So there is an inner circle (the "root circle") that touches the
base of all the teeth, an outer circle that touches the tips of all the teeth,
and the invisible pitch circle in between them.  There is also a "base circle", which can be smaller than
all three of the others, which controls the shape of the teeth.  The side of each tooth lies on the path
that the end of a string would follow if it were wrapped tightly around the base circle, then slowly unwound.
That shape is an "involute", which gives this type of gear its name.

An involute spur gear, with reasonable defaults for all the parameters.
Normally, you should just choose the first 4 parameters, and let the rest be default values.
Meshing gears must match in mm_per_tooth, pressure_angle, and twist,
and be separated by the sum of their pitch radii, which can be found with pitch_radius().
"""

from math import (
    acos,
    cos,
    degrees,
    pi,
    sin,
    sqrt,
)

from shapely.geometry import Polygon

import bpy

from .utilities.shapely_utils import shapely_to_curve
from .utilities.simple_utils import (
    deselect,
    duplicate,
    rotate,
    join_multiple,
    active_name,
    union,
    remove_doubles,
    difference,
    add_rectangle,
    move,
)


# convert gear_polar to cartesian coordinates
def gear_polar(r, theta):
    return r * sin(theta), r * cos(theta)


# unwind a string this many degrees to go from radius r1 to radius r2
def gear_iang(r1, r2):
    return sqrt((r2 / r1) * (r2 / r1) - 1) - acos(r1 / r2)


#  radius a fraction f up the curved side of the tooth
def gear_q7(f, r, b, r2, t, s):
    return gear_q6(b, s, t, (1 - f) * max(b, r) + f * r2)


# point at radius d on the involute curve
def gear_q6(b, s, t, d):
    return gear_polar(d, s * (gear_iang(b, d) + t))


def gear(
    mm_per_tooth=0.003,
    number_of_teeth=5,
    hole_diameter=0.003175,
    pressure_angle=0.3488,
    clearance=0.0,
    backlash=0.0,
    rim_size=0.0005,
    hub_diameter=0.006,
    spokes=4,
):
    """Generate a 3D gear model based on specified parameters.

    This function creates a 3D representation of a gear using the provided
    parameters such as the circular pitch, number of teeth, hole diameter,
    pressure angle, clearance, backlash, rim size, hub diameter, and the
    number of spokes. The gear is constructed by calculating various radii
    and angles based on the input parameters and then using geometric
    operations to form the final shape. The resulting gear is named
    according to its specifications.

    Args:
        mm_per_tooth (float): The circular pitch of the gear in millimeters (default is 0.003).
        number_of_teeth (int): The total number of teeth on the gear (default is 5).
        hole_diameter (float): The diameter of the central hole in millimeters (default is 0.003175).
        pressure_angle (float): The angle that controls the shape of the tooth sides in radians (default
            is 0.3488).
        clearance (float): The gap between the top of a tooth and the bottom of a valley on a
            meshing gear in millimeters (default is 0.0).
        backlash (float): The gap between two meshing teeth along the circumference of the pitch
            circle in millimeters (default is 0.0).
        rim_size (float): The size of the rim around the gear in millimeters (default is 0.0005).
        hub_diameter (float): The diameter of the hub in millimeters (default is 0.006).
        spokes (int): The number of spokes on the gear (default is 4).

    Returns:
        None: This function does not return a value but modifies the Blender scene to
            include the generated gear model.
    """

    deselect()
    p = mm_per_tooth * number_of_teeth / pi / 2  # radius of pitch circle
    c = p + mm_per_tooth / pi - clearance  # radius of outer circle
    b = p * cos(pressure_angle)  # radius of base circle
    r = p - (c - p) - clearance  # radius of root circle
    t = mm_per_tooth / 2 - backlash / 2  # tooth thickness at pitch circle
    # angle to where involute meets base circle on each side of tooth
    k = -gear_iang(b, p) - t / 2 / p
    shapely_gear = Polygon(
        [
            (0, 0),
            gear_polar(r, k if r < b else -pi / number_of_teeth),
            gear_q7(0, r, b, c, k, 1),
            gear_q7(0.1, r, b, c, k, 1),
            gear_q7(0.2, r, b, c, k, 1),
            gear_q7(0.3, r, b, c, k, 1),
            gear_q7(0.4, r, b, c, k, 1),
            gear_q7(0.5, r, b, c, k, 1),
            gear_q7(0.6, r, b, c, k, 1),
            gear_q7(0.7, r, b, c, k, 1),
            gear_q7(0.8, r, b, c, k, 1),
            gear_q7(0.9, r, b, c, k, 1),
            gear_q7(1.0, r, b, c, k, 1),
            gear_q7(1.0, r, b, c, k, -1),
            gear_q7(0.9, r, b, c, k, -1),
            gear_q7(0.8, r, b, c, k, -1),
            gear_q7(0.7, r, b, c, k, -1),
            gear_q7(0.6, r, b, c, k, -1),
            gear_q7(0.5, r, b, c, k, -1),
            gear_q7(0.4, r, b, c, k, -1),
            gear_q7(0.3, r, b, c, k, -1),
            gear_q7(0.2, r, b, c, k, -1),
            gear_q7(0.1, r, b, c, k, -1),
            gear_q7(0.0, r, b, c, k, -1),
            gear_polar(r, -k if r < b else pi / number_of_teeth),
        ]
    )
    shapely_to_curve("tooth", shapely_gear, 0.0)
    i = number_of_teeth
    while i > 1:
        duplicate()
        rotate(2 * pi / number_of_teeth)
        i -= 1
    join_multiple("tooth")
    active_name("_teeth")

    bpy.ops.curve.simple(
        align="WORLD",
        location=(0, 0, 0),
        rotation=(0, 0, 0),
        Simple_Type="Circle",
        Simple_radius=r,
        shape="3D",
        use_cyclic_u=True,
        edit_mode=False,
    )
    active_name("_hub")
    union("_")
    active_name("_gear")
    remove_doubles()

    if spokes > 0:
        bpy.ops.curve.simple(
            align="WORLD",
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            Simple_Type="Circle",
            Simple_radius=r - rim_size,
            shape="3D",
            use_cyclic_u=True,
            edit_mode=False,
        )
        active_name("_hole")
        difference("_", "_gear")
        bpy.ops.curve.simple(
            align="WORLD",
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            Simple_Type="Circle",
            Simple_radius=hub_diameter / 2,
            shape="3D",
            use_cyclic_u=True,
            edit_mode=False,
        )
        active_name("_hub")
        bpy.ops.curve.simple(
            align="WORLD",
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            Simple_Type="Circle",
            Simple_radius=hole_diameter / 2,
            shape="3D",
            use_cyclic_u=True,
            edit_mode=False,
        )
        active_name("_hub_hole")
        difference("_hub", "_hub")

        join_multiple("_")

        add_rectangle(
            r - rim_size - ((hub_diameter - hole_diameter) / 4 + hole_diameter / 2),
            hub_diameter / 2,
            center_x=False,
        )
        move(x=(hub_diameter - hole_diameter) / 4 + hole_diameter / 2)
        active_name("_spoke")

        angle = 2 * pi / spokes
        while spokes > 0:
            duplicate()
            rotate(angle)
            spokes -= 1
        union("_spoke")
        remove_doubles()
        union("_")
    else:
        bpy.ops.curve.simple(
            align="WORLD",
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            Simple_Type="Circle",
            Simple_radius=hole_diameter,
            shape="3D",
            use_cyclic_u=True,
            edit_mode=False,
        )
        active_name("_hole")
        difference("_", "_gear")

    name = "gear-" + str(round(mm_per_tooth * 1000, 1))
    name += "mm-pitch-" + str(number_of_teeth)
    name += "teeth-PA-" + str(round(degrees(pressure_angle), 1))
    active_name(name)


def rack(
    mm_per_tooth=0.01,
    number_of_teeth=11,
    height=0.012,
    pressure_angle=0.3488,
    backlash=0.0,
    hole_diameter=0.003175,
    tooth_per_hole=4,
):
    """Generate a rack gear profile based on specified parameters.

    This function creates a rack gear by calculating the geometry based on
    the provided parameters such as millimeters per tooth, number of teeth,
    height, pressure angle, backlash, hole diameter, and teeth per hole. It
    constructs the gear shape using the Shapely library and duplicates the
    tooth to create the full rack. If a hole diameter is specified, it also
    creates holes along the rack. The resulting gear is named based on the
    input parameters.

    Args:
        mm_per_tooth (float): The distance in millimeters for each tooth. Default is 0.01.
        number_of_teeth (int): The total number of teeth on the rack. Default is 11.
        height (float): The height of the rack. Default is 0.012.
        pressure_angle (float): The pressure angle in radians. Default is 0.3488.
        backlash (float): The backlash distance in millimeters. Default is 0.0.
        hole_diameter (float): The diameter of the holes in millimeters. Default is 0.003175.
        tooth_per_hole (int): The number of teeth per hole. Default is 4.
    """

    deselect()
    mm_per_tooth *= 1000
    a = mm_per_tooth / pi  # addendum
    # tooth side is tilted so top/bottom corners move this amount
    t = a * sin(pressure_angle)
    a /= 1000
    mm_per_tooth /= 1000
    t /= 1000

    shapely_gear = Polygon(
        [
            (-mm_per_tooth * 2 / 4 * 1.001, a - height),
            (-mm_per_tooth * 2 / 4 * 1.001 - backlash, -a),
            (-mm_per_tooth * 1 / 4 + backlash - t, -a),
            (-mm_per_tooth * 1 / 4 + backlash + t, a),
            (mm_per_tooth * 1 / 4 - backlash - t, a),
            (mm_per_tooth * 1 / 4 - backlash + t, -a),
            (mm_per_tooth * 2 / 4 * 1.001 + backlash, -a),
            (mm_per_tooth * 2 / 4 * 1.001, a - height),
        ]
    )

    shapely_to_curve("_tooth", shapely_gear, 0.0)
    i = number_of_teeth
    while i > 1:
        duplicate(x=mm_per_tooth)
        i -= 1
    union("_tooth")
    move(y=height / 2)
    if hole_diameter > 0:
        bpy.ops.curve.simple(
            align="WORLD",
            location=(mm_per_tooth / 2, 0, 0),
            rotation=(0, 0, 0),
            Simple_Type="Circle",
            Simple_radius=hole_diameter / 2,
            shape="3D",
            use_cyclic_u=True,
            edit_mode=False,
        )
        active_name("_hole")
        distance = (number_of_teeth - 1) * mm_per_tooth
        while distance > tooth_per_hole * mm_per_tooth:
            duplicate(x=tooth_per_hole * mm_per_tooth)
            distance -= tooth_per_hole * mm_per_tooth
        difference("_", "_tooth")

    name = "rack-" + str(round(mm_per_tooth * 1000, 1))
    name += "-PA-" + str(round(degrees(pressure_angle), 1))
    active_name(name)
