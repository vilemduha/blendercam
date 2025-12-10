"""Fabex 'log_ops.py' © 2012 Vilem Novak

Blender Operator definitions are in this file.
They mostly call the functions from 'utils.py'
"""

from os import listdir
from platform import system
from pathlib import Path
from subprocess import call

import bpy
from bpy.types import Operator

log_folder = str(Path(__file__).parent.parent / "logs")


class CamOpenLogFolder(Operator):
    """Open the CAM Log Folder"""

    bl_idname = "scene.cam_open_log_folder"
    bl_label = "Open Log Folder"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Opens the folder where CAM logs are stored.

        Args:
            context: The context in which the operation is executed.

        Returns:
            dict: A dictionary indicating the operation's completion status,
                specifically returning {'FINISHED'} upon successful execution.
        """

        # bpy.ops.file.external_operation(log_folder, operation="OPEN")
        if system() == "Linux":
            call(["xdg-open", log_folder])
        elif system() == "Darwin":
            call(["open", log_folder])
        else:
            from os import startfile

            startfile(log_folder)

        return {"FINISHED"}


class CamPurgeLogs(Operator):
    """Delete CAM Logs"""

    bl_idname = "scene.cam_purge_logs"
    bl_label = "Purge CAM Logs"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        """Execute the CAM log removal process.

        This function removes the files from the CAM logs folder

        Args:
            context: The context in which the function is executed.

        Returns:
            dict: A dictionary indicating the status of the operation,
                specifically {'FINISHED'} upon successful execution.
        """

        for file in listdir(log_folder):
            file_name = Path(log_folder) / file
            if not file_name == ".gitignore":
                Path.unlink(file_name)

        return {"FINISHED"}
