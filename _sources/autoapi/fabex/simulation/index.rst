fabex.simulation
================

.. py:module:: fabex.simulation

.. autoapi-nested-parse::

   Fabex 'simulation.py' © 2012 Vilem Novak

   Functions to generate a mesh simulation from CAM Chain / Operation data.



Functions
---------

.. autoapisummary::

   fabex.simulation.create_simulation_object
   fabex.simulation.do_simulation
   fabex.simulation.generate_simulation_image
   fabex.simulation.sim_cutter_spot


Module Contents
---------------

.. py:function:: create_simulation_object(name, operations, i)

   Create a simulation object in Blender.
   This function creates a simulation object in Blender with the specified
   name and operations. If an object with the given name already exists, it
   retrieves that object; otherwise, it creates a new plane object and
   applies several modifiers to it. The function also sets the object's
   location and scale based on the provided operations and assigns a
   texture to the object.
   :param name: The name of the simulation object to be created.
   :type name: str
   :param operations: A list of operation objects that contain bounding box information.
   :type operations: list
   :param i: The image to be used as a texture for the simulation object.


.. py:function:: do_simulation(name, operations)
   :async:


   Perform simulation of operations for a 3-axis system.
   This function iterates through a list of operations, retrieves the
   necessary sources for each operation, and computes the bounds for the
   operations. It then generates a simulation image based on the operations
   and their limits, saves the image to a specified path, and finally
   creates a simulation object in Blender using the generated image.
   :param name: The name to be used for the simulation object.
   :type name: str
   :param operations: A list of operations to be simulated.
   :type operations: list


.. py:function:: generate_simulation_image(operations, limits)
   :async:


   Generate a simulation image based on provided operations and limits.
   This function creates a 2D simulation image by processing a series of
   operations that define how the simulation should be conducted. It uses
   the limits provided to determine the boundaries of the simulation area.
   The function calculates the necessary resolution for the simulation
   image based on the specified simulation detail and border width. It
   iterates through each operation, simulating the effect of each operation
   on the image, and updates the shape keys of the corresponding Blender
   object to reflect the simulation results. The final output is a 2D array
   representing the simulated image.

   :param operations: A list of operation objects that contain details
                      about the simulation, including feed rates and other parameters.
   :type operations: list
   :param limits: A tuple containing the minimum and maximum coordinates
                  (minx, miny, minz, maxx, maxy, maxz) that define the simulation
                  boundaries.
   :type limits: tuple

   :returns: A 2D array representing the simulated image.
   :rtype: np.ndarray


.. py:function:: sim_cutter_spot(xs, ys, z, cutterArray, si, getvolume=False)

   Simulates a cutter cutting into stock and optionally returns the volume
   removed.

   This function takes the position of a cutter and modifies a stock image
   by simulating the cutting process. It updates the stock image based on
   the cutter's dimensions and position, ensuring that the stock does not
   go below a certain level defined by the cutter's height. If requested,
   it also calculates and returns the volume of material that has been
   milled away.

   :param xs: The x-coordinate of the cutter's position.
   :type xs: int
   :param ys: The y-coordinate of the cutter's position.
   :type ys: int
   :param z: The height of the cutter.
   :type z: float
   :param cutterArray: A 2D array representing the cutter's shape.
   :type cutterArray: numpy.ndarray
   :param si: A 2D array representing the stock image to be modified.
   :type si: numpy.ndarray
   :param getvolume: If True, the function returns the volume removed. Defaults to False.
   :type getvolume: bool?

   :returns:

             The volume of material removed if `getvolume` is True; otherwise,
                 returns 0.
   :rtype: float


