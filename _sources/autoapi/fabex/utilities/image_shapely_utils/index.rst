fabex.utilities.image_shapely_utils
===================================

.. py:module:: fabex.utilities.image_shapely_utils


Functions
---------

.. autoapisummary::

   fabex.utilities.image_shapely_utils.image_to_shapely


Module Contents
---------------

.. py:function:: image_to_shapely(o, i, with_border=False)

   Convert an image to Shapely polygons.

   This function takes an image and converts it into a series of Shapely
   polygon objects. It first processes the image into chunks and then
   transforms those chunks into polygon geometries. The `with_border`
   parameter allows for the inclusion of borders in the resulting polygons.

   :param o: The input image to be processed.
   :param i: Additional input parameters for processing the image.
   :param with_border: A flag indicating whether to include
                       borders in the resulting polygons. Defaults to False.
   :type with_border: bool

   :returns:

             A list of Shapely polygon objects created from the
                 image chunks.
   :rtype: list


