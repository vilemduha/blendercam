cam.polygon_utils_cam
=====================

.. py:module:: cam.polygon_utils_cam

.. autoapi-nested-parse::

   BlenderCAM 'polygon_utils_cam.py' © 2012 Vilem Novak

   Functions to handle shapely operations and conversions - curve, coords, polygon



Attributes
----------

.. autoapisummary::

   cam.polygon_utils_cam.SHAPELY


Functions
---------

.. autoapisummary::

   cam.polygon_utils_cam.Circle
   cam.polygon_utils_cam.shapelyRemoveDoubles
   cam.polygon_utils_cam.shapelyToMultipolygon
   cam.polygon_utils_cam.shapelyToCoords
   cam.polygon_utils_cam.shapelyToCurve


Module Contents
---------------

.. py:data:: SHAPELY
   :value: True


.. py:function:: Circle(r, np)

   Generate a circle defined by a given radius and number of points.

   This function creates a polygon representing a circle by generating a
   list of points based on the specified radius and the number of points
   (np). It uses vector rotation to calculate the coordinates of each point
   around the circle. The resulting points are then used to create a
   polygon object.

   :param r: The radius of the circle.
   :type r: float
   :param np: The number of points to generate around the circle.
   :type np: int

   :returns: A polygon object representing the circle.
   :rtype: spolygon.Polygon


.. py:function:: shapelyRemoveDoubles(p, optimize_threshold)

   Remove duplicate points from the boundary of a shape.

   This function simplifies the boundary of a given shape by removing
   duplicate points using the Ramer-Douglas-Peucker algorithm. It iterates
   through each contour of the shape, applies the simplification, and adds
   the resulting contours to a new shape. The optimization threshold can be
   adjusted to control the level of simplification.

   :param p: The shape object containing boundaries to be simplified.
   :type p: Shape
   :param optimize_threshold: A threshold value that influences the
                              simplification process.
   :type optimize_threshold: float

   :returns: A new shape object with simplified boundaries.
   :rtype: Shape


.. py:function:: shapelyToMultipolygon(anydata)

   Convert a Shapely geometry to a MultiPolygon.

   This function takes a Shapely geometry object and converts it to a
   MultiPolygon. If the input geometry is already a MultiPolygon, it
   returns it as is. If the input is a Polygon and not empty, it wraps the
   Polygon in a MultiPolygon. If the input is an empty Polygon, it returns
   an empty MultiPolygon. For any other geometry type, it prints a message
   indicating that the conversion was aborted and returns an empty
   MultiPolygon.

   :param anydata: A Shapely geometry object
   :type anydata: shapely.geometry.base.BaseGeometry

   :returns: A MultiPolygon representation of the input
             geometry.
   :rtype: shapely.geometry.MultiPolygon


.. py:function:: shapelyToCoords(anydata)

   Convert a Shapely geometry object to a list of coordinates.

   This function takes a Shapely geometry object and extracts its
   coordinates based on the geometry type. It handles various types of
   geometries including Polygon, MultiPolygon, LineString, MultiLineString,
   and GeometryCollection. If the geometry is empty or of type MultiPoint,
   it returns an empty list. The coordinates are returned in a nested list
   format, where each sublist corresponds to the exterior or interior
   coordinates of the geometries.

   :param anydata: A Shapely geometry object
   :type anydata: shapely.geometry.base.BaseGeometry

   :returns: A list of coordinates extracted from the input geometry.
             The structure of the list depends on the geometry type.
   :rtype: list


.. py:function:: shapelyToCurve(name, p, z, cyclic=True)

   Create a 3D curve object in Blender from a Shapely geometry.

   This function takes a Shapely geometry and converts it into a 3D curve
   object in Blender. It extracts the coordinates from the Shapely geometry
   and creates a new curve object with the specified name. The curve is
   created in the 3D space at the given z-coordinate, with a default weight
   for the points.

   :param name: The name of the curve object to be created.
   :type name: str
   :param p: A Shapely geometry object from which to extract
             coordinates.
   :type p: shapely.geometry
   :param z: The z-coordinate for all points of the curve.
   :type z: float

   :returns: The newly created curve object in Blender.
   :rtype: bpy.types.Object


