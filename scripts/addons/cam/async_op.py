import bpy
import sys

import types

@types.coroutine
def progress_async(text, n=None,value_type='%'):
    """function for reporting during the script, works for background operations in the header."""
    throw_exception=yield ('progress',{'text':text,'n':n,"value_type":value_type})
    if throw_exception is not None:
        raise throw_exception

class AsyncCancelledException(Exception):
    pass

class AsyncOperatorMixin:

    def __init__(self):
        self.timer=None
        self.coroutine=None
        self._is_cancelled=False

    def modal(self,context,event):
        if event.type == 'TIMER':
            try:
                if self.tick(context):
                    return {'RUNNING_MODAL'}
                else:
                    context.window_manager.event_timer_remove(self.timer)
                    bpy.context.workspace.status_text_set(None)
                    return {'FINISHED'}
            except Exception as e:
                context.window_manager.event_timer_remove(self.timer)
                bpy.context.workspace.status_text_set(None)
                self.report({'ERROR'},str(e))
                return {'FINISHED'}
        elif event.type == 'ESC':
            self._is_cancelled=True
            self.tick(context)
            context.window_manager.event_timer_remove(self.timer)
            bpy.context.workspace.status_text_set(None)
            return {'FINISHED'}
        if 'BLOCKING' in self.bl_options:
            return {'RUNNING_MODAL'}
        else:
            return {'PASS_THROUGH'}

    def show_progress(self,context,text, n,value_type):
        if n is not None:
            progress_text = f"{text}: {n:.2f}{value_type}"
        else:
            progress_text = f"{text}"
        bpy.context.workspace.status_text_set(progress_text + " (Press ESC to cancel)")
        sys.stdout.write(f"Progress: {progress_text}\n")
        sys.stdout.flush()

    def tick(self,context):
        if self.coroutine==None:
            self.coroutine=self.execute_async(context)
        try:
            if self._is_cancelled:
                (msg,args)=self.coroutine.send(AsyncCancelledException("Cancelled with ESC key"))
                raise StopIteration
            else:
                (msg,args)=self.coroutine.send(None)
            if msg=='progress':                
                self.show_progress(context,**args)
            else:
                sys.stdout.write(f"{msg},{args}")
            return True
        except StopIteration:
            return False

    def execute(self, context):
        if bpy.app.background:
            # running in background - don't run as modal,
            # otherwise tests all fail
            while self.tick(context)==True:
                pass
            return {'FINISHED'}
        else:
            self.timer=context.window_manager.event_timer_add(.001, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

class AsyncTestOperator(bpy.types.Operator,AsyncOperatorMixin):
    """test async operator"""
    bl_idname = "object.cam_async_test_operator"
    bl_label = "Test operator for async stuff"
    bl_options = {'REGISTER', 'UNDO','BLOCKING'}

    async def execute_async(self,context):
        for x in range(100):
            await progress_async("Async test:",x)

#bpy.utils.register_class(AsyncTestOperator) 