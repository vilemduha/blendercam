import sys
import warnings

import bpy

warnings.simplefilter("once")

print(bpy.context.scene.render.engine)
print(bpy.context.preferences.addons["bl_ext.user_default.fabex"])

# Get the scene
s = bpy.context.scene
s.render.engine = "FABEX_RENDER"

for i, operation in enumerate(s.cam_operations):
    # Set the active operation using the index
    s.cam_active_operation = i

    print(f"############ Generating {operation.name} #############")

    # Run the calculate_cam_path() operator
    bpy.ops.object.calculate_cam_path()

sys.exit(0)
