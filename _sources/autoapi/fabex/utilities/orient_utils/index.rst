fabex.utilities.orient_utils
============================

.. py:module:: fabex.utilities.orient_utils

.. autoapi-nested-parse::

   Fabex 'orient_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.orient_utils.add_orientation_object
   fabex.utilities.orient_utils.remove_orientation_object
   fabex.utilities.orient_utils.rotation_to_2_axes


Module Contents
---------------

.. py:function:: add_orientation_object(o)

   Set up orientation for a milling object.

   This function creates an orientation object in the Blender scene for
   4-axis and 5-axis milling operations. It checks if an orientation object
   with the specified name already exists, and if not, it adds a new empty
   object of type 'ARROWS'. The function then configures the rotation locks
   and initial rotation angles based on the specified machine axes and
   rotary axis.

   :param o: An object containing properties such as name,
   :type o: object


.. py:function:: remove_orientation_object(o)

   Remove an orientation object from the current Blender scene.

   This function constructs the name of the orientation object based on the
   name of the provided object and attempts to find and delete it from the
   Blender scene. If the orientation object exists, it will be removed
   using the `delob` function.

   :param o: The object whose orientation object is to be removed.
   :type o: Object


.. py:function:: rotation_to_2_axes(e, axescombination)

   Converts an Orientation Object Rotation to Rotation Defined by 2
   Rotational Axes on the Machine.

   This function takes an orientation object and a specified axes
   combination, and computes the angles of rotation around two axes based
   on the provided orientation. It supports different axes combinations for
   indexed machining. The function utilizes vector mathematics to determine
   the angles of rotation and returns them as a tuple.

   :param e: The orientation object representing the rotation.
   :type e: OrientationObject
   :param axescombination: A string indicating the axes combination ('CA' or 'CB').
   :type axescombination: str

   :returns: A tuple containing two angles (float) representing the rotation
             around the specified axes.
   :rtype: tuple


