fabex.utilities.async_utils
===========================

.. py:module:: fabex.utilities.async_utils

.. autoapi-nested-parse::

   Fabex 'async_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.async_utils.progress_async


Module Contents
---------------

.. py:function:: progress_async(text, n=None, value_type='%')

   Report progress during script execution for background operations.

   This function is designed to provide progress updates while a script is
   running, particularly for background operations. It yields a dictionary
   containing the progress information, which includes the text description
   of the progress, an optional numeric value, and the type of value being
   reported. If an exception is thrown during the operation, it will be
   raised for handling.

   :param text: A message indicating the current progress.
   :type text: str
   :param n: An optional numeric value representing the progress.
   :type n: optional
   :param value_type: A string indicating the type of value being reported (default is '%').
   :type value_type: str?

   :raises Exception: If an exception is thrown during the operation.


