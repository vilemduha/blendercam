import sys
import warnings

import bpy

warnings.simplefilter("once")

# Set the Render Engine to Fabex
scene = bpy.context.scene
scene.render.engine = "FABEX_RENDER"

for i, operation in enumerate(scene.cam_operations):
    # Set the active operation using the index
    scene.cam_active_operation = i

    print("~")
    print("~")
    print(f"############ Generating Operation: {operation.name} ############")

    # Run the calculate_cam_path() operator
    bpy.ops.object.calculate_cam_path()

sys.exit(0)
