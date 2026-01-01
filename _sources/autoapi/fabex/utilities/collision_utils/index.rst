fabex.utilities.collision_utils
===============================

.. py:module:: fabex.utilities.collision_utils

.. autoapi-nested-parse::

   Fabex 'collision.py' © 2012 Vilem Novak

   Functions for Bullet and Cutter collision checks.



Functions
---------

.. autoapisummary::

   fabex.utilities.collision_utils.get_cutter_bullet
   fabex.utilities.collision_utils.prepare_bullet_collision
   fabex.utilities.collision_utils.cleanup_bullet_collision
   fabex.utilities.collision_utils.get_sample_bullet
   fabex.utilities.collision_utils.get_sample_bullet_n_axis


Module Contents
---------------

.. py:function:: get_cutter_bullet(o)

   Create a cutter for Rigidbody simulation collisions.

   This function generates a 3D cutter object based on the specified cutter
   type and parameters. It supports various cutter types including 'END',
   'BALLNOSE', 'VCARVE', 'CYLCONE', 'BALLCONE', and 'CUSTOM'. The function
   also applies rigid body physics to the created cutter for realistic
   simulation in Blender.

   :param o: An object containing properties such as cutter_type, cutter_diameter,
             cutter_tip_angle, ball_radius, and cutter_object_name.
   :type o: object

   :returns: The created cutter object with rigid body properties applied.
   :rtype: bpy.types.Object


.. py:function:: prepare_bullet_collision(o)

   Prepares all objects needed for sampling with Bullet collision.

   This function sets up the Bullet physics simulation by preparing the
   specified objects for collision detection. It begins by cleaning up any
   existing rigid bodies that are not part of the 'machine' object. Then,
   it duplicates the collision objects, converts them to mesh if they are
   curves or fonts, and applies necessary modifiers. The function also
   handles the subdivision of long edges and configures the rigid body
   properties for each object. Finally, it scales the 'machine' objects to
   the simulation scale and steps through the simulation frames to ensure
   that all objects are up to date.

   :param o: An object containing properties and settings for
   :type o: Object


.. py:function:: cleanup_bullet_collision(o)

   Clean up bullet collision objects in the scene.

   This function checks for the presence of a 'machine' object in the
   Blender scene and removes any rigid body objects that are not part of
   the 'machine'. If the 'machine' object is present, it scales the machine
   objects up to the simulation scale and adjusts their locations
   accordingly.

   :param o: An object that may be used in the cleanup process (specific usage not
             detailed).

   :returns: This function does not return a value.
   :rtype: None


.. py:function:: get_sample_bullet(cutter, x, y, radius, startz, endz)

   Perform a collision test for a 3-axis milling cutter.

   This function simplifies the collision detection process compared to a
   full 3D test. It utilizes the Blender Python API to perform a convex
   sweep test on the cutter's position within a specified 3D space. The
   function checks for collisions between the cutter and other objects in
   the scene, adjusting for the cutter's radius to determine the effective
   position of the cutter tip.

   :param cutter: The milling cutter object used for the collision test.
   :type cutter: object
   :param x: The x-coordinate of the cutter's position.
   :type x: float
   :param y: The y-coordinate of the cutter's position.
   :type y: float
   :param radius: The radius of the cutter, used to adjust the collision detection.
   :type radius: float
   :param startz: The starting z-coordinate for the collision test.
   :type startz: float
   :param endz: The ending z-coordinate for the collision test.
   :type endz: float

   :returns:

             The adjusted z-coordinate of the cutter tip if a collision is detected;
                 otherwise, returns a value 10 units below the specified endz.
   :rtype: float


.. py:function:: get_sample_bullet_n_axis(cutter, startpoint, endpoint, rotation, cutter_compensation)

   Perform a fully 3D collision test for N-Axis milling.

   This function computes the collision detection between a cutter and a
   specified path in a 3D space. It takes into account the cutter's
   rotation and compensation to accurately determine if a collision occurs
   during the milling process. The function uses Bullet physics for the
   collision detection and returns the adjusted position of the cutter if a
   collision is detected.

   :param cutter: The cutter object used in the milling operation.
   :type cutter: object
   :param startpoint: The starting point of the milling path.
   :type startpoint: Vector
   :param endpoint: The ending point of the milling path.
   :type endpoint: Vector
   :param rotation: The rotation applied to the cutter.
   :type rotation: Euler
   :param cutter_compensation: The compensation factor for the cutter's position.
   :type cutter_compensation: float

   :returns:

             The adjusted position of the cutter if a collision is
                 detected;
                 otherwise, returns None.
   :rtype: Vector or None


