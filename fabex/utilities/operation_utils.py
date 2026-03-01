"""Fabex 'operation_utils.py' © 2012 Vilem Novak

Main functionality of Fabex.
The functions here are called with operators defined in 'ops.py'
"""

from math import (
    acos,
    ceil,
    cos,
    pi,
    radians,
    sin,
    sqrt,
    tan,
)

import numpy as np
import pickle

from shapely.geometry import Polygon
from shapely.ops import unary_union

import bpy
from bpy_extras import object_utils
from mathutils import Vector

from .curve_utils import curve_to_shapely
from .logging_utils import log
from .simple_utils import (
    get_cache_path,
    unit_value_to_string,
)

from .. import __package__ as base_package
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

    s = bpy.context.scene
    oname = s.cam_names.path_name_full
    ob = s.objects[oname] if oname in s.objects else None
    old_pathmesh = s.objects[oname].data if oname in s.objects else None

    picklepath = get_cache_path(o) + ".pickle"
    f = open(picklepath, "rb")
    d = pickle.load(f)
    f.close()

    o.info.warnings = d["warnings"]
    o.info.duration = d["duration"]

    verts = d["path"]
    edges = [(a, a + 1) for a in range(0, len(verts) - 1)]

    # for a in range(0, len(verts) - 1):
    #     edges.append((a, a + 1))

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
            log.info(was_hidden_dict)
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
        log.error(e)


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
        addon_prefs = bpy.context.preferences.addons[base_package].preferences
        if addon_prefs.show_popups:
            bpy.ops.cam.popup("INVOKE_DEFAULT")

    if o.geometry_source == "IMAGE":
        o.optimisation.use_exact = False
    o.update_offset_image_tag = True
    o.update_z_buffer_image_tag = True
    log.info("Validity ")


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
    log.info("~ Update Chipload ~")
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
    log.info(f"Chipload: {o.info.chipload}")
    log.info(f"Chipload per Tooth: {o.info.chipload_per_tooth}")


def update_offset_image(self, context):
    """Refresh the Offset Image Tag for re-rendering.

    This method updates the chip load and marks the offset image tag for re-
    rendering. It sets the `changed` attribute to True and indicates that
    the offset image tag needs to be updated.

    Args:
        context: The context in which the update is performed.
    """
    update_chipload(self, context)
    log.info("~ Update Offset ~")
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
            size_y = int(size_x * i.size[1] * 1000000) / 1000
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

    log.info("~ Update Bridges ~")
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

    log.info("~ Update Rotation ~")
    if o.enable_b_axis or o.enable_a_axis:
        log.info(f"{o}, {o.rotation_a}")
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

    log.info("~ Update Rest ~")
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
    # chop = []
    # for cho in chain.operations:
    #     for so in bpy.context.scene.cam_operations:
    #         if so.name == cho.name:
    #             chop.append(so)\

    operations = bpy.context.scene.cam_operations
    chop = [so for so in operations for cho in chain.operations if so.name == cho.name]
    return chop


def get_change_data(o):
    """Check if object properties have changed to determine if image updates
    are needed.

    This function inspects the properties of objects specified by the input
    parameter to see if any changes have occurred. It concatenates the
    location, rotation, and dimensions of the relevant objects into a single
    string, which can be used to determine if an image update is necessary
    based on changes in the object's state.

    Args:
        o (object): An object containing properties that specify the geometry source
            and relevant object or collection names.

    Returns:
        str: A string representation of the location, rotation, and dimensions of
            the specified objects.
    """
    changedata = ""
    obs = []

    if o.geometry_source == "OBJECT":
        obs = [bpy.data.objects[o.object_name]]
    elif o.geometry_source == "COLLECTION":
        obs = bpy.data.collections[o.collection_name].objects

    for ob in obs:
        changedata += str(ob.location)
        changedata += str(ob.rotation_euler)
        changedata += str(ob.dimensions)

    return changedata


def check_memory_limit(o):
    """Check and adjust the memory limit for an object.

    This function calculates the resolution of an object based on its
    dimensions and the specified pixel size. If the calculated resolution
    exceeds the defined memory limit, it adjusts the pixel size accordingly
    to reduce the resolution. A warning message is appended to the object's
    info if the pixel size is modified.

    Args:
        o (object): An object containing properties such as max, min, optimisation, and
            info.

    Returns:
        None: This function modifies the object's properties in place and does not
            return a value.
    """

    sx = o.max.x - o.min.x
    sy = o.max.y - o.min.y
    resx = sx / o.optimisation.pixsize
    resy = sy / o.optimisation.pixsize
    res = resx * resy
    limit = o.optimisation.imgres_limit * 1000000

    if res > limit:
        ratio = res / limit
        o.optimisation.pixsize = o.optimisation.pixsize * sqrt(ratio)

        log.warning("!!! Memory Error !!!")
        log.warning("Memory Limit Exceeded!")
        log.warning(f"Detail Size Increased to {round(o.optimisation.pixsize, 5)}")

        o.info.warnings += " \n!!! Memory Error !!!\n"
        o.info.warnings += "Memory Limit Exceeded!\n"
        o.info.warnings += f"Detail Size Increased to {round(o.optimisation.pixsize, 5)}\n"

        log.info("Changing Sampling Resolution to %f" % o.optimisation.pixsize)


def get_move_and_spin(o):
    move_type = o.movement.type
    spin = o.movement.spindle_rotation

    climb_CW = move_type == "CLIMB" and spin == "CW"
    climb_CCW = move_type == "CLIMB" and spin == "CCW"

    conventional_CW = move_type == "CONVENTIONAL" and spin == "CW"
    conventional_CCW = move_type == "CONVENTIONAL" and spin == "CCW"

    return climb_CW, climb_CCW, conventional_CW, conventional_CCW


def get_ambient(o):
    """Calculate and update the ambient geometry based on the provided object.

    This function computes the ambient shape for a given object based on its
    properties, such as cutter restrictions and ambient behavior. It
    determines the appropriate radius and creates the ambient geometry
    either from the silhouette or as a polygon defined by the object's
    minimum and maximum coordinates. If a limit curve is specified, it will
    also intersect the ambient shape with the limit polygon.

    Args:
        o (object): An object containing properties that define the ambient behavior,
            cutter restrictions, and limit curve.

    Returns:
        None: The function updates the ambient property of the object in place.
    """

    if o.update_ambient_tag:  # cutter stays in ambient & limit curve
        m = o.cutter_diameter / 2 if o.ambient_cutter_restrict else 0

        if o.ambient_behaviour == "AROUND":
            r = o.ambient_radius - m
            # in this method we need ambient from silhouette
            o.ambient = get_object_outline(r, o, True)
        else:
            o.ambient = Polygon(
                (
                    (o.min.x + m, o.min.y + m),
                    (o.min.x + m, o.max.y - m),
                    (o.max.x - m, o.max.y - m),
                    (o.max.x - m, o.min.y + m),
                )
            )

        if o.use_limit_curve:
            if o.limit_curve != "":
                limit_curve = bpy.data.objects[o.limit_curve]
                polys = curve_to_shapely(limit_curve)
                o.limit_poly = unary_union(polys)

                if o.ambient_cutter_restrict:
                    o.limit_poly = o.limit_poly.buffer(
                        o.cutter_diameter / 2, resolution=o.optimisation.circle_detail
                    )
            o.ambient = o.ambient.intersection(o.limit_poly)
    o.update_ambient_tag = False


def get_cutter_array(operation, pixsize):
    """Generate a cutter array based on the specified operation and pixel size.

    This function calculates a 2D array representing the cutter shape based
    on the cutter type defined in the operation object. The cutter can be of
    various types such as 'END', 'BALL', 'VCARVE', 'CYLCONE', 'BALLCONE', or
    'CUSTOM'. The function uses geometric calculations to fill the array
    with appropriate values based on the cutter's dimensions and properties.

    Args:
        operation (object): An object containing properties of the cutter, including
            cutter type, diameter, tip angle, and other relevant parameters.
        pixsize (float): The size of each pixel in the generated cutter array.

    Returns:
        numpy.ndarray: A 2D array filled with values representing the cutter shape.
    """

    cutter_type = operation.cutter_type
    r = operation.cutter_diameter / 2 + operation.skin
    res = ceil((r * 2) / pixsize)
    m = res / 2.0
    car = np.full(shape=(res, res), fill_value=-10.0, dtype=float)
    v = Vector((0, 0, 0))
    ps = pixsize

    if cutter_type == "END":
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps

            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps

                if v.length <= r:
                    car.itemset((a, b), 0)

    elif cutter_type in ["BALL", "BALLNOSE"]:
        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps

            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps

                if v.length <= r:
                    z = sin(acos(v.length / r)) * r - r
                    car.itemset((a, b), z)  # [a,b]=z

    elif cutter_type == "VCARVE":
        angle = operation.cutter_tip_angle
        s = tan(pi * (90 - angle / 2) / 180)  # angle in degrees

        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps

            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps

                if v.length <= r:
                    z = -v.length * s
                    car.itemset((a, b), z)

    elif cutter_type == "CYLCONE":
        angle = operation.cutter_tip_angle
        cyl_r = operation.cylcone_diameter / 2
        s = tan(pi * (90 - angle / 2) / 180)  # angle in degrees

        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps

            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps

                if v.length <= r:
                    z = -(v.length - cyl_r) * s

                    if v.length <= cyl_r:
                        z = 0

                    car.itemset((a, b), z)

    elif cutter_type == "BALLCONE":
        angle = radians(operation.cutter_tip_angle) / 2
        ball_r = operation.ball_radius
        cutter_r = operation.cutter_diameter / 2
        conedepth = (cutter_r - ball_r) / tan(angle)
        Ball_R = ball_r / cos(angle)
        D_ofset = ball_r * tan(angle)
        s = tan(pi / 2 - angle)

        for a in range(0, res):
            v.x = (a + 0.5 - m) * ps

            for b in range(0, res):
                v.y = (b + 0.5 - m) * ps

                if v.length <= cutter_r:
                    z = -(v.length - ball_r) * s - Ball_R + D_ofset

                    if v.length <= ball_r:
                        z = sin(acos(v.length / Ball_R)) * Ball_R - Ball_R

                    car.itemset((a, b), z)

    elif cutter_type == "CUSTOM":
        cutob = bpy.data.objects[operation.cutter_object_name]
        scale = ((cutob.dimensions.x / cutob.scale.x) / 2) / r  #
        vstart = Vector((0, 0, -10))
        vend = Vector((0, 0, 10))
        log.info("Sampling Custom Cutter")
        maxz = -1

        for a in range(0, res):
            vstart.x = (a + 0.5 - m) * ps * scale
            vend.x = vstart.x

            for b in range(0, res):
                vstart.y = (b + 0.5 - m) * ps * scale
                vend.y = vstart.y
                v = vend - vstart
                c = cutob.ray_cast(vstart, v, distance=1.70141e38)

                if c[3] != -1:
                    z = -c[1][2] / scale

                    if z > -9:
                        if z > maxz:
                            maxz = z

                        car.itemset((a, b), z)

        car -= maxz

    return car


def check_min_z(o):
    """Check the minimum value based on the specified condition.

    This function evaluates the 'minz_from' attribute of the input object
    'o'. If 'minz_from' is set to 'MATERIAL', it returns the value of
    'min.z'. Otherwise, it returns the value of 'minz'.

    Args:
        o (object): An object that has attributes 'minz_from', 'min', and 'minz'.

    Returns:
        The minimum value, which can be either 'o.min.z' or 'o.min_z' depending
            on the condition.
    """
    if o.min_z_from == "MATERIAL":
        return o.min.z
    else:
        return o.min_z


def get_layers(operation, start_depth, end_depth):
    """Returns a list of layers bounded by start depth and end depth.

    This function calculates the layers between the specified start and end
    depths based on the step down value defined in the operation. If the
    operation is set to use layers, it computes the number of layers by
    dividing the difference between start and end depths by the step down
    value. The function raises an exception if the start depth is lower than
    the end depth.

    Args:
        operation (object): An object that contains the properties `use_layers`,
            `stepdown`, and `maxz` which are used to determine
            how layers are generated.
        start_depth (float): The starting depth for layer calculation.
        end_depth (float): The ending depth for layer calculation.

    Returns:
        list: A list of layers, where each layer is represented as a list
            containing the start and end depths of that layer.

    Raises:
        CamException: If the start depth is lower than the end depth.
    """

    if start_depth < end_depth:
        string = (
            "Start Depth Is Lower than End Depth.\n"
            "if You Have Set a Custom Depth End, It Must Be Lower than Depth Start,\n"
            "and Should Usually Be Negative.\nSet This in the CAM Operation Area Panel."
        )
        log.error("Start Depth Is Lower than End Depth.")
        raise CamException(string)

    if operation.use_layers:
        layers = []
        layer_count = ceil((start_depth - end_depth) / operation.stepdown)

        log.info("-")
        log.info("~ Getting Layer Data ~")
        log.info(f"Start Depth: {start_depth}")
        log.info(f"End Depth: {end_depth}")
        log.info(f"Layers: {layer_count}")
        log.info("-")

        layer_start = operation.max_z

        for x in range(0, layer_count):
            layer_end = round(
                max(start_depth - ((x + 1) * operation.stepdown), end_depth),
                6,
            )
            if int(layer_start * 10**8) != int(layer_end * 10**8):
                # it was possible that with precise same end of operation,
                # last layer was done 2x on exactly same level...
                layers.append([layer_start, layer_end])
            layer_start = layer_end
    else:
        layers = [[round(start_depth, 6), round(end_depth, 6)]]

    return layers


def get_operation_axes(o):
    three_axis = o.machine_axes == "3"
    four_axis = o.machine_axes == "4"
    five_axis = o.machine_axes == "5"

    indexed_four_axis = four_axis and o.strategy_4_axis == "INDEXED"
    indexed_five_axis = five_axis and o.strategy_5_axis == "INDEXED"

    return three_axis, four_axis, five_axis, indexed_four_axis, indexed_five_axis
