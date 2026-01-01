fabex.strategies.curve_to_path
==============================

.. py:module:: fabex.strategies.curve_to_path


Functions
---------

.. autoapisummary::

   fabex.strategies.curve_to_path.curve


Module Contents
---------------

.. py:function:: curve(o)
   :async:


   Process and convert curve objects into mesh chunks.

   This function takes an operation object and processes the curves
   contained within it. It first checks if all objects are curves; if not,
   it raises an exception. The function then converts the curves into
   chunks, sorts them, and refines them. If layers are to be used, it
   applies layer information to the chunks, adjusting their Z-offsets
   accordingly. Finally, it converts the processed chunks into a mesh.

   :param o: An object containing operation parameters, including a list of
             objects, flags for layer usage, and movement constraints.
   :type o: Operation

   :returns:

             This function does not return a value; it performs operations on the
                 input.
   :rtype: None

   :raises CamException: If not all objects in the operation are curves.


