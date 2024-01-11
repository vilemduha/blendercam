import tempfile
import sys
import subprocess
import pathlib

INSTALL_CODE=f"""
import bpy
bpy.ops.preferences.addon_install(filepath='{sys.argv[1]}')
bpy.ops.preferences.addon_enable(module='cam')
bpy.ops.wm.save_userpref()
"""

with tempfile.TemporaryDirectory() as td:
  file=pathlib.Path(td,"install.py")
  file.write_text(INSTALL_CODE)
  command = f'blender -b -P "{str(file)}"'
  subprocess.run(command, shell=True, check=True)


