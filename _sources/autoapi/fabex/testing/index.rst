fabex.testing
=============

.. py:module:: fabex.testing

.. autoapi-nested-parse::

   Fabex 'testing.py' © 2012 Vilem Novak

   Functions for automated testing.



Attributes
----------

.. autoapisummary::

   fabex.testing.tests
   fabex.testing.p


Functions
---------

.. autoapisummary::

   fabex.testing.addTestCurve
   fabex.testing.addTestMesh
   fabex.testing.deleteFirstVert
   fabex.testing.testCalc
   fabex.testing.testCutout
   fabex.testing.testPocket
   fabex.testing.testParallel
   fabex.testing.testWaterline
   fabex.testing.testSimulation
   fabex.testing.cleanUp
   fabex.testing.testOperation
   fabex.testing.testAll


Module Contents
---------------

.. py:function:: addTestCurve(loc)

   Add a test curve to the Blender scene.

   This function creates a Bezier circle at the specified location in the
   Blender scene. It first adds a primitive Bezier circle, then enters edit
   mode to duplicate the circle twice, resizing each duplicate to half its
   original size. The function ensures that the transformations are applied
   in the global orientation and does not use proportional editing.

   :param loc: A tuple representing the (x, y, z) coordinates where
               the Bezier circle will be added in the 3D space.
   :type loc: tuple


.. py:function:: addTestMesh(loc)

   Add a test mesh to the Blender scene.

   This function creates a monkey mesh and a plane mesh at the specified
   location in the Blender scene. It first adds a monkey mesh with a small
   radius, rotates it, and applies the transformation. Then, it toggles
   into edit mode, adds a plane mesh, resizes it, and translates it
   slightly before toggling back out of edit mode.

   :param loc: A tuple representing the (x, y, z) coordinates where
               the meshes will be added in the Blender scene.
   :type loc: tuple


.. py:function:: deleteFirstVert(ob)

   Delete the first vertex of a given object.

   This function activates the specified object, enters edit mode,
   deselects all vertices, selects the first vertex, and then deletes it.
   The function ensures that the object is properly updated after the
   deletion.

   :param ob: The Blender object from which the first
   :type ob: bpy.types.Object


.. py:function:: testCalc(o)

   Test the calculation of the CAM path for a given object.

   This function invokes the Blender operator to calculate the CAM path
   for the specified object and then deletes the first vertex of that
   object. It is intended to be used within a Blender environment where the
   bpy module is available.

   :param o: The Blender object for which the CAM path is to be calculated.
   :type o: Object


.. py:function:: testCutout(pos)

   Test the cutout functionality in the scene.

   This function adds a test curve based on the provided position, performs
   a CAM operation, and sets the strategy to 'CUTOUT'. It then calls the
   `testCalc` function to perform further calculations on the CAM
   operation.

   :param pos: A tuple containing the x and y coordinates for the
               position of the test curve.
   :type pos: tuple


.. py:function:: testPocket(pos)

   Test the pocket operation in a 3D scene.

   This function sets up a pocket operation by adding a test curve based on
   the provided position. It configures the CAM operation settings for
   the pocket strategy, enabling helix entry and tangential retraction.
   Finally, it performs a calculation based on the configured operation.

   :param pos: A tuple containing the x and y coordinates for
               the position of the test curve.
   :type pos: tuple


.. py:function:: testParallel(pos)

   Test the parallel functionality of the CAM operations.

   This function adds a test mesh at a specified position and then performs
   CAM operations in the Blender environment. It sets the ambient
   behavior of the CAM operation to 'AROUND' and configures the material
   radius around the model. Finally, it calculates the CAM path based on
   the current scene settings.

   :param pos: A tuple containing the x and y coordinates for
               positioning the test mesh.
   :type pos: tuple


.. py:function:: testWaterline(pos)

   Test the waterline functionality in the scene.

   This function adds a test mesh at a specified position and then performs
   a CAM operation with the strategy set to 'WATERLINE'. It also
   configures the optimization pixel size for the operation. The function
   is intended for use in a 3D environment where waterline calculations are
   necessary for rendering or simulation.

   :param pos: A tuple containing the x and y coordinates for
               the position of the test mesh.
   :type pos: tuple


.. py:function:: testSimulation()

   Testsimulation function.


.. py:function:: cleanUp()

   Clean up the Blender scene by removing all objects and CAM
   operations.

   This function selects all objects in the current Blender scene and
   deletes them. It also removes any CAM operations that are present in
   the scene. This is useful for resetting the scene to a clean state
   before performing further operations.


.. py:function:: testOperation(i)

   Test the operation of a CAM path in Blender.

   This function tests a specific CAM operation by comparing the
   generated CAM path with an existing reference path. It retrieves the
   CAM operation from the scene and checks if the generated path matches
   the expected path in terms of vertex count and positions. If there is no
   existing reference path, it marks the new result as comparable. The
   function generates a report detailing the results of the comparison,
   including any discrepancies found.

   :param i: The index of the CAM operation to test.
   :type i: int

   :returns: A report summarizing the results of the operation test.
   :rtype: str


.. py:function:: testAll()

   Run tests on all CAM operations in the current scene.

   This function iterates through all CAM operations defined in the
   current Blender scene and executes a test for each operation. The
   results of these tests are collected into a report string, which is then
   printed to the console. This is useful for verifying the functionality
   of CAM operations within the Blender environment.


.. py:data:: tests

.. py:data:: p

