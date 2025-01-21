"""Fabex 'material_utils.py' © 2012 Vilem Novak
"""

import bpy

from .bounds_utils import get_bounds
from .operation_utils import get_operation_sources


def add_transparent_material(ob, mname, color, alpha):
    """Add a transparent material to a given object.

    This function checks if a material with the specified name already
    exists in the Blender data. If it does, it retrieves that material; if
    not, it creates a new material with the given name and enables the use
    of nodes. The function then assigns the material to the specified
    object, ensuring that it is applied correctly whether the object already
    has materials or not.

    Args:
        ob (bpy.types.Object): The Blender object to which the material will be assigned.
        mname (str): The name of the material to be added or retrieved.
        color (tuple): The RGBA color value for the material (not used in this function).
        alpha (float): The transparency value for the material (not used in this function).
    """

    if mname in bpy.data.materials:
        mat = bpy.data.materials[mname]
    else:
        mat = bpy.data.materials.new(name=mname)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]

        # Assign it to object
        if ob.data.materials:
            ob.data.materials[0] = mat
        else:
            ob.data.materials.append(mat)


def add_material_area_object():
    """Add a material area object to the current Blender scene.

    This function checks if a material area object named 'CAM_material'
    already exists in the current scene. If it does, it retrieves that
    object; if not, it creates a new cube mesh object to serve as the
    material area. The dimensions and location of the object are set based
    on the current CAM operation's bounds. The function also applies
    transformations to ensure the object's location and dimensions are
    correctly set.  The created or retrieved object is configured to be non-
    renderable and non-selectable in the viewport, while still being
    selectable for operations. This is useful for visualizing the working
    area of the CAM without affecting the render output.  Raises:
    None
    """

    s = bpy.context.scene
    operation = s.cam_operations[s.cam_active_operation]
    get_operation_sources(operation)
    get_bounds(operation)

    ao = bpy.context.active_object
    if s.objects.get("CAM_material") is not None:
        o = s.objects["CAM_material"]
    else:
        bpy.ops.mesh.primitive_cube_add(
            align="WORLD", enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0)
        )
        o = bpy.context.active_object
        o.name = "CAM_material"
        o.data.name = "CAM_material"
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        # addTranspMat(o, 'blue_transparent', (0.458695, 0.794658, 0.8), 0.1)
        o.display_type = "BOUNDS"
        o.hide_render = True
        o.hide_select = True
        o.select_set(state=True, view_layer=None)
    # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    o.dimensions = bpy.context.scene.cam_machine.working_area

    o.dimensions = (
        operation.max.x - operation.min.x,
        operation.max.y - operation.min.y,
        operation.max.z - operation.min.z,
    )
    o.location = (operation.min.x, operation.min.y, operation.max.z)
    if ao is not None:
        ao.select_set(True)
    # else:
    #     bpy.context.scene.objects.active = None


def update_material(self, context):
    """Update the material in the given context.

    This method is responsible for updating the material based on the
    provided context. It performs necessary operations to ensure that the
    material is updated correctly. Currently, it prints a message indicating
    the update process and calls the `addMaterialAreaObject` function to
    handle additional material area object updates.

    Args:
        context: The context in which the material update is performed.
    """

    print("Update Material")
    add_material_area_object()


# def update_material(self, context):
#     add_material_area_object()
