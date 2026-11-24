import os
import re
import shutil
import subprocess
from pathlib import Path

import bpy

delta = 0.002


def activate_dependencies(self):
    """Install / Enable Addon Dependencies"""
    bpy.context.preferences.system.use_online_access = True
    bpy.ops.extensions.repo_sync_all(use_active_only=False)
    dependencies = [
        "curve_tools",
        "simplify_curves_plus",
        "stl_format_legacy",
        "extra_mesh_objects",
        "extra_curve_objectes",
        "print3d_toolbox",
    ]
    for dependency in dependencies:
        try:
            bpy.ops.preferences.addon_enable(
                module=f"bl_ext.blender_org.{dependency}",
            )
        except RuntimeError:
            bpy.ops.extensions.package_install(
                repo_index=0,
                pkg_id=dependency,
            )
    addons = bpy.context.preferences.addons
    self.modules = [addon.module for addon in addons]


def get_modules(self):
    addons = bpy.context.preferences.addons
    self.modules = [addon.module for addon in addons]


def install_extension():
    """Identify the version and install the matching zip file"""
    version_file = Path(__file__).parent.parent / "version.py"
    with open(version_file) as f:
        lines = f.readlines()
        version = lines[0].split("(")[1].replace(",", "")
    major, minor, patch = version[0], version[1], version[2]
    path = str(Path(__file__).parent.parent.parent / f"fabex-{major}.{minor}.{patch}.zip")
    bpy.ops.extensions.package_install_files(filepath=path, repo="user_default")


def activate_engine(self):
    """Activate the Fabex Engine and store the name"""
    # Set the Render Engine to Fabex
    scene = bpy.context.scene
    scene.render.engine = "FABEX_RENDER"
    self.engine = scene.render.engine


def add_collections():
    """Adds color-coded Collection folders to the scene.

    This function adds three collections to aid in scene management.
    Bridges, Paths and Simulations are now auto-sorted into their
    own collections upon creation, which can be shown or hidden as
    groups.
    """
    context = bpy.context
    data = bpy.data
    collections = data.collections
    cam_names = context.scene.cam_names
    path_prefix = cam_names.path_prefix
    simulation_prefix = cam_names.simulation_prefix

    scene_collection = context.scene.collection
    default_collection = collections["Collection"]
    fabex_collections = [
        ("Bridges (Tabs)", "COLOR_06"),
        ("Paths", "COLOR_04"),
        ("Simulations", "COLOR_05"),
    ]

    for collection, color in fabex_collections:
        if collection not in collections:
            collections.new(collection)
            scene_collection.children.link(collections[collection])
            collections[collection].color_tag = color

    bridges_collection = collections["Bridges (Tabs)"]
    paths_collection = collections["Paths"]
    simulations_collection = collections["Simulations"]

    children = default_collection.children
    for child in children:
        prefix = child.name.startswith
        if prefix("bridge"):
            bridges_collection.children.link(child)
            default_collection.children.unlink(child)

    objects = default_collection.objects
    for obj in objects:
        prefix = obj.name.startswith
        if prefix(path_prefix):
            try:
                paths_collection.objects[obj.name]
            except RuntimeError:
                paths_collection.objects.link(obj)
        if prefix(simulation_prefix):
            try:
                simulations_collection.objects[obj.name]
            except RuntimeError:
                simulations_collection.objects.link(obj)
        if prefix in ["bridge", path_prefix, simulation_prefix]:
            default_collection.objects.unlink(obj)


# def remove_test_images(test):
#     """Loads a Test Blend file and calculates all operations in order"""
#     path = str(Path(__file__).parent / "test_data" / test / "temp_cam")
#     [os.remove(file) for _root, _dir, files in os.walk(path) for file in files]


def run_test_file(test):
    """Loads a Test Blend file and calculates all operations in order"""
    path = str(Path(__file__).parent / "test_data" / test / f"{test}.blend")
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    operations = scene.cam_operations
    # Set the active operation using the index
    for i, operation in enumerate(operations):
        scene.cam_active_operation = i
        # Run the calculate_cam_path() operator
        bpy.ops.object.calculate_cam_path()


def get_gcode_filepaths(test, paths):
    """Loads the generated and reference Gcode filepaths from the test folder"""
    path = str(Path(__file__).parent / "test_data" / test)
    # os.chdir(path)
    generated_files = [
        file
        for _root, _dir, files in os.walk(path)
        for file in files
        if (file.startswith("_") and (file.endswith(".gcode") or file.endswith(".tap")))
    ]
    expected_files = [
        file
        for _root, _dir, files in os.walk(path)
        for file in files
        if (not file.startswith("_") and (file.endswith(".gcode") or file.endswith(".tap")))
    ]

    return generated_files, expected_files


def get_gcode_from_file(file):
    """Opens and reads a Gcode file, removes comment lines and returns a list of lines"""
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("("):
                lines.remove(line)
        return "".join(lines)


def compare_gcode_files(generated_file, expected_file):
    """Compares coordinate and feedrate data from the supplied Gcode files"""
    generated = get_gcode_from_file(generated_file)
    expected = get_gcode_from_file(expected_file)

    pattern = re.compile(r"(?<!G)[+-]?\d+(?:\.\d+)?", re.IGNORECASE)
    generated_stripped = [float(m.group(0)) for m in pattern.finditer(generated)]
    expected_stripped = [float(m.group(0)) for m in pattern.finditer(expected)]

    return generated_stripped, expected_stripped


def build_extension(blender):
    """Build the Extension using the Blender executable specified"""
    source_dir = str(Path(__file__).parent.parent)
    output_dir = str(Path(__file__).parent.parent.parent)

    subprocess.run(
        [
            blender,
            "--background",
            "--factory-startup",
            "--command",
            "extension",
            "build",
            "--source-dir",
            source_dir,
            "--output-dir",
            output_dir,
        ],
        check=False,
    )


def zip_extension():
    """Create an Extension by zipping the main folder"""
    version_file = Path(__file__).parent.parent / "version.py"
    with open(version_file) as f:
        lines = f.readlines()
        version = lines[0].split("(")[1].replace(",", "")
    major, minor, patch = version[0], version[1], version[2]
    extension_name = f"fabex-{major}.{minor}.{patch}"
    fabex_path = Path(__file__).parent.parent
    shutil.make_archive(extension_name, "zip", fabex_path)


# import bpy

# decimal_places = 4
# test_path_name = "cam_path_Op_Suzanne_1"

# path_calc = bpy.data.objects[test_path_name]
# path_file = bpy.data.objects["Gcode"]

# try:
#     verts_calc = path_calc.data.splines[0].points
# except AttributeError:
#     verts_calc = path_calc.data.vertices

# verts_file = path_file.data.splines[0].points

# errors = 0
# points = len(verts_calc)

# for i, v in enumerate(verts_calc):
#     if i < len(verts_calc) - 1:
#         cx, cy, cz = (
#             round(verts_calc[i + 1].co[0], decimal_places),
#             round(verts_calc[i + 1].co[1], decimal_places),
#             round(verts_calc[i + 1].co[2], decimal_places),
#         )
#         fx, fy, fz = (
#             round(verts_file[i].co[0], decimal_places),
#             round(verts_file[i].co[1], decimal_places),
#             round(verts_file[i].co[2], decimal_places),
#         )

#         if (cx, cy, cz) != (fx, fy, fz):
#             errors += 1
#             print("Error:")
#             print(f"Point {i}:")
#             if cx != fx:
#                 print(f"X: {cx} != {fx}")
#             if cy != fy:
#                 print(f"Y: {cy} != {fy}")
#             if cz != fz:
#                 print(f"Z: {cz} != {fz}")
#             print("")

# percent = 100.0 - (errors/points) if errors > 0 else 100

# print("____________________")
# print("")
# print("| Analysis Complete")
# print(f"| {errors} discrepancies")
# print(f"| {round(percent, decimal_places)}% accurate to {decimal_places} decimal points")
# print("____________________")
# print("")
