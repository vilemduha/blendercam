fabex.utilities.curve_utils
===========================

.. py:module:: fabex.utilities.curve_utils


Functions
---------

.. autoapisummary::

   fabex.utilities.curve_utils.curve_to_shapely
   fabex.utilities.curve_utils.mesh_from_curve
   fabex.utilities.curve_utils.mesh_from_curve_to_chunk
   fabex.utilities.curve_utils.curve_to_chunks


Module Contents
---------------

.. py:function:: curve_to_shapely(cob, use_modifiers=False)

   Convert a curve object to Shapely polygons.

   This function takes a curve object and converts it into a list of
   Shapely polygons. It first breaks the curve into chunks and then
   transforms those chunks into Shapely-compatible polygon representations.
   The `use_modifiers` parameter allows for additional processing of the
   curve before conversion, depending on the specific requirements of the
   application.

   :param cob: The curve object to be converted.
   :param use_modifiers: A flag indicating whether to apply modifiers
                         during the conversion process. Defaults to False.
   :type use_modifiers: bool

   :returns: A list of Shapely polygons created from the curve object.
   :rtype: list


.. py:function:: mesh_from_curve(o, use_modifiers=False)

   Create a Mesh Object from a Curve Object

   This function converts a curve object into a mesh object, maintaining
   parent-child relationships, applying transforms, deleting the old
   curve object and returning the mesh as the active object.


.. py:function:: mesh_from_curve_to_chunk(object)

   Convert a Curve Object to a Mesh and then to a CAM path chunk

   This function uses 'mesh_from_curve' and 'CamPathChunkBuilder' to convert
   a Curve object into a Mesh, then sample the points and edges of the mesh to
   create and return a list of CAM path chunks.


.. py:function:: curve_to_chunks(o, use_modifiers=False)

   Convert a Curve Object into CAM path chunks

   This function uses 'mesh_from_curve' and 'mesh_from_curve_to_chunk' to
   convert a Curve object into CAM path chunks, deletes the Curve object
   and returns the CAM path chunks.


