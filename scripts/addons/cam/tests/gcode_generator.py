import sys
import warnings

import bpy

warnings.simplefilter("once")

# try:
#     bpy.context.preferences.addons["bl_ext.user_default.fabex"]
# except KeyError:
#     print("Addon is not installed, attempting install...")
#     bpy.context.preferences.system.use_online_access = True
#     bpy.ops.extensions.repo_sync_all(use_active_only=False)
#     bpy.ops.extensions.package_install_files(filepath=f"{sys.argv[1]}", repo="user_default")

sys.path.append(sys.argv[1])

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
