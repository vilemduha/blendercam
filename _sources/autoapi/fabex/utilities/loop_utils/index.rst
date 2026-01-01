fabex.utilities.loop_utils
==========================

.. py:module:: fabex.utilities.loop_utils

.. autoapi-nested-parse::

   Fabex 'loop_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.loop_utils.add_loop
   fabex.utilities.loop_utils.cut_loops


Module Contents
---------------

.. py:function:: add_loop(parentloop, start, end)

   Add a loop to a parent loop structure.

   This function recursively checks if the specified start and end values
   can be added as a new loop to the parent loop. If an existing loop
   encompasses the new loop, it will call itself on that loop. If no such
   loop exists, it appends the new loop defined by the start and end values
   to the parent loop's list of loops.

   :param parentloop: A list representing the parent loop, where the
                      third element is a list of child loops.
   :type parentloop: list
   :param start: The starting value of the new loop to be added.
   :type start: int
   :param end: The ending value of the new loop to be added.
   :type end: int

   :returns:

             This function modifies the parentloop in place and does not
                 return a value.
   :rtype: None


.. py:function:: cut_loops(csource, parentloop, loops)

   Cut loops from a source code segment.

   This function takes a source code segment and a parent loop defined by
   its start and end indices, along with a list of nested loops. It creates
   a copy of the source code segment and removes the specified nested loops
   from it. The modified segment is then appended to the provided list of
   loops. The function also recursively processes any nested loops found
   within the parent loop.

   :param csource: The source code from which loops will be cut.
   :type csource: str
   :param parentloop: A tuple containing the start index, end index, and a list of nested
                      loops.
                      The list of nested loops should contain tuples with start and end
                      indices for each loop.
   :type parentloop: tuple
   :param loops: A list that will be populated with the modified source code segments
                 after
                 removing the specified loops.
   :type loops: list

   :returns:

             This function modifies the `loops` list in place and does not return a
                 value.
   :rtype: None


