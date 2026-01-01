fabex.strategies.project_curve
==============================

.. py:module:: fabex.strategies.project_curve


Functions
---------

.. autoapisummary::

   fabex.strategies.project_curve.projected_curve


Module Contents
---------------

.. py:function:: projected_curve(o)
   :async:


   Project a curve onto another curve object.

   This function takes a source object and a target object, both of which
   are expected to be curve objects. It projects the points of the source
   curve onto the target curve, adjusting the start and end points based on
   specified extensions. The resulting projected points are stored in the
   source object's path samples.

   :param s: The source object containing the curve to be projected.
   :type s: object
   :param o: An object containing references to the curve objects
             involved in the projection.
   :type o: object

   :returns:

             This function does not return a value; it modifies the
                 source object's path samples in place.
   :rtype: None

   :raises CamException: If the target curve is not of type 'CURVE'.


