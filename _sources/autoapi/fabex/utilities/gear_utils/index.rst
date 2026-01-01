fabex.utilities.gear_utils
==========================

.. py:module:: fabex.utilities.gear_utils

.. autoapi-nested-parse::

   Fabex 'involute_gear.py' Ported by Alain Pelletier Jan 2022

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



Functions
---------

.. autoapisummary::

   fabex.utilities.gear_utils.gear_polar
   fabex.utilities.gear_utils.gear_iang
   fabex.utilities.gear_utils.gear_q7
   fabex.utilities.gear_utils.gear_q6
   fabex.utilities.gear_utils.gear
   fabex.utilities.gear_utils.rack


Module Contents
---------------

.. py:function:: gear_polar(r, theta)

   Convert gear_polar to Cartesian coordinates


.. py:function:: gear_iang(r1, r2)

   Unwind a string (x) Degrees to go from Radius r1 to r2


.. py:function:: gear_q7(f, r, b, r2, t, s)

   Radius a fraction (f) up the curved side of the Tooth


.. py:function:: gear_q6(b, s, t, d)

   Point at Radius (d) on the involute curve


.. py:function:: gear(mm_per_tooth=0.003, number_of_teeth=5, hole_diameter=0.003175, pressure_angle=0.3488, clearance=0.0, backlash=0.0, rim_size=0.0005, hub_diameter=0.006, spokes=4)

   Generate a 3D gear model based on specified parameters.

   This function creates a 3D representation of a gear using the provided
   parameters such as the circular pitch, number of teeth, hole diameter,
   pressure angle, clearance, backlash, rim size, hub diameter, and the
   number of spokes. The gear is constructed by calculating various radii
   and angles based on the input parameters and then using geometric
   operations to form the final shape. The resulting gear is named
   according to its specifications.

   :param mm_per_tooth: The circular pitch of the gear in millimeters (default is 0.003).
   :type mm_per_tooth: float
   :param number_of_teeth: The total number of teeth on the gear (default is 5).
   :type number_of_teeth: int
   :param hole_diameter: The diameter of the central hole in millimeters (default is 0.003175).
   :type hole_diameter: float
   :param pressure_angle: The angle that controls the shape of the tooth sides in radians (default
                          is 0.3488).
   :type pressure_angle: float
   :param clearance: The gap between the top of a tooth and the bottom of a valley on a
                     meshing gear in millimeters (default is 0.0).
   :type clearance: float
   :param backlash: The gap between two meshing teeth along the circumference of the pitch
                    circle in millimeters (default is 0.0).
   :type backlash: float
   :param rim_size: The size of the rim around the gear in millimeters (default is 0.0005).
   :type rim_size: float
   :param hub_diameter: The diameter of the hub in millimeters (default is 0.006).
   :type hub_diameter: float
   :param spokes: The number of spokes on the gear (default is 4).
   :type spokes: int

   :returns:

             This function does not return a value but modifies the Blender scene to
                 include the generated gear model.
   :rtype: None


.. py:function:: rack(mm_per_tooth=0.01, number_of_teeth=11, height=0.012, pressure_angle=0.3488, backlash=0.0, hole_diameter=0.003175, tooth_per_hole=4)

   Generate a rack gear profile based on specified parameters.

   This function creates a rack gear by calculating the geometry based on
   the provided parameters such as millimeters per tooth, number of teeth,
   height, pressure angle, backlash, hole diameter, and teeth per hole. It
   constructs the gear shape using the Shapely library and duplicates the
   tooth to create the full rack. If a hole diameter is specified, it also
   creates holes along the rack. The resulting gear is named based on the
   input parameters.

   :param mm_per_tooth: The distance in millimeters for each tooth. Default is 0.01.
   :type mm_per_tooth: float
   :param number_of_teeth: The total number of teeth on the rack. Default is 11.
   :type number_of_teeth: int
   :param height: The height of the rack. Default is 0.012.
   :type height: float
   :param pressure_angle: The pressure angle in radians. Default is 0.3488.
   :type pressure_angle: float
   :param backlash: The backlash distance in millimeters. Default is 0.0.
   :type backlash: float
   :param hole_diameter: The diameter of the holes in millimeters. Default is 0.003175.
   :type hole_diameter: float
   :param tooth_per_hole: The number of teeth per hole. Default is 4.
   :type tooth_per_hole: int


