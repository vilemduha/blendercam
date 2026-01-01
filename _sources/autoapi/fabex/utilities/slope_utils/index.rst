fabex.utilities.slope_utils
===========================

.. py:module:: fabex.utilities.slope_utils


Functions
---------

.. autoapisummary::

   fabex.utilities.slope_utils.find_slope
   fabex.utilities.slope_utils.slope_array
   fabex.utilities.slope_utils.d_slope_array


Module Contents
---------------

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


