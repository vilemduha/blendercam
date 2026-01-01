fabex.strategies.cutout
=======================

.. py:module:: fabex.strategies.cutout


Functions
---------

.. autoapisummary::

   fabex.strategies.cutout.cutout


Module Contents
---------------

.. py:function:: cutout(o)
   :async:


   Perform a cutout operation based on the provided parameters.

   This function calculates the necessary cutter offset based on the cutter
   type and its parameters. It processes a list of objects to determine how
   to cut them based on their geometry and the specified cutting type. The
   function handles different cutter types such as 'VCARVE', 'CYLCONE',
   'BALLCONE', and 'BALLNOSE', applying specific calculations for each. It
   also manages the layering and movement strategies for the cutting
   operation, including options for lead-ins, ramps, and bridges.

   :param o: An object containing parameters for the cutout operation,
             including cutter type, diameter, depth, and other settings.
   :type o: object

   :returns:

             This function does not return a value but performs operations
                 on the provided object.
   :rtype: None


