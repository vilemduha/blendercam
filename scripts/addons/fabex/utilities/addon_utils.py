"""Fabex 'addon_utils.py' © 2012 Vilem Novak
"""

from pathlib import Path
import shutil

import bpy
from bpy.app.handlers import persistent

from ..constants import _IS_LOADING_DEFAULTS


def addon_dependencies():
    addons = bpy.context.preferences.addons

    modules = [
        # Objects & Tools
        "extra_mesh_objects",
        "extra_curve_objectes",
        "simplify_curves_plus",
        "curve_tools",
        "print3d_toolbox",
        # File Formats
        "stl_format_legacy",
        "import_autocad_dxf_format_dxf",
        "export_autocad_dxf_format_dxf",
    ]

    for module in modules:
        if module not in addons:
            try:
                addons[f"bl_ext.blender_org.{module}"]
            except KeyError:
                bpy.ops.extensions.package_install(repo_index=0, pkg_id=module)


def load_defaults(addon_prefs):
    scene = bpy.context.scene
    # set interface level to previously used level for a new file
    if not bpy.data.filepath:
        _IS_LOADING_DEFAULTS = True

        scene.interface.level = addon_prefs.default_interface_level
        scene.interface.shading = addon_prefs.default_shading

        scene.interface.layout = addon_prefs.default_layout

        scene.interface.main_location = addon_prefs.default_main_location
        scene.interface.operation_location = addon_prefs.default_operation_location
        scene.interface.tools_location = addon_prefs.default_tools_location

        machine_preset = addon_prefs.machine_preset = addon_prefs.default_machine_preset
        if len(machine_preset) > 0:
            print("Loading Preset:", machine_preset)
            # load last used machine preset
            bpy.ops.script.execute_preset(
                filepath=machine_preset,
                menu_idname="CAM_MACHINE_MT_presets",
            )
        _IS_LOADING_DEFAULTS = False


def copy_if_not_exists(src, dst):
    """Copy a file from source to destination if it does not already exist.

    This function checks if the destination file exists. If it does not, the
    function copies the source file to the destination using a high-level
    file operation that preserves metadata.

    Args:
        src (str): The path to the source file to be copied.
        dst (str): The path to the destination where the file should be copied.
    """

    if Path(dst).exists() == False:
        shutil.copy2(src, dst)


def copy_presets(addon_prefs):
    # copy presets if not there yet
    preset_source_path = Path(__file__).parent.parent / "presets"
    preset_target_path = Path(bpy.utils.script_path_user()) / "presets"

    shutil.copytree(
        preset_source_path,
        preset_target_path,
        copy_function=copy_if_not_exists,
        dirs_exist_ok=True,
    )

    bpy.ops.wm.save_userpref()

    if not addon_prefs.op_preset_update:
        # Update the Operation presets
        op_presets_source = Path(__file__).parent.parent / "presets" / "cam_operations"
        op_presets_target = Path(bpy.utils.script_path_user()) / "presets" / "cam_operations"
        shutil.copytree(op_presets_source, op_presets_target, dirs_exist_ok=True)
        addon_prefs.op_preset_update = True


@bpy.app.handlers.persistent
def on_blender_startup(context):
    """Checks for any broken computations on load and resets them.

    This function verifies the presence of necessary Blender add-ons and
    installs any that are missing. It also resets any ongoing computations
    in CAM operations and sets the interface level to the previously used
    level when loading a new file. If the add-on has been updated, it copies
    the necessary presets from the source to the target directory.
    Additionally, it checks for updates to the CAM plugin and updates
    operation presets if required.

    Args:
        context: The context in which the function is executed, typically containing
            information about
            the current Blender environment.
    """

    scene = bpy.context.scene
    for o in scene.cam_operations:
        if o.computing:
            o.computing = False

    addon_prefs = bpy.context.preferences.addons["bl_ext.user_default.fabex"].preferences

    addon_dependencies()
    load_defaults(addon_prefs)
    copy_presets(addon_prefs)


def on_engine_change(*args):
    if bpy.context.scene.render.engine == "FABEX_RENDER":
        bpy.context.scene.interface.layout = bpy.context.preferences.addons[
            "bl_ext.user_default.fabex"
        ].preferences.default_layout
        print("Fabex!")


def fix_units():
    """Set up units for Fabex.

    This function configures the unit settings for the current Blender
    scene. It sets the rotation system to degrees and the scale length to
    1.0, ensuring that the units are appropriately configured for use within
    Fabex.
    """
    s = bpy.context.scene
    s.unit_settings.system_rotation = "DEGREES"
    s.unit_settings.scale_length = 1.0
    # Blender CAM doesn't respect this property and there were users reporting problems, not seeing this was changed.


def keymap_register():
    wm = bpy.context.window_manager
    addon_kc = wm.keyconfigs.addon

    km = addon_kc.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new(
        "wm.call_menu_pie",
        "C",
        "PRESS",
        alt=True,
    )
    kmi.properties.name = "VIEW3D_MT_PIE_CAM"
    kmi.active = True


def keymap_unregister():
    wm = bpy.context.window_manager
    active_kc = wm.keyconfigs.active

    for key in active_kc.keymaps["Object Mode"].keymap_items:
        if key.idname == "wm.call_menu" and key.properties.name == "VIEW3D_MT_PIE_CAM":
            active_kc.keymaps["Object Mode"].keymap_items.remove(key)
