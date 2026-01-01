fabex.joinery.finger
====================

.. py:module:: fabex.joinery.finger


Functions
---------

.. autoapisummary::

   fabex.joinery.finger.finger
   fabex.joinery.finger.fingers
   fabex.joinery.finger.finger_amount
   fabex.joinery.finger.finger_pair
   fabex.joinery.finger.horizontal_finger
   fabex.joinery.finger.vertical_finger
   fabex.joinery.finger.fixed_finger
   fabex.joinery.finger.variable_finger


Module Contents
---------------

.. py:function:: finger(diameter, stem=2)

   Create a joint shape based on the specified diameter and stem.

   This function generates a 3D joint shape using Blender's curve
   operations. It calculates the dimensions of a rectangle and an ellipse
   based on the provided diameter and stem parameters. The function then
   creates these shapes, duplicates and mirrors them, and performs boolean
   operations to form the final joint shape. The resulting object is named
   and cleaned up to ensure no overlapping vertices remain.

   :param diameter: The diameter of the tool for joint creation.
   :type diameter: float
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 2.
   :type stem: float?

   :returns: This function does not return any value.
   :rtype: None


.. py:function:: fingers(diameter, inside, amount=1, stem=1)

   Create a specified number of fingers for a joint tool.

   This function generates a set of fingers based on the provided diameter
   and tolerance values. It calculates the necessary translations for
   positioning the fingers and duplicates them if more than one is
   required. Additionally, it creates a receptacle using a silhouette
   offset from the fingers, allowing for precise joint creation.

   :param diameter: The diameter of the tool used for joint creation.
   :type diameter: float
   :param inside: The tolerance in the joint receptacle.
   :type inside: float
   :param amount: The number of fingers to create. Defaults to 1.
   :type amount: int?
   :param stem: The amount of radius the stem or neck of the joint will have. Defaults
                to 1.
   :type stem: float?


.. py:function:: finger_amount(space, size)

   Calculates the amount of fingers needed from the available space vs the size of the finger

   :param space: available distance to cover
   :type space: float
   :param size: size of the finger
   :type size: float


.. py:function:: finger_pair(name, dx=0, dy=0)

   Creates a duplicate set of fingers.

   :param name: name of original finger
   :type name: str
   :param dx: x offset
   :type dx: float
   :param dy: y offset
   :type dy: float


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


