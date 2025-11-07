import sys
import platform

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty


class Fabex_Compatibility_Panel(Operator):
    bl_idname = "fabex.compatibility"
    bl_label = ""

    os = platform.uname()[0]
    architecture = platform.uname()[4]
    python_version = sys.version.split(" (")[0]
    python_executable = sys.executable
    correct_python_version = "3.11.13"

    string_1 = f"""Hello and welcome to Fabex!
This popup will check your system for compatibility and assist with issues in the installation process."""

    string_2 = f"""Fabex officially supports Blender 4.2+ using Python {correct_python_version}.
We recommend downloading Blender from blender.org so it comes with the correct version of Python."""

    string_3 = f"""Linux users may install Blender with a Package Manager then find that Fabex will not install / work correctly.
apt, dnf, pacman, zypper etc. will provide copies of Blender that use your system's Python install.
If your Python version is not ⚠️⚠️⚠️ EXACTLY {correct_python_version} ⚠️⚠️⚠️ then Fabex will not install / work correctly.
    """

    string_4 = f"""{'OS:':>19} {os}
Architecture: {architecture}
{'Blender:':>16} {bpy.app.version_string}
{'Python:':>16} {python_version}
{'Location:':>15} {python_executable}"""

    compatible = python_version == correct_python_version

    title: StringProperty(default="Fabex Compatibility Check")

    text_1: StringProperty(default=string_1)

    text_2: StringProperty(default=string_2)

    text_3: StringProperty(default=string_3)

    text_4: StringProperty(default=string_4)

    def execute(self, context):
        print(self.text_1)
        return {"FINISHED"}

    def invoke(self, context, event):
        window = context.window
        wm = context.window_manager

        width = window.width
        height = window.height
        popup_width = 720
        v_offset = 100

        x = int(width / 2 + popup_width / 2)
        y = int(height / 2 + v_offset)
        context.window.cursor_warp(x, y)

        return wm.invoke_props_dialog(self, width=popup_width, title=self.title)

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        column.alignment = "CENTER"
        for line in self.text_1.split("\n"):
            column.label(text=line)

        box = layout.box()
        column = box.column(align=True)
        for line in self.text_2.split("\n"):
            column.label(text=line)

        column = layout.column(align=True)
        for line in self.text_3.split("\n"):
            column.label(text=line)

        layout.alert = not self.compatible
        if self.compatible:
            status = "Compatible" if self.compatible else "Incompatible"
            status_icon = "STRIP_COLOR_04" if self.compatible else "STRIP_COLOR_01"
        else:
            status = "Incompatible"
            status_icon = "STRIP_COLOR_01"
        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.label(text="Your System:", icon="SYSTEM")
        row.label(text=f"{status}", icon=status_icon)

        box = layout.box()
        column = box.column(align=True)

        for line in self.text_4.split("\n"):
            column.label(text=line)

        if self.compatible:
            column = layout.column(align=True)
            column.label(text="")
            column.label(text="Congratulations! You are ready to start using Fabex!")
            column.label(text="Click OK to finish the installation!")
            column.label(
                text="Then, switch the Render Engine to Fabex, select an Object and add an Operation to get started!"
            )
        else:
            layout.label(text="Incompatibilities have been detected!")
            layout.label(
                text="⚠️⚠️⚠️ The easiest fix is to download Blender from blender.org if that is possible! ⚠️⚠️⚠️"
            )
            layout.label(text="Common Issues:")

            box = layout.box()
            box.label(text="RuntimeError")
            box = box.box()
            col = box.column(align=True)
            col.label(
                text="You are using an incompatible version of Python. Check the location and version of your Python install in the box above."
            )
            col.label(
                text="Try using a tool like uv or pyenv to install the correct version and create a virtual environment for Blender"
            )

            box = layout.box()
            box.label(text="ModuleNotFoundError")
            box = box.box()
            col = box.column(align=True)
            col.label(
                text="You are using an incompatible version of Python. Check the location and version of your Python install in the box above."
            )
            col.label(
                text="You can manually manage the packages available to Blender's Python to resolve missing modules."
            )
            col.label(text="Fabex comes with pre-built binary packages for Python 3.11.13")
            col.label(
                text="You will need to provide replacements for: shapely, opencamlib, llvmlite, numba"
            )

            box = layout.box()
            box.label(text="Presets Not Found")
            box = box.box()
            col = box.column(align=True)
            col.label(text="Fabex will verify Presets on Blender startup.")
            col.label(text="Restarting Blender should fix this issue.")

            box = layout.box()
            box.label(text="UI is incomplete or broken.")
            box = box.box()
            col = box.column(align=True)
            col.label(text="There may have been errors in the installation process.")
            col.label(
                text="If you have resolved all the above issues, then restarting Blender should fix this issue."
            )
            col.label(text="If not, double-check your Python version and dependencies.")
