import tempfile
import sys
import subprocess
import pathlib
import shutil

INSTALL_CODE = f"""
import bpy
bpy.ops.preferences.addon_install(filepath='{sys.argv[1]}')
bpy.ops.preferences.addon_enable(module='cam')
bpy.ops.wm.save_userpref()
import cam
"""

NUM_RETRIES = 10

with tempfile.TemporaryDirectory() as td:
    file = pathlib.Path(td, "install.py")
    file.write_text(INSTALL_CODE)

    # blender 4.0 installing addon crashes sometimes on mac github actions...
    for x in range(NUM_RETRIES):
        try:
            subprocess.run([shutil.which('blender'), '-b', '-P', str(file)], shell=False,
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            print("installed addon okay")
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print("Install addon failed, retrying:", e)
            print("Command output:")
            print("------------------------------")
            print(e.output)
            print("------------------------------")
            for line in str(e.output):
                if line.startswith("Writing: "):
                    crash_file = pathlib.Path(line[len("Writing: "):])
                    if crash_file.exists():
                        print("Crash log:\n================")
                        print(crash_file.read_text())
                        print("============================")
