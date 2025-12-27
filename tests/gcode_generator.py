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

    generate_string = f"############ Generating Operation: {operation.name} ############"
    generate_border = len(generate_string) * "#"

    complete_string = f"############ Operation: {operation.name} Complete! ############"
    complete_border = len(complete_string) * "#"

    print(".")
    print("#")
    print("##")
    print("###")
    print(generate_border)
    print(generate_string)
    print(generate_border)

    # Run the calculate_cam_path() operator
    bpy.ops.object.calculate_cam_path()

    print(complete_border)
    print(complete_string)
    print(complete_border)
    print("###")
    print("##")
    print("#")
    print(".")

sys.exit(0)
