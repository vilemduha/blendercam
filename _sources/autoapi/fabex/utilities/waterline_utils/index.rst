fabex.utilities.waterline_utils
===============================

.. py:module:: fabex.utilities.waterline_utils


Functions
---------

.. autoapisummary::

   fabex.utilities.waterline_utils.oclWaterlineLayerHeights
   fabex.utilities.waterline_utils.oclGetWaterline


Module Contents
---------------

.. py:function:: oclWaterlineLayerHeights(operation)

   Generate a list of waterline layer heights for a given operation.

   This function calculates the heights of waterline layers based on the
   specified parameters of the operation. It starts from the maximum height
   and decrements by a specified step until it reaches the minimum height.
   The resulting list of heights can be used for further processing in
   operations that require layered depth information.

   :param operation: An object containing the properties `minz`,
                     `maxz`, and `stepdown` which define the
                     minimum height, maximum height, and step size
                     for layer generation, respectively.
   :type operation: object

   :returns: A list of waterline layer heights from maximum to minimum.
   :rtype: list


.. py:function:: oclGetWaterline(operation, chunks)
   :async:


   Generate waterline paths for a given machining operation.

   This function calculates the waterline paths based on the provided
   machining operation and its parameters. It determines the appropriate
   cutter type and dimensions, sets up the waterline object with the
   corresponding STL file, and processes each layer to generate the
   machining paths. The resulting paths are stored in the provided chunks
   list. The function also handles different cutter types, including end
   mills, ball nose cutters, and V-carve cutters.

   :param operation: An object representing the machining operation,
                     containing details such as cutter type, diameter, and minimum Z height.
   :type operation: Operation
   :param chunks: A list that will be populated with the generated
                  machining path chunks.
   :type chunks: list


