import sys
import warnings

import bpy

# from ..utilities.logging_utils import log

warnings.simplefilter("once")
try:
    bpy.ops.preferences.addon_disable(module="bl_ext.user_default.fabex")
except:
    pass
bpy.ops.preferences.addon_enable(module="bl_ext.user_default.fabex")

# Set the Render Engine to Fabex
scene = bpy.context.scene
scene.render.engine = "FABEX_RENDER"

for i, operation in enumerate(scene.cam_operations):
    # Set the active operation using the index
    scene.cam_active_operation = i

    print(".")
    print("~")
    print("~~")
    print("~~~")
    print("################################################################")
    print(f"############ Generating Operation: {operation.name} ############")
    print("################################################################")

    # Run the calculate_cam_path() operator
    bpy.ops.object.calculate_cam_path()

    print("################################################################")
    print(f"############ Operation: {operation.name} Complete! ############")
    print("################################################################")
    print("~~~")
    print("~~")
    print("~")
    print(".")

sys.exit(0)
