fabex.utilities.thread_utils
============================

.. py:module:: fabex.utilities.thread_utils

.. autoapi-nested-parse::

   Fabex 'thread_utils.py' © 2012 Vilem Novak

   They mostly call the functions from 'utils.py'



Classes
-------

.. autoapisummary::

   fabex.utilities.thread_utils.threadCom


Functions
---------

.. autoapisummary::

   fabex.utilities.thread_utils.thread_read
   fabex.utilities.thread_utils.timer_update


Module Contents
---------------

.. py:class:: threadCom(o, proc)

   .. py:attribute:: opname


   .. py:attribute:: out_text
      :value: ''



   .. py:attribute:: proc


   .. py:attribute:: lasttext
      :value: ''



.. py:function:: thread_read(tcom)

   Reads the standard output of a background process in a non-blocking
   manner.

   This function reads a line from the standard output of a background
   process associated with the provided `tcom` object. It searches for a
   specific substring that indicates progress information, and if found,
   extracts that information and assigns it to the `outtext` attribute of
   the `tcom` object. This allows for real-time monitoring of the
   background process's output without blocking the main thread.

   :param tcom: An object that has a `proc` attribute with a `stdout`
                stream from which to read the output.
   :type tcom: object

   :returns:

             This function does not return a value; it modifies the `tcom`
                 object in place.
   :rtype: None


.. py:function:: timer_update(context)

   Monitor background processes related to CAM path calculations.

   This function checks the status of background processes that are
   responsible for calculating CAM paths. It retrieves the current
   processes and monitors their state. If a process has finished, it
   updates the corresponding CAM operation and reloads the necessary
   paths. If the process is still running, it restarts the associated
   thread to continue monitoring.

   :param context: The context in which the function is called, typically
                   containing information about the current scene and operations.


