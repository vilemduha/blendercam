fabex.joinery
=============

.. py:module:: fabex.joinery

.. autoapi-nested-parse::

   Fabex 'joinery.py' © 2021 Alain Pelletier

   Functions to create various woodworking joints - mortise, finger etc.



Functions
---------

.. autoapisummary::

   fabex.joinery.finger_amount
   fabex.joinery.mortise
   fabex.joinery.interlock_groove
   fabex.joinery.interlock_twist
   fabex.joinery.twist_line
   fabex.joinery.twist_separator_slot
   fabex.joinery.interlock_twist_separator
   fabex.joinery.horizontal_finger
   fabex.joinery.vertical_finger
   fabex.joinery.finger_pair
   fabex.joinery.create_base_plate
   fabex.joinery.make_flex_pocket
   fabex.joinery.make_variable_flex_pocket
   fabex.joinery.create_flex_side
   fabex.joinery.angle
   fabex.joinery.angle_difference
   fabex.joinery.fixed_finger
   fabex.joinery.find_slope
   fabex.joinery.slope_array
   fabex.joinery.d_slope_array
   fabex.joinery.variable_finger
   fabex.joinery.single_interlock
   fabex.joinery.distributed_interlock


Module Contents
---------------

.. py:function:: finger_amount(space, size)

   Calculates the amount of fingers needed from the available space vs the size of the finger

   :param space: available distance to cover
   :type space: float
   :param size: size of the finger
   :type size: float


.. py:function:: mortise(length, thickness, finger_play, cx=0, cy=0, rotation=0)

   Generates a mortise of length, thickness and finger_play tolerance
   cx and cy are the center position and rotation is the angle

   :param length: length of the mortise
   :type length: float
   :param thickness: thickness of material
   :type thickness: float
   :param finger_play: tolerance for good fit
   :type finger_play: float
   :param cx: coordinate for x center of the finger
   :type cx: float
   :param cy: coordinate for y center of the finger
   :type cy: float
   :param rotation: angle of rotation
   :type rotation: float


.. py:function:: interlock_groove(length, thickness, finger_play, cx=0, cy=0, rotation=0)

   Generates an interlocking groove.

   :param length: Length of groove
   :type length: float
   :param thickness: thickness of groove
   :type thickness: float
   :param finger_play: tolerance for proper fit
   :type finger_play: float
   :param cx: center offset x
   :type cx: float
   :param cy: center offset y
   :type cy: float
   :param rotation: angle of rotation
   :type rotation: float


.. py:function:: interlock_twist(length, thickness, finger_play, cx=0, cy=0, rotation=0, percentage=0.5)

   Generates an interlocking twist.

   :param length: Length of groove
   :type length: float
   :param thickness: thickness of groove
   :type thickness: float
   :param finger_play: tolerance for proper fit
   :type finger_play: float
   :param cx: center offset x
   :type cx: float
   :param cy: center offset y
   :type cy: float
   :param rotation: angle of rotation
   :type rotation: float
   :param percentage: percentage amount the twist will take (between 0 and 1)
   :type percentage: float


.. py:function:: twist_line(length, thickness, finger_play, percentage, amount, distance, center=True)

   Generates a multiple interlocking twist.

   :param length: Length of groove
   :type length: float
   :param thickness: thickness of groove
   :type thickness: float
   :param finger_play: tolerance for proper fit
   :type finger_play: float
   :param percentage: percentage amount the twist will take (between 0 and 1)
   :type percentage: float
   :param amount: amount of twists generated
   :type amount: int
   :param distance: distance between twists
   :type distance: float
   :param center: center or not from origin
   :type center: bool


.. py:function:: twist_separator_slot(length, thickness, finger_play=5e-05, percentage=0.5)

   Generates a slot for interlocking twist separator.

   :param length: Length of slot
   :type length: float
   :param thickness: thickness of slot
   :type thickness: float
   :param finger_play: tolerance for proper fit
   :type finger_play: float
   :param percentage: percentage amount the twist will take (between 0 and 1)
   :type percentage: float


.. py:function:: interlock_twist_separator(length, thickness, amount, spacing, edge_distance, finger_play=5e-05, percentage=0.5, start='rounded', end='rounded')

   Generates a interlocking twist separator.

   :param length: Length of separator
   :type length: float
   :param thickness: thickness of separator
   :type thickness: float
   :param amount: quantity of separation grooves
   :type amount: int
   :param spacing: distance between slots
   :type spacing: float
   :param edge_distance: distance of the first slots close to the edge
   :type edge_distance: float
   :param finger_play: tolerance for proper fit
   :type finger_play: float
   :param percentage: percentage amount the twist will take (between 0 and 1)
   :type percentage: float
   :param start: type of start wanted (rounded, flat or other) not implemented
   :type start: string
   :param start: type of end wanted (rounded, flat or other) not implemented
   :type start: string


.. py:function:: horizontal_finger(length, thickness, finger_play, amount, center=True)

   Generates an interlocking horizontal finger pair _wfa and _wfb.

   _wfa is centered at 0,0
   _wfb is _wfa offset by one length

   :param length: Length of mortise
   :type length: float
   :param thickness: thickness of material
   :type thickness: float
   :param amount: quantity of fingers
   :type amount: int
   :param finger_play: tolerance for proper fit
   :type finger_play: float
   :param center: centered of not
   :type center: bool


.. py:function:: vertical_finger(length, thickness, finger_play, amount)

   Generates an interlocking horizontal finger pair _vfa and _vfb.

   _vfa is starts at 0,0
   _vfb is _vfa offset by one length

   :param length: Length of mortise
   :type length: float
   :param thickness: thickness of material
   :type thickness: float
   :param amount: quantity of fingers
   :type amount: int
   :param finger_play: tolerance for proper fit
   :type finger_play: float


.. py:function:: finger_pair(name, dx=0, dy=0)

   Creates a duplicate set of fingers.

   :param name: name of original finger
   :type name: str
   :param dx: x offset
   :type dx: float
   :param dy: y offset
   :type dy: float


.. py:function:: create_base_plate(height, width, depth)

   Creates blank plates for a box.

   :param height: height size for box
   :type height: float
   :param width: width size for box
   :type width: float
   :param depth: depth size for box
   :type depth: float


.. py:function:: make_flex_pocket(length, height, finger_thick, finger_width, pocket_width)

   creates pockets using mortise function for kerf bending

   :param length: Length of pocket
   :type length: float
   :param height: height of pocket
   :type height: float
   :param finger_thick: thickness of finger
   :type finger_thick: float
   :param finger_width: width of finger
   :type finger_width: float
   :param pocket_width: width of pocket
   :type pocket_width: float


.. py:function:: make_variable_flex_pocket(height, finger_thick, pocket_width, locations)

   creates pockets pocket using mortise function for kerf bending

   :param height: height of the side
   :type height: float
   :param finger_thick: thickness of the finger
   :type finger_thick: float
   :param pocket_width: width of pocket
   :type pocket_width: float
   :param locations: coordinates for pocket
   :type locations: tuple


.. py:function:: create_flex_side(length, height, finger_thick, top_bottom=False)

   crates a flex side for mortise on curve. Assumes the base fingers were created and exist

   :param length: length of curve
   :type length: float
   :param height: height of side
   :type height: float
   :param finger_thick: finger thickness or thickness of material
   :type finger_thick: float
   :param top_bottom: fingers on top and bottom if true, just on bottom if false
   :type top_bottom: bool


.. py:function:: angle(a, b)

   returns angle of a vector

   :param a: point a x,y coordinates
   :type a: tuple
   :param b: point b x,y coordinates
   :type b: tuple


.. py:function:: angle_difference(a, b, c)

   returns the difference between two lines with three points

   :param a: point a x,y coordinates
   :type a: tuple
   :param b: point b x,y coordinates
   :type b: tuple
   :param c: point c x,y coordinates
   :type c: tuple


.. py:function:: fixed_finger(loop, loop_length, finger_size, finger_thick, finger_tolerance, base=False)

   distributes mortises of a fixed distance.  Dynamically changes the finger tolerance with the angle differences

   :param loop: takes in a shapely shape
   :type loop: list of tuples
   :param loop_length: length of loop
   :type loop_length: float
   :param finger_size: size of the mortise
   :type finger_size: float
   :param finger_thick: thickness of the material
   :type finger_thick: float
   :param finger_tolerance: minimum finger tolerance
   :type finger_tolerance: float
   :param base: if base exists, it will join with it
   :type base: bool


.. py:function:: find_slope(p1, p2)

   returns slope of a vector

   :param p1: point 1 x,y coordinates
   :type p1: tuple
   :param p2: point 2 x,y coordinates
   :type p2: tuple


.. py:function:: slope_array(loop)

   Returns an array of slopes from loop coordinates.

   :param loop: list of coordinates for a curve
   :type loop: list of tuples


.. py:function:: d_slope_array(loop, resolution=0.001)

   Returns a double derivative array or slope of the slope

   :param loop: list of coordinates for a curve
   :type loop: list of tuples
   :param resolution: granular resolution of the array
   :type resolution: float


.. py:function:: variable_finger(loop, loop_length, min_finger, finger_size, finger_thick, finger_tolerance, adaptive, base=False, double_adaptive=False)

   Distributes mortises of a fixed distance. Dynamically changes the finger tolerance with the angle differences

   :param loop: takes in a shapely shape
   :type loop: list of tuples
   :param loop_length: length of loop
   :type loop_length: float
   :param finger_size: size of the mortise
   :type finger_size: float
   :param finger_thick: thickness of the material
   :type finger_thick: float
   :param min_finger: minimum finger size
   :type min_finger: float
   :param finger_tolerance: minimum finger tolerance
   :type finger_tolerance: float
   :param adaptive: angle threshold to reduce finger size
   :type adaptive: float
   :param base: join with base if true
   :type base: bool
   :param double_adaptive: uses double adaptive algorithm if true
   :type double_adaptive: bool


.. py:function:: single_interlock(finger_depth, finger_thick, finger_tolerance, x, y, groove_angle, type, amount=1, twist_percentage=0.5)

   Generates a single interlock at coodinate x,y.

   :param finger_depth: depth of finger
   :type finger_depth: float
   :param finger_thick: thickness of finger
   :type finger_thick: float
   :param finger_tolerance: tolerance for proper fit
   :type finger_tolerance: float
   :param x: offset x
   :type x: float
   :param y: offset y
   :type y: float
   :param groove_angle: angle of rotation
   :type groove_angle: float
   :param type: GROOVE, TWIST, PUZZLE are the valid choices
   :type type: str
   :param twist_percentage: percentage of thickness for twist (not used in puzzle or groove)


.. py:function:: distributed_interlock(loop, loop_length, finger_depth, finger_thick, finger_tolerance, finger_amount, tangent=0, fixed_angle=0, start=0.01, end=0.01, closed=True, type='GROOVE', twist_percentage=0.5)

   Distributes interlocking joints of a fixed amount.
    Dynamically changes the finger tolerance with the angle differences

   :param loop: coordinates curve
   :type loop: list of tuples
   :param loop_length: length of the curve
   :type loop_length: float
   :param finger_depth: depth of the mortise
   :type finger_depth: float
   :param finger_thick:
   :type finger_thick: float
   :param finger_tolerance: minimum finger tolerance
   :type finger_tolerance: float
   :param finger_amount: quantity of fingers
   :type finger_amount: int
   :param tangent:
   :type tangent: int
   :param fixed_angle: 0 will be variable, desired angle for the finger
   :type fixed_angle: float
   :param closed: False:open curve  -  True:closed curved
   :type closed: bool
   :param twist_percentage = portion of twist finger which is the stem:
   :type twist_percentage = portion of twist finger which is the stem: for twist joint only
   :param type: GROOVE, TWIST, PUZZLE are the valid choices
   :type type: str
   :param start: start distance from first point
   :type start: float
   :param end: end distance from last point
   :type end: float


