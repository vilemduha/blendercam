fabex.strategies.pocket
=======================

.. py:module:: fabex.strategies.pocket


Functions
---------

.. autoapisummary::

   fabex.strategies.pocket.pocket


Module Contents
---------------

.. py:function:: pocket(o)
   :async:


   Perform pocketing operation based on the provided parameters.

   This function executes a pocketing operation using the specified
   parameters from the object `o`. It calculates the cutter offset based on
   the cutter type and depth, processes curves, and generates the necessary
   chunks for the pocketing operation. The function also handles various
   movement types and optimizations, including helix entry and retract
   movements.

   :param o: An object containing parameters for the pocketing
   :type o: object

   :returns: The function modifies the scene and generates geometry
             based on the pocketing operation.
   :rtype: None


