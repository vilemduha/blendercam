fabex.utilities.index_utils
===========================

.. py:module:: fabex.utilities.index_utils

.. autoapi-nested-parse::

   Fabex 'index_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.index_utils.prepare_indexed
   fabex.utilities.index_utils.cleanup_indexed


Module Contents
---------------

.. py:function:: prepare_indexed(o)

   Prepare and index objects in the given collection.

   This function stores the world matrices and parent relationships of the
   objects in the provided collection. It then clears the parent
   relationships while maintaining their transformations, sets the
   orientation of the objects based on a specified orientation object, and
   finally re-establishes the parent-child relationships with the
   orientation object. The function also resets the location and rotation
   of the orientation object to the origin.

   :param o: A collection of objects to be prepared and indexed.
   :type o: ObjectCollection


.. py:function:: cleanup_indexed(operation)

   Clean up indexed operations by updating object orientations and paths.

   This function takes an operation object and updates the orientation of a
   specified object in the scene based on the provided orientation matrix.
   It also sets the location and rotation of a CAM path object to match
   the updated orientation. Additionally, it reassigns parent-child
   relationships for the objects involved in the operation and updates
   their world matrices.

   :param operation: An object containing the necessary data
   :type operation: OperationType


