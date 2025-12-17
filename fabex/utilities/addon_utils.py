"""Fabex 'addon_utils.py' © 2012 Vilem Novak"""

from pathlib import Path
import shutil

import bpy
from bpy.app.handlers import persistent

from .logging_utils import log

from ..constants import _IS_LOADING_DEFAULTS
from ..exception import CamException
from .. import __package__ as base_package


def addon_dependencies():
    """Checks for and installs Blender addon dependencies.

    This function installs a number of addons that previously came
    with Blender, but now have to be downloaded from an online repository.
    It checks for the addon in the users Blender install, and if it
    can't find them, attempts to download them from Blender.
    """
    preferences = bpy.context.preferences
    addons = preferences.addons
    online_access = preferences.system.use_online_access

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

    if online_access:
        for module in modules:
            if module not in addons:
                try:
                    addons[f"bl_ext.blender_org.{module}"]
                except KeyError:
                    bpy.ops.extensions.package_install(repo_index=0, pkg_id=module)
    else:
        log.debug("Could not Access Online Addon Repository!")
        raise CamException(
            "Fabex couldn't install required addons - 'Enable Online Access' in 'Preferences > System'"
        )


def load_defaults(addon_prefs):
    """Assigns scene settings based on user preferences.

    When Fabex is activated it will restore the user's scene settings.
    This includes the interface level (Beginner - Experimental), viewport
    shading, panel layout and machine preset.
    """
    scene = bpy.context.scene
    interface = scene.interface

    # set interface level to previously used level for a new file
    if not bpy.data.filepath:
        _IS_LOADING_DEFAULTS = True

        interface.level = addon_prefs.default_interface_level
        interface.shading = addon_prefs.default_shading

        interface.layout = addon_prefs.default_layout

        interface.main_location = addon_prefs.default_main_location
        interface.operation_location = addon_prefs.default_operation_location
        interface.tools_location = addon_prefs.default_tools_location

        machine_preset = addon_prefs.machine_preset = addon_prefs.default_machine_preset
        if len(machine_preset) > 0:
            log.info(f"Loading Preset: {machine_preset}")
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
    """Copies Presets from the addon to Blender's Script Directory

    This function copies new presets without overwriting the existing presets,
    unless it detects that the presets have not been updated to the current spec,
    in which case it will overwrite them with the addon presets.
    """
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

    log.debug("Blender Startup")

    scene = bpy.context.scene
    render_engine = scene.render.engine
    interface_layout = scene.interface.layout

    for o in scene.cam_operations:
        if o.computing:
            o.computing = False

    addon_dependencies()
    log.debug("Found / Installed Addon Dependencies")

    add_asset_library()
    log.debug("Found / Installed Asset Library")

    add_workspace()
    log.debug("Found / Installed Workspace")

    addon_prefs = bpy.context.preferences.addons[base_package].preferences
    copy_presets(addon_prefs)
    log.debug("Preset Files Copied")

    # Use the Message Bus to notify when the Render Engine is changed
    # And run the 'on_engine_change' function
    bpy.types.Scene.engine_check = object()
    subscribe_to = bpy.types.RenderSettings, "engine"
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=bpy.types.Scene.engine_check,
        args=(),
        notify=on_engine_change,
    )

    if render_engine in ["CNCCAM_RENDER", "BLENDERCAM_RENDER"]:
        render_engine = "FABEX_RENDER"

    if render_engine == "FABEX_RENDER":
        interface_layout = addon_prefs.default_layout

        add_collections()
        log.debug("Collections Added to Scene")
        load_defaults(addon_prefs)
        log.debug("Loading Fabex Settings")

        log.debug("Fabex Activated")


def on_engine_change(*args):
    """Callback function to setup Fabex when activated.

    In combination with a message bus (msgbus) listener, this function will
    run when the Render Engine is changed. If it detects that Fabex is active
    it will call the required setup functions, and log the Fabex activation.
    """
    context = bpy.context
    scene = context.scene

    render_engine = scene.render.engine
    interface_layout = scene.interface.layout

    addon_prefs = context.preferences.addons[base_package].preferences

    if render_engine == "FABEX_RENDER":
        interface_layout = addon_prefs.default_layout

        add_collections()
        log.debug("Collections Added to Scene")
        load_defaults(addon_prefs)
        log.debug("Loading Fabex Settings")

        log.debug("Fabex Activated")

        # Initialize an Operation if one hasn't already been created
        if len(context.scene.cam_operations) == 0:
            bpy.ops.scene.cam_operation_add()
            log.debug("Added Default Operation")


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


def add_asset_library():
    """Installs the Fabex Asset Library.

    This function adds the /assets/ folder from Fabex to the users'
    Asset Library, which adds a number of Material and Geometry Node
    assets.
    """
    filepaths = bpy.context.preferences.filepaths
    libraries = filepaths.asset_libraries

    if "Fabex Assets" not in libraries:
        library_path = str(Path(__file__).parent.parent / "assets")
        bpy.ops.preferences.asset_library_add(directory=library_path)
        filepaths.asset_libraries["assets"].name = "Fabex Assets"
    else:
        pass


def add_workspace():
    """Installs the Fabex Workspace

    This function adds the Fabex Workspace to the users' default Blender
    startup scene.
    """
    workspaces = bpy.data.workspaces
    if "FabexCNC" not in workspaces:
        workspace_file = str(
            Path(__file__).parent.parent / "assets" / "Fabex_Assets.blend/WorkSpace/"
        )
        bpy.ops.wm.append(directory=workspace_file, filename="FabexCNC")

    else:
        pass


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
