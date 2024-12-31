"""Fabex 'thread_utils.py' © 2012 Vilem Novak

They mostly call the functions from 'utils.py'
"""
import threading

import bpy

from ..utilities.operation_utils import reload_paths


class threadCom:  # object passed to threads to read background process stdout info
    def __init__(self, o, proc):
        self.opname = o.name
        self.out_text = ""
        self.proc = proc
        self.lasttext = ""


def thread_read(tcom):
    """Reads the standard output of a background process in a non-blocking
    manner.

    This function reads a line from the standard output of a background
    process associated with the provided `tcom` object. It searches for a
    specific substring that indicates progress information, and if found,
    extracts that information and assigns it to the `outtext` attribute of
    the `tcom` object. This allows for real-time monitoring of the
    background process's output without blocking the main thread.

    Args:
        tcom (object): An object that has a `proc` attribute with a `stdout`
            stream from which to read the output.

    Returns:
        None: This function does not return a value; it modifies the `tcom`
            object in place.
    """
    inline = tcom.proc.stdout.readline()
    inline = str(inline)
    s = inline.find("progress{")
    if s > -1:
        e = inline.find("}")
        tcom.out_text = inline[s + 9 : e]


@bpy.app.handlers.persistent
def timer_update(context):
    """Monitor background processes related to camera path calculations.

    This function checks the status of background processes that are
    responsible for calculating camera paths. It retrieves the current
    processes and monitors their state. If a process has finished, it
    updates the corresponding camera operation and reloads the necessary
    paths. If the process is still running, it restarts the associated
    thread to continue monitoring.

    Args:
        context: The context in which the function is called, typically
            containing information about the current scene and operations.
    """
    text = ""
    s = bpy.context.scene
    if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, "cam_processes"):
        processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
        for p in processes:
            # proc=p[1].proc
            readthread = p[0]
            tcom = p[1]
            if not readthread.is_alive():
                readthread.join()
                # readthread.
                tcom.lasttext = tcom.out_text
                if tcom.out_text != "":
                    print(tcom.opname, tcom.out_text)
                    tcom.out_text = ""

                if "finished" in tcom.lasttext:
                    processes.remove(p)

                    o = s.cam_operations[tcom.opname]
                    o.computing = False
                    reload_paths(o)
                    update_z_buffer_image_tag = False
                    update_offset_image_tag = False
                else:
                    readthread = threading.Thread(target=thread_read, args=([tcom]), daemon=True)
                    readthread.start()
                    p[0] = readthread
            o = s.cam_operations[tcom.opname]  # changes
            o.out_text = tcom.lasttext  # changes
