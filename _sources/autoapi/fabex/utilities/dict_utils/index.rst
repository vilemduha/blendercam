fabex.utilities.dict_utils
==========================

.. py:module:: fabex.utilities.dict_utils

.. autoapi-nested-parse::

   Fabex 'dict_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.dict_utils.dict_cleanup
   fabex.utilities.dict_utils.dict_remove


Module Contents
---------------

.. py:function:: dict_cleanup(ndict)

   Remove lonely points from a dictionary.

   This function iterates over the keys of the provided dictionary and
   removes any entries that contain one or fewer associated values. It
   continues to check for and remove "lonely" points until no more can be
   found. The process is repeated until all such entries are eliminated
   from the dictionary.

   :param ndict: A dictionary where keys are associated with lists of values.
   :type ndict: dict

   :returns:

             This function modifies the input dictionary in place and does not return
                 a value.
   :rtype: None


.. py:function:: dict_remove(dict, val)

   Remove a key and its associated values from a dictionary.

   This function takes a dictionary and a key (val) as input. It iterates
   through the list of values associated with the given key and removes the
   key from each of those values' lists. Finally, it removes the key itself
   from the dictionary.

   :param dict: A dictionary where the key is associated with a list of values.
   :type dict: dict
   :param val: The key to be removed from the dictionary and from the lists of its
               associated values.


