fabex.joinery.interlock_twist
=============================

.. py:module:: fabex.joinery.interlock_twist


Functions
---------

.. autoapisummary::

   fabex.joinery.interlock_twist.interlock_groove
   fabex.joinery.interlock_twist.interlock_twist
   fabex.joinery.interlock_twist.twist_line
   fabex.joinery.interlock_twist.twist_separator_slot
   fabex.joinery.interlock_twist.interlock_twist_separator
   fabex.joinery.interlock_twist.single_interlock
   fabex.joinery.interlock_twist.distributed_interlock
   fabex.joinery.interlock_twist.twist_female
   fabex.joinery.interlock_twist.twist_male


Module Contents
---------------

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


.. py:function:: twist_female(name, length, diameter, tolerance, twist, tneck, tthick, twist_keep=False)

   Add a twist lock to a receptacle.

   This function modifies the receptacle by adding a twist lock feature if
   the `twist` parameter is set to True. It performs several operations
   including interlocking the twist, rotating the object, and moving it to
   the correct position. If `twist_keep` is True, it duplicates the twist
   lock for further modifications. The function utilizes parameters such as
   length, diameter, tolerance, and thickness to accurately create the
   twist lock.

   :param name: The name of the receptacle to be modified.
   :type name: str
   :param length: The length of the receptacle.
   :type length: float
   :param diameter: The diameter of the receptacle.
   :type diameter: float
   :param tolerance: The tolerance value for the twist lock.
   :type tolerance: float
   :param twist: A flag indicating whether to add a twist lock.
   :type twist: bool
   :param tneck: The neck thickness for the twist lock.
   :type tneck: float
   :param tthick: The thickness of the twist lock.
   :type tthick: float
   :param twist_keep: A flag indicating whether to keep the twist
                      lock after duplication. Defaults to False.
   :type twist_keep: bool?


.. py:function:: twist_male(name, length, diameter, tolerance, twist, tneck, tthick, angle, twist_keep=False, x=0, y=0)

   Add a twist lock to a male connector.

   This function modifies the geometry of a male connector by adding a
   twist lock feature. It utilizes various parameters to determine the
   dimensions and positioning of the twist lock. If the `twist_keep`
   parameter is set to True, it duplicates the twist lock for further
   modifications. The function also allows for adjustments in position
   through the `x` and `y` parameters.

   :param name: The name of the connector to be modified.
   :type name: str
   :param length: The length of the connector.
   :type length: float
   :param diameter: The diameter of the connector.
   :type diameter: float
   :param tolerance: The tolerance level for the twist lock.
   :type tolerance: float
   :param twist: A flag indicating whether to add a twist lock.
   :type twist: bool
   :param tneck: The neck thickness for the twist lock.
   :type tneck: float
   :param tthick: The thickness of the twist lock.
   :type tthick: float
   :param angle: The angle at which to rotate the twist lock.
   :type angle: float
   :param twist_keep: A flag indicating whether to keep the twist lock duplicate. Defaults to
                      False.
   :type twist_keep: bool?
   :param x: The x-coordinate for positioning. Defaults to 0.
   :type x: float?
   :param y: The y-coordinate for positioning. Defaults to 0.
   :type y: float?

   :returns:

             This function modifies the state of the connector but does not return a
                 value.
   :rtype: None


