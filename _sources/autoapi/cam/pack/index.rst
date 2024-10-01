cam.pack
========

.. py:module:: cam.pack

.. autoapi-nested-parse::

   BlenderCAM 'pack.py' © 2012 Vilem Novak

   Takes all selected curves, converts them to polygons, offsets them by the pre-set margin
   then chooses a starting location possibly inside the already occupied area and moves and rotates the
   polygon out of the occupied area if one or more positions are found where the poly doesn't overlap,
   it is placed and added to the occupied area - allpoly
   Very slow and STUPID, a collision algorithm would be much much faster...



Classes
-------

.. autoapisummary::

   cam.pack.PackObjectsSettings


Functions
---------

.. autoapisummary::

   cam.pack.srotate
   cam.pack.packCurves


Module Contents
---------------

.. py:function:: srotate(s, r, x, y)

   Rotate a polygon's coordinates around a specified point.

   This function takes a polygon and rotates its exterior coordinates
   around a given point (x, y) by a specified angle (r) in radians. It uses
   the Euler rotation to compute the new coordinates for each point in the
   polygon's exterior. The resulting coordinates are then used to create a
   new polygon.

   :param s: The polygon to be rotated.
   :type s: shapely.geometry.Polygon
   :param r: The angle of rotation in radians.
   :type r: float
   :param x: The x-coordinate of the point around which to rotate.
   :type x: float
   :param y: The y-coordinate of the point around which to rotate.
   :type y: float

   :returns: A new polygon with the rotated coordinates.
   :rtype: shapely.geometry.Polygon


.. py:function:: packCurves()

   Pack selected curves into a defined area based on specified settings.

   This function organizes selected curve objects in Blender by packing
   them into a specified area defined by the camera pack settings. It
   calculates the optimal positions for each curve while considering
   parameters such as sheet size, fill direction, distance, tolerance, and
   rotation. The function utilizes geometric operations to ensure that the
   curves do not overlap and fit within the defined boundaries. The packed
   curves are then transformed and their properties are updated
   accordingly.  The function performs the following steps: 1. Activates
   speedup features if available. 2. Retrieves packing settings from the
   current scene. 3. Processes each selected object to create polygons from
   curves. 4. Attempts to place each polygon within the defined area while
   avoiding    overlaps and respecting the specified fill direction. 5.
   Outputs the final arrangement of polygons.


.. py:class:: PackObjectsSettings

   Bases: :py:obj:`bpy.types.PropertyGroup`


   stores all data for machines


   .. py:attribute:: sheet_fill_direction
      :type:  EnumProperty(name='Fill Direction', items=(('X', 'X', 'Fills sheet in X axis direction'), ('Y', 'Y', 'Fills sheet in Y axis direction')), description='Fill direction of the packer algorithm', default='Y')


   .. py:attribute:: sheet_x
      :type:  FloatProperty(name='X Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: sheet_y
      :type:  FloatProperty(name='Y Size', description='Sheet size', min=0.001, max=10, default=0.5, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: distance
      :type:  FloatProperty(name='Minimum Distance', description='Minimum distance between objects(should be at least cutter diameter!)', min=0.001, max=10, default=0.01, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: tolerance
      :type:  FloatProperty(name='Placement Tolerance', description='Tolerance for placement: smaller value slower placemant', min=0.001, max=0.02, default=0.005, precision=constants.PRECISION, unit='LENGTH')


   .. py:attribute:: rotate
      :type:  BoolProperty(name='Enable Rotation', description='Enable rotation of elements', default=True)


   .. py:attribute:: rotate_angle
      :type:  FloatProperty(name='Placement Angle Rotation Step', description='Bigger rotation angle, faster placemant', default=0.19635 * 4, min=pi / 180, max=pi, precision=5, subtype='ANGLE', unit='ROTATION')


