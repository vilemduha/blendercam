fabex.utilities.material_utils
==============================

.. py:module:: fabex.utilities.material_utils

.. autoapi-nested-parse::

   Fabex 'material_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.material_utils.add_transparent_material
   fabex.utilities.material_utils.add_material_area_object
   fabex.utilities.material_utils.update_material


Module Contents
---------------

.. py:function:: add_transparent_material(ob, mname, color, alpha)

   Add a transparent material to a given object.

   This function checks if a material with the specified name already
   exists in the Blender data. If it does, it retrieves that material; if
   not, it creates a new material with the given name and enables the use
   of nodes. The function then assigns the material to the specified
   object, ensuring that it is applied correctly whether the object already
   has materials or not.

   :param ob: The Blender object to which the material will be assigned.
   :type ob: bpy.types.Object
   :param mname: The name of the material to be added or retrieved.
   :type mname: str
   :param color: The RGBA color value for the material (not used in this function).
   :type color: tuple
   :param alpha: The transparency value for the material (not used in this function).
   :type alpha: float


.. py:function:: add_material_area_object()

   Add a material area object to the current Blender scene.

   This function checks if a material area object named 'CAM_Material'
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


.. py:function:: update_material(self, context)

   Update the material in the given context.

   This method is responsible for updating the material based on the
   provided context. It performs necessary operations to ensure that the
   material is updated correctly. Currently, it prints a message indicating
   the update process and calls the `addMaterialAreaObject` function to
   handle additional material area object updates.

   :param context: The context in which the material update is performed.


