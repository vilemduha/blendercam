"""Fabex 'operation_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

from math import pi
from pathlib import Path
import pickle

import bpy
from bpy_extras import object_utils

from .simple_utils import get_cache_path
from .simple_utils import unit_value_to_string

from ..constants import was_hidden_dict


def get_operation_sources(o):
    """Get operation sources based on the geometry source type.

    This function retrieves and sets the operation sources for a given
    object based on its geometry source type. It handles three types of
    geometry sources: 'OBJECT', 'COLLECTION', and 'IMAGE'. For 'OBJECT', it
    selects the specified object and applies rotations if enabled. For
    'COLLECTION', it retrieves all objects within the specified collection.
    For 'IMAGE', it sets a specific optimization flag. Additionally, it
    determines whether the objects are curves or meshes based on the
    geometry source.

    Args:
        o (Object): An object containing properties such as geometry_source,
            object_name, collection_name, rotation_a, rotation_b,
            enable_A, enable_B, old_rotation_a, old_rotation_b,
            A_along_x, and optimisation.

    Returns:
        None: This function does not return a value but modifies the
            properties of the input object.
    """

    if o.geometry_source == "OBJECT":
        # bpy.ops.object.select_all(action='DESELECT')
        ob = bpy.data.objects[o.object_name]
        o.objects = [ob]
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if o.enable_b_axis or o.enable_a_axis:
            if o.old_rotation_a != o.rotation_a or o.old_rotation_b != o.rotation_b:
                o.old_rotation_a = o.rotation_a
                o.old_rotation_b = o.rotation_b
                ob = bpy.data.objects[o.object_name]
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
                if o.a_along_x:  # A parallel with X
                    if o.enable_a_axis:
                        bpy.context.active_object.rotation_euler.x = o.rotation_a
                    if o.enable_b_axis:
                        bpy.context.active_object.rotation_euler.y = o.rotation_b
                else:  # A parallel with Y
                    if o.enable_a_axis:
                        bpy.context.active_object.rotation_euler.y = o.rotation_a
                    if o.enable_b_axis:
                        bpy.context.active_object.rotation_euler.x = o.rotation_b

    elif o.geometry_source == "COLLECTION":
        collection = bpy.data.collections[o.collection_name]
        o.objects = collection.objects
    elif o.geometry_source == "IMAGE":
        o.optimisation.use_exact = False

    if o.geometry_source == "OBJECT" or o.geometry_source == "COLLECTION":
        o.onlycurves = True
        for ob in o.objects:
            if ob.type == "MESH":
                o.onlycurves = False
    else:
        o.onlycurves = False


def reload_paths(o):
    """Reload the CAM path data from a pickle file.

    This function retrieves the CAM path data associated with the given
    object `o`. It constructs a new mesh from the path vertices and updates
    the object's properties with the loaded data. If a previous path mesh
    exists, it is removed to avoid memory leaks. The function also handles
    the creation of a new mesh object if one does not already exist in the
    current scene.

    Args:
        o (Object): The object for which the CAM path is being
    """

    oname = "cam_path_" + o.name
    s = bpy.context.scene
    # for o in s.objects:
    ob = None
    old_pathmesh = None
    if oname in s.objects:
        old_pathmesh = s.objects[oname].data
        ob = s.objects[oname]

    picklepath = get_cache_path(o) + ".pickle"
    f = open(picklepath, "rb")
    d = pickle.load(f)
    f.close()

    o.info.warnings = d["warnings"]
    o.info.duration = d["duration"]
    verts = d["path"]

    edges = []
    for a in range(0, len(verts) - 1):
        edges.append((a, a + 1))

    oname = "cam_path_" + o.name
    mesh = bpy.data.meshes.new(oname)
    mesh.name = oname
    mesh.from_pydata(verts, edges, [])

    if oname in s.objects:
        s.objects[oname].data = mesh
    else:
        object_utils.object_data_add(bpy.context, mesh, operator=None)
        ob = bpy.context.active_object
        ob.name = oname
    ob = s.objects[oname]
    ob.location = (0, 0, 0)
    o.path_object_name = oname
    o.changed = False

    if old_pathmesh is not None:
        bpy.data.meshes.remove(old_pathmesh)


def update_operation(self, context):
    """Update the visibility and selection state of CAM operations in the
    scene.

    This method manages the visibility of objects associated with CAM
    operations based on the current active operation. If the
    'hide_all_others' flag is set to true, it hides all other objects except
    for the currently active one. If the flag is false, it restores the
    visibility of previously hidden objects. The method also attempts to
    highlight the currently active object in the 3D view and make it the
    active object in the scene.

    Args:
        context (bpy.types.Context): The context containing the current scene and
    """

    scene = context.scene
    ao = scene.cam_operations[scene.cam_active_operation]
    operation_valid(self, context)

    if ao.hide_all_others:
        for _ao in scene.cam_operations:
            if _ao.path_object_name in bpy.data.objects:
                other_obj = bpy.data.objects[_ao.path_object_name]
                current_obj = bpy.data.objects[ao.path_object_name]
                if other_obj != current_obj:
                    other_obj.hide = True
                    other_obj.select = False
    else:
        for path_obj_name in was_hidden_dict:
            print(was_hidden_dict)
            if was_hidden_dict[path_obj_name]:
                # Find object and make it hidde, then reset 'hidden' flag
                obj = bpy.data.objects[path_obj_name]
                obj.hide = True
                obj.select = False
                was_hidden_dict[path_obj_name] = False

    # try highlighting the object in the 3d view and make it active
    bpy.ops.object.select_all(action="DESELECT")
    # highlight the cutting path if it exists
    try:
        ob = bpy.data.objects[ao.path_object_name]
        ob.select_set(state=True, view_layer=None)
        # Show object if, it's was hidden
        if ob.hide:
            ob.hide = False
            was_hidden_dict[ao.path_object_name] = True
        bpy.context.scene.objects.active = ob
    except Exception as e:
        print(e)


def source_valid(o, context):
    """Check the validity of a geometry source.

    This function verifies if the provided geometry source is valid based on
    its type. It checks for three types of geometry sources: 'OBJECT',
    'COLLECTION', and 'IMAGE'. For 'OBJECT', it ensures that the object name
    ends with '_cut_bridges' or exists in the Blender data objects. For
    'COLLECTION', it checks if the collection name exists and contains
    objects. For 'IMAGE', it verifies if the source image name exists in the
    Blender data images.

    Args:
        o (object): An object containing geometry source information, including
            attributes like `geometry_source`, `object_name`, `collection_name`,
            and `source_image_name`.
        context: The context in which the validation is performed (not used in this
            function).

    Returns:
        bool: True if the geometry source is valid, False otherwise.
    """

    valid = True
    if o.geometry_source == "OBJECT":
        if not o.object_name.endswith("_cut_bridges"):  # let empty bridge cut be valid
            if o.object_name not in bpy.data.objects:
                valid = False
    if o.geometry_source == "COLLECTION":
        if o.collection_name not in bpy.data.collections:
            valid = False
        elif len(bpy.data.collections[o.collection_name].objects) == 0:
            valid = False

    if o.geometry_source == "IMAGE":
        if o.source_image_name not in bpy.data.images:
            valid = False
    return valid


def operation_valid(self, context):
    """Validate the current CAM operation in the given context.

    This method checks if the active CAM operation is valid based on the
    current scene context. It updates the operation's validity status and
    provides warnings if the source object is invalid. Additionally, it
    configures specific settings related to image geometry sources.

    Args:
        context (Context): The context containing the scene and CAM operations.
    """

    scene = context.scene
    o = scene.cam_operations[scene.cam_active_operation]
    o.changed = True
    o.valid = source_valid(o, context)
    invalidmsg = "Invalid Source Object for Operation.\n"
    if o.valid:
        o.info.warnings = ""
    else:
        o.info.warnings = invalidmsg
        addon_prefs = bpy.context.preferences.addons["bl_ext.user_default.fabex"].preferences
        if addon_prefs.show_popups:
            bpy.ops.cam.popup("INVOKE_DEFAULT")

    if o.geometry_source == "IMAGE":
        o.optimisation.use_exact = False
    o.update_offset_image_tag = True
    o.update_z_buffer_image_tag = True
    print("Validity ")


def chain_valid(chain, context):
    """Check the validity of a chain of operations within a given context.

    This function verifies if all operations in the provided chain are valid
    according to the current scene context. It first checks if the chain
    contains any operations. If it does, it iterates through each operation
    in the chain and checks if it exists in the scene's CAM operations.
    If an operation is not found or is deemed invalid, the function returns
    a tuple indicating the failure and provides an appropriate error
    message. If all operations are valid, it returns a success indication.

    Args:
        chain (Chain): The chain of operations to validate.
        context (Context): The context containing the scene and CAM operations.

    Returns:
        tuple: A tuple containing a boolean indicating validity and an error message
            (if any). The first element is True if valid, otherwise False. The
            second element is an error message string.
    """

    s = context.scene
    if len(chain.operations) == 0:
        return (False, "")
    for cho in chain.operations:
        found_op = None
        for so in s.cam_operations:
            if so.name == cho.name:
                found_op = so
        if found_op == None:
            return (False, f"Couldn't Find Operation {cho.name}")
        if source_valid(found_op, context) is False:
            return (False, f"Operation {found_op.name} Is Not Valid")
    return (True, "")


def update_operation_valid(self, context):
    update_operation(self, context)


# Update functions start here
def update_chipload(self, context):
    """Update the chipload based on feedrate, spindle RPM, and cutter
    parameters.

    This function calculates the chipload using the formula: chipload =
    feedrate / (spindle_rpm * cutter_flutes). It also attempts to account
    for chip thinning when cutting at less than 50% cutter engagement with
    cylindrical end mills by combining two formulas. The first formula
    provides the nominal chipload based on standard recommendations, while
    the second formula adjusts for the cutter diameter and distance between
    paths.  The current implementation may not yield consistent results, and
    there are concerns regarding the correctness of the units used in the
    calculations. Further review and refinement of this function may be
    necessary to improve accuracy and reliability.

    Args:
        context: The context in which the update is performed (not used in this
            implementation).

    Returns:
        None: This function does not return a value; it updates the chipload in place.
    """
    print("Update Chipload ")
    o = self
    # Old chipload
    o.info.chipload = o.feedrate / (o.spindle_rpm * o.cutter_flutes)
    o.info.chipload_per_tooth = unit_value_to_string(o.info.chipload, 4)
    # New chipload with chip thining compensation.
    # I have tried to combine these 2 formulas to compinsate for the phenomenon of chip thinning when cutting at less
    # than 50% cutter engagement with cylindrical end mills. formula 1 Nominal Chipload is
    # " feedrate mm/minute = spindle rpm x chipload x cutter diameter mm x cutter_flutes "
    # formula 2 (.5*(cutter diameter mm devided by distance_between_paths)) divided by square root of
    # ((cutter diameter mm devided by distance_between_paths)-1) x Nominal Chipload
    # Nominal Chipload = what you find in end mill data sheats recomended chip load at %50 cutter engagment.
    # I am sure there is a better way to do this. I dont get consistent result and
    # I am not sure if there is something wrong with the units going into the formula, my math or my lack of
    # underestanding of python or programming in genereal. Hopefuly some one can have a look at this and with any luck
    # we will be one tiny step on the way to a slightly better chipload calculating function.

    # self.chipload = ((0.5*(o.cutter_diameter/o.distance_between_paths))/(sqrt((o.feedrate*1000)/(o.spindle_rpm*o.cutter_diameter*o.cutter_flutes)*(o.cutter_diameter/o.distance_between_paths)-1)))
    print(f"Chipload: {o.info.chipload}")
    print(f"Chipload per Tooth: {o.info.chipload_per_tooth}")


def update_offset_image(self, context):
    """Refresh the Offset Image Tag for re-rendering.

    This method updates the chip load and marks the offset image tag for re-
    rendering. It sets the `changed` attribute to True and indicates that
    the offset image tag needs to be updated.

    Args:
        context: The context in which the update is performed.
    """
    update_chipload(self, context)
    print("Update Offset")
    self.changed = True
    self.update_offset_image_tag = True


def update_Z_buffer_image(self, context):
    """Update the Z-buffer and offset image tags for recalculation.

    This method modifies the internal state to indicate that the Z-buffer
    image and offset image tags need to be updated during the calculation
    process. It sets the `changed` attribute to True and marks the relevant
    tags for updating. Additionally, it calls the `getOperationSources`
    function to ensure that the necessary operation sources are retrieved.

    Args:
        context: The context in which the update is being performed.
    """
    self.changed = True
    self.update_z_buffer_image_tag = True
    self.update_offset_image_tag = True
    get_operation_sources(self)


def update_image_size_y(self, context):
    """Updates the Image Y size based on the following function."""
    if self.source_image_name != "":
        i = bpy.data.images[self.source_image_name]
        if i is not None:
            size_x = self.source_image_size_x / i.size[0]
            size_y = int(x_size * i.size[1] * 1000000) / 1000
            col.label(text="Image Size on Y Axis: " + unit_value_to_string(size_y, 8))
            col.separator()


def update_bridges(o, context):
    """Update the status of bridges.

    This function marks the bridge object as changed, indicating that an
    update has occurred. It prints a message to the console for logging
    purposes. The function takes in an object and a context, but the context
    is not utilized within the function.

    Args:
        o (object): The bridge object that needs to be updated.
        context (object): Additional context for the update, not used in this function.
    """

    print("Update Bridges ")
    o.changed = True


def update_rotation(o, context):
    """Update the rotation of a specified object in Blender.

    This function modifies the rotation of a Blender object based on the
    properties of the provided object 'o'. It checks which rotations are
    enabled and applies the corresponding rotation values to the active
    object in the scene. The rotation can be aligned either along the X or Y
    axis, depending on the configuration of 'o'.

    Args:
        o (object): An object containing rotation settings and flags.
        context (object): The context in which the operation is performed.
    """

    print("Update Rotation")
    if o.enable_b_axis or o.enable_a_axis:
        print(o, o.rotation_a)
        ob = bpy.data.objects[o.object_name]
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if o.a_along_x:  # A parallel with X
            if o.enable_a_axis:
                bpy.context.active_object.rotation_euler.x = o.rotation_a
            if o.enable_b_axis:
                bpy.context.active_object.rotation_euler.y = o.rotation_b
        else:  # A parallel with Y
            if o.enable_a_axis:
                bpy.context.active_object.rotation_euler.y = o.rotation_a
            if o.enable_b_axis:
                bpy.context.active_object.rotation_euler.x = o.rotation_b


def update_rest(o, context):
    """Update the state of the object.

    This function modifies the given object by setting its 'changed'
    attribute to True. It also prints a message indicating that the update
    operation has been performed.

    Args:
        o (object): The object to be updated.
        context (object): The context in which the update is being performed.
    """

    print("Update Rest ")
    o.changed = True


def update_operation(self, context):
    """Update the CAM operation based on the current context.

    This function retrieves the active CAM operation from the Blender
    context and updates it using the `updateRest` function. It accesses the
    active operation from the scene's CAM operations and passes the
    current context to the updating function.

    Args:
        context: The context in which the operation is being updated.
    """

    # from . import updateRest
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    update_rest(active_op, bpy.context)


def update_zbuffer_image(self, context):
    """Update the Z-buffer image based on the active CAM operation.

    This function retrieves the currently active CAM operation from the
    Blender context and updates the Z-buffer image accordingly. It accesses
    the scene's CAM operations and invokes the `updateZbufferImage`
    function with the active operation and context.

    Args:
        context (bpy.context): The current Blender context.
    """

    # from . import updateZbufferImage
    active_op = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
    update_Z_buffer_image(active_op, bpy.context)


def get_chain_operations(chain):
    """Return chain operations associated with a given chain object.

    This function iterates through the operations of the provided chain
    object and retrieves the corresponding operations from the current
    scene's CAM operations in Blender. Due to limitations in Blender,
    chain objects cannot store operations directly, so this function serves
    to extract and return the relevant operations for further processing.

    Args:
        chain (object): The chain object from which to retrieve operations.

    Returns:
        list: A list of operations associated with the given chain object.
    """
    chop = []
    for cho in chain.operations:
        for so in bpy.context.scene.cam_operations:
            if so.name == cho.name:
                chop.append(so)
    return chop
