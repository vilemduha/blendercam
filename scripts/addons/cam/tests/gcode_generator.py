import sys
import warnings

import bpy

warnings.simplefilter("once")

# Get the scene
s = bpy.context.scene

for i, operation in enumerate(s.cam_operations):
    # Set the active operation using the index
    s.cam_active_operation = i

    print(f"############ Generating {operation.name} #############")

    # Run the calculate_cam_path() operator
    bpy.ops.object.calculate_cam_path()

sys.exit(0)
