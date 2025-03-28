"""Fabex 'async_op.py'

Functions and Classes to allow asynchronous updates.
Used to report progress during path calculation.
"""

import sys

import bpy

from ..utilities.async_utils import progress_async


class AsyncCancelledException(Exception):
    pass


class AsyncOperatorMixin:
    def __init__(self, *args, **kwargs):
        self.timer = None
        self.coroutine = None
        self._is_cancelled = False

    def modal(self, context, event):
        """Handle modal operations for a Blender event.

        This function processes events in a modal operator. It checks for
        specific event types, such as TIMER and ESC, and performs actions
        accordingly. If the event type is TIMER, it attempts to execute a tick
        function, managing the timer and status text in the Blender workspace.
        If an exception occurs during the tick execution, it handles the error
        gracefully by removing the timer and reporting the error. The function
        also allows for cancellation of the operation when the ESC key is
        pressed.

        Args:
            context (bpy.context): The current Blender context.
            event (bpy.types.Event): The event being processed.
        """

        if bpy.app.background:
            return {"PASS_THROUGH"}

        if event.type == "TIMER":
            try:
                if self.tick(context):
                    return {"RUNNING_MODAL"}
                else:
                    context.window_manager.event_timer_remove(self.timer)
                    bpy.context.workspace.status_text_set(None)
                    context.window_manager.progress = 0
                    return {"FINISHED"}
            except Exception as e:
                context.window_manager.event_timer_remove(self.timer)
                bpy.context.workspace.status_text_set(None)
                self.report({"ERROR"}, str(e))
                return {"FINISHED"}
        elif event.type == "ESC":
            self._is_cancelled = True
            self.tick(context)
            context.window_manager.event_timer_remove(self.timer)
            bpy.context.workspace.status_text_set(None)
            return {"FINISHED"}
        if "BLOCKING" in self.bl_options:
            return {"RUNNING_MODAL"}
        else:
            return {"PASS_THROUGH"}

    def show_progress(self, context, text, n, value_type):
        """Display the progress of a task in the workspace and console.

        This function updates the status text in the Blender workspace to show
        the current progress of a task. It formats the progress message based on
        the provided parameters and outputs it to both the Blender interface and
        the standard output. If the value of `n` is not None, it includes the
        formatted number and value type in the progress message; otherwise, it
        simply displays the provided text.

        Args:
            context: The context in which the progress is displayed (typically
                the Blender context).
            text (str): A message indicating the task being performed.
            n (float or None): The current progress value to be displayed.
            value_type (str): A string representing the type of value (e.g.,
                percentage, units).
        """

        if n is not None:
            progress_text = f"{text}: {n:.2f}{value_type}"
            context.window_manager.progress = n * 0.01
            [a.tag_redraw() for a in context.screen.areas if a.type == "VIEW_3D"]
        else:
            progress_text = f"{text}"
        bpy.context.workspace.status_text_set(progress_text + " (Press ESC to cancel)")
        sys.stdout.write(f"Progress: {progress_text}\n")
        sys.stdout.flush()

    def tick(self, context):
        """Execute a tick of the coroutine and handle its progress.

        This method checks if the coroutine is initialized; if not, it
        initializes it by calling `execute_async` with the provided context. It
        then attempts to send a signal to the coroutine to either continue its
        execution or handle cancellation. If the coroutine is cancelled, it
        raises a `StopIteration` exception. The method also processes messages
        from the coroutine, displaying progress or other messages as needed.

        Args:
            context: The context in which the coroutine is executed.

        Returns:
            bool: True if the tick was processed successfully, False if the coroutine has
                completed.

        Raises:
            StopIteration: If the coroutine has completed its execution.
            Exception: If an unexpected error occurs during the execution of the tick.
        """

        if self.coroutine == None:
            self.coroutine = self.execute_async(context)
        try:
            if self._is_cancelled:
                (msg, args) = self.coroutine.send(AsyncCancelledException("Cancelled with ESC Key"))
                raise StopIteration
            else:
                (msg, args) = self.coroutine.send(None)
            if msg == "Progress:":
                self.show_progress(context, **args)
            else:
                sys.stdout.write(f"{msg},{args}")
            return True
        except StopIteration:
            return False
        except Exception as e:
            print("Exception Thrown in Tick:", e)

    def execute(self, context):
        """Execute the modal operation based on the context.

        This function checks if the application is running in the background. If
        it is, it continuously ticks until the operation is complete. If not, it
        sets up a timer for the modal operation and adds the modal handler to
        the window manager, allowing the operation to run in a modal state.

        Args:
            context (bpy.types.Context): The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the status of the operation, either
                {'FINISHED'} if completed or {'RUNNING_MODAL'} if running in modal.
        """

        if bpy.app.background:
            # running in background - don't run as modal,
            # otherwise tests all fail
            while self.tick(context) == True:
                pass
            return {"FINISHED"}
        else:
            self.timer = context.window_manager.event_timer_add(0.001, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}


class AsyncTestOperator(bpy.types.Operator, AsyncOperatorMixin):
    """Test Async Operator"""

    bl_idname = "object.cam_async_test_operator"
    bl_label = "Test Operator for Async Stuff"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    async def execute_async(self, context):
        """Execute an asynchronous operation with a progress indicator.

        This function runs a loop 100 times, calling an asynchronous function to
        report progress for each iteration. It is designed to be used in an
        asynchronous context where the progress of a task needs to be tracked
        and reported.

        Args:
            context: The context in which the asynchronous operation is executed.
        """

        for x in range(100):
            await progress_async("Async test:", x)


# bpy.utils.register_class(AsyncTestOperator)
