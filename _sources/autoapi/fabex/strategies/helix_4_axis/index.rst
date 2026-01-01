fabex.strategies.helix_4_axis
=============================

.. py:module:: fabex.strategies.helix_4_axis

.. autoapi-nested-parse::

   Fabex 'pattern.py' © 2012 Vilem Novak

   Functions to read CAM path patterns and return CAM path chunks.



Functions
---------

.. autoapisummary::

   fabex.strategies.helix_4_axis.helix_four_axis


Module Contents
---------------

.. py:function:: helix_four_axis(o)
   :async:


   Generate path patterns for a specified operation along a rotary axis.

   This function constructs a series of path chunks based on the provided
   operation's parameters, including the rotary axis, strategy, and
   dimensions. It calculates the necessary angles and positions for the
   cutter based on the specified strategy (PARALLELR, PARALLEL, or HELIX)
   and generates the corresponding path chunks for machining operations.

   :param operation: An object containing parameters for the machining operation,
                     including min and max coordinates, rotary axis configuration,
                     distance settings, and movement strategy.
   :type operation: object

   :returns: A list of path chunks generated for the specified operation.
   :rtype: list


