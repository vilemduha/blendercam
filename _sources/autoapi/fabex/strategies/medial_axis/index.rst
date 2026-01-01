fabex.strategies.medial_axis
============================

.. py:module:: fabex.strategies.medial_axis


Functions
---------

.. autoapisummary::

   fabex.strategies.medial_axis.medial_axis


Module Contents
---------------

.. py:function:: medial_axis(o)
   :async:


   Generate the medial axis for a given operation.

   This function computes the medial axis of the specified operation, which
   involves processing various cutter types and their parameters. It starts
   by removing any existing medial mesh, then calculates the maximum depth
   based on the cutter type and its properties. The function refines curves
   and computes the Voronoi diagram for the points derived from the
   operation's silhouette. It filters points and edges based on their
   positions relative to the computed shapes, and generates a mesh
   representation of the medial axis. Finally, it handles layers and
   optionally adds a pocket operation if specified.

   :param o: An object containing parameters for the operation, including
             cutter type, dimensions, and other relevant properties.
   :type o: Operation

   :returns: A dictionary indicating the completion status of the operation.
   :rtype: dict

   :raises CamException: If an unsupported cutter type is provided or if the input curve
       is not closed.


