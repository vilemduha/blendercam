fabex.operators.async_op
========================

.. py:module:: fabex.operators.async_op

.. autoapi-nested-parse::

   Fabex 'async_op.py'

   Functions and Classes to allow asynchronous updates.
   Used to report progress during path calculation.



Exceptions
----------

.. autoapisummary::

   fabex.operators.async_op.AsyncCancelledException


Classes
-------

.. autoapisummary::

   fabex.operators.async_op.AsyncOperatorMixin
   fabex.operators.async_op.AsyncTestOperator


Module Contents
---------------

.. py:exception:: AsyncCancelledException

   Bases: :py:obj:`Exception`


   Common base class for all non-exit exceptions.


.. py:class:: AsyncOperatorMixin(*args, **kwargs)

   .. py:attribute:: timer
      :value: None



   .. py:attribute:: coroutine
      :value: None



   .. py:attribute:: _is_cancelled
      :value: False



   .. py:method:: modal(context, event)

      Handle modal operations for a Blender event.

      This function processes events in a modal operator. It checks for
      specific event types, such as TIMER and ESC, and performs actions
      accordingly. If the event type is TIMER, it attempts to execute a tick
      function, managing the timer and status text in the Blender workspace.
      If an exception occurs during the tick execution, it handles the error
      gracefully by removing the timer and reporting the error. The function
      also allows for cancellation of the operation when the ESC key is
      pressed.

      :param context: The current Blender context.
      :type context: bpy.context
      :param event: The event being processed.
      :type event: bpy.types.Event



   .. py:method:: show_progress(context, text, n, value_type)

      Display the progress of a task in the workspace and console.

      This function updates the status text in the Blender workspace to show
      the current progress of a task. It formats the progress message based on
      the provided parameters and outputs it to both the Blender interface and
      the standard output. If the value of `n` is not None, it includes the
      formatted number and value type in the progress message; otherwise, it
      simply displays the provided text.

      :param context: The context in which the progress is displayed (typically
                      the Blender context).
      :param text: A message indicating the task being performed.
      :type text: str
      :param n: The current progress value to be displayed.
      :type n: float or None
      :param value_type: A string representing the type of value (e.g.,
                         percentage, units).
      :type value_type: str



   .. py:method:: tick(context)

      Execute a tick of the coroutine and handle its progress.

      This method checks if the coroutine is initialized; if not, it
      initializes it by calling `execute_async` with the provided context. It
      then attempts to send a signal to the coroutine to either continue its
      execution or handle cancellation. If the coroutine is cancelled, it
      raises a `StopIteration` exception. The method also processes messages
      from the coroutine, displaying progress or other messages as needed.

      :param context: The context in which the coroutine is executed.

      :returns:

                True if the tick was processed successfully, False if the coroutine has
                    completed.
      :rtype: bool

      :raises StopIteration: If the coroutine has completed its execution.
      :raises Exception: If an unexpected error occurs during the execution of the tick.



   .. py:method:: execute(context)

      Execute the modal operation based on the context.

      This function checks if the application is running in the background. If
      it is, it continuously ticks until the operation is complete. If not, it
      sets up a timer for the modal operation and adds the modal handler to
      the window manager, allowing the operation to run in a modal state.

      :param context: The context in which the operation is executed.
      :type context: bpy.types.Context

      :returns:

                A dictionary indicating the status of the operation, either
                    {'FINISHED'} if completed or {'RUNNING_MODAL'} if running in modal.
      :rtype: dict



.. py:class:: AsyncTestOperator(*args, **kwargs)

   Bases: :py:obj:`bpy.types.Operator`, :py:obj:`AsyncOperatorMixin`


   Test Async Operator


   .. py:attribute:: bl_idname
      :value: 'object.cam_async_test_operator'



   .. py:attribute:: bl_label
      :value: 'Test Operator for Async Stuff'



   .. py:attribute:: bl_options


   .. py:method:: execute_async(context)
      :async:


      Execute an asynchronous operation with a progress indicator.

      This function runs a loop 100 times, calling an asynchronous function to
      report progress for each iteration. It is designed to be used in an
      asynchronous context where the progress of a task needs to be tracked
      and reported.

      :param context: The context in which the asynchronous operation is executed.



