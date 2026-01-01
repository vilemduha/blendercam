fabex.strategies.drill
======================

.. py:module:: fabex.strategies.drill


Functions
---------

.. autoapisummary::

   fabex.strategies.drill.drill


Module Contents
---------------

.. py:function:: drill(o)
   :async:


   Perform a drilling operation on the specified objects.

   This function iterates through the objects in the provided context,
   activating each object and applying transformations. It duplicates the
   objects and processes them based on their type (CURVE or MESH). For
   CURVE objects, it calculates the bounding box and center points of the
   splines and bezier points, and generates chunks based on the specified
   drill type. For MESH objects, it generates chunks from the vertices. The
   function also manages layers and chunk depths for the drilling
   operation.

   :param o: An object containing properties and methods required
             for the drilling operation, including a list of
             objects to drill, drill type, and depth parameters.
   :type o: object

   :returns:

             This function does not return a value but performs operations
                 that modify the state of the Blender context.
   :rtype: None


