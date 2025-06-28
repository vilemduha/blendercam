fabex.utilities.bounds_utils
============================

.. py:module:: fabex.utilities.bounds_utils

.. autoapi-nested-parse::

   Fabex 'bounds_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.bounds_utils.get_bounds_worldspace
   fabex.utilities.bounds_utils.get_spline_bounds
   fabex.utilities.bounds_utils.get_bounds
   fabex.utilities.bounds_utils.get_bounds_multiple
   fabex.utilities.bounds_utils.position_object


Module Contents
---------------

.. py:function:: get_bounds_worldspace(obs, use_modifiers=False)

   Get the bounding box of a list of objects in world space.

   This function calculates the minimum and maximum coordinates that
   encompass all the specified objects in the 3D world space. It iterates
   through each object, taking into account their transformations and
   modifiers if specified. The function supports different object types,
   including meshes and fonts, and handles the conversion of font objects
   to mesh format for accurate bounding box calculations.

   :param obs: A list of Blender objects to calculate bounds for.
   :type obs: list
   :param use_modifiers: If True, apply modifiers to the objects
                         before calculating bounds. Defaults to False.
   :type use_modifiers: bool

   :returns:

             A tuple containing the minimum and maximum coordinates
                 in the format (minx, miny, minz, maxx, maxy, maxz).
   :rtype: tuple

   :raises CamException: If an object type does not support CAM operations.


.. py:function:: get_spline_bounds(ob, curve)

   Get the bounding box of a spline object.

   This function calculates the minimum and maximum coordinates (x, y, z)
   of the given spline object by iterating through its bezier points and
   regular points. It transforms the local coordinates to world coordinates
   using the object's transformation matrix. The resulting bounds can be
   used for various purposes, such as collision detection or rendering.

   :param ob: The object containing the spline whose bounds are to be calculated.
   :type ob: Object
   :param curve: The curve object that contains the bezier points and regular points.
   :type curve: Curve

   :returns: A tuple containing the minimum and maximum coordinates in the
             format (minx, miny, minz, maxx, maxy, maxz).
   :rtype: tuple


.. py:function:: get_bounds(o)

   Calculate the bounding box for a given object.

   This function determines the minimum and maximum coordinates of an
   object's bounding box based on its geometry source. It handles different
   geometry types such as OBJECT, COLLECTION, and CURVE. The function also
   considers material properties and image cropping if applicable. The
   bounding box is adjusted according to the object's material settings and
   the optimization parameters defined in the object.

   :param o: An object containing geometry and material properties, as well as
             optimization settings.
   :type o: object

   :returns:

             This function modifies the input object in place and does not return a
                 value.
   :rtype: None


.. py:function:: get_bounds_multiple(operations)

   Gets bounds of multiple operations for simulations or rest milling.

   This function iterates through a list of operations to determine the
   minimum and maximum bounds in three-dimensional space (x, y, z). It
   initializes the bounds to extreme values and updates them based on the
   bounds of each operation. The function is primarily intended for use in
   simulations or rest milling processes, although it is noted that the
   implementation may not be optimal.

   :param operations: A list of operation objects, each containing
                      'min' and 'max' attributes with 'x', 'y',
                      and 'z' coordinates.
   :type operations: list

   :returns:

             A tuple containing the minimum and maximum bounds in the
                 order (minx, miny, minz, maxx, maxy, maxz).
   :rtype: tuple


.. py:function:: position_object(operation)

   Position an object based on specified operation parameters.

   This function adjusts the location of a Blender object according to the
   provided operation settings. It calculates the bounding box of the
   object in world space and modifies its position based on the material's
   center settings and specified z-positioning (BELOW, ABOVE, or CENTERED).
   The function also applies transformations to the object if it is not of
   type 'CURVE'.

   :param operation: An object containing parameters for positioning,
                     including object_name, use_modifiers, and material
                     settings.
   :type operation: OperationType


