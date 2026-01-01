fabex.joinery.flex
==================

.. py:module:: fabex.joinery.flex


Functions
---------

.. autoapisummary::

   fabex.joinery.flex.create_base_plate
   fabex.joinery.flex.make_flex_pocket
   fabex.joinery.flex.make_variable_flex_pocket
   fabex.joinery.flex.create_flex_side


Module Contents
---------------

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


