fabex.bridges
=============

.. py:module:: fabex.bridges

.. autoapi-nested-parse::

   Fabex 'bridges.py' © 2012 Vilem Novak

   Functions to add Bridges / Tabs to meshes or curves.
   Called with Operators defined in 'ops.py'



Functions
---------

.. autoapisummary::

   fabex.bridges.add_bridge
   fabex.bridges.add_auto_bridges
   fabex.bridges.get_bridges_poly
   fabex.bridges.use_bridges
   fabex.bridges.auto_cut_bridge


Module Contents
---------------

.. py:function:: add_bridge(x, y, rot, size_x, size_y)

   Add a bridge mesh object to the scene.

   This function creates a bridge by adding a primitive plane to the
   Blender scene, adjusting its dimensions, and then converting it into a
   curve. The bridge is positioned based on the provided coordinates and
   rotation. The size of the bridge is determined by the `sizex` and
   `sizey` parameters.

   :param x: The x-coordinate for the bridge's location.
   :type x: float
   :param y: The y-coordinate for the bridge's location.
   :type y: float
   :param rot: The rotation angle around the z-axis in radians.
   :type rot: float
   :param sizex: The width of the bridge.
   :type sizex: float
   :param sizey: The height of the bridge.
   :type sizey: float

   :returns: The created bridge object.
   :rtype: bpy.types.Object


.. py:function:: add_auto_bridges(o)

   Attempt to add auto bridges as a set of curves.

   This function creates a collection of bridges based on the provided
   object. It checks if a collection for bridges already exists; if not, it
   creates a new one. The function then iterates through the objects in the
   input object, processing curves and meshes to generate bridge
   geometries. For each geometry, it calculates the necessary points and
   adds bridges at various orientations based on the geometry's bounds.

   :param o: An object containing properties such as
             bridges_collection_name, bridges_width, and cutter_diameter,
             along with a list of objects to process.
   :type o: object

   :returns:

             This function does not return a value but modifies the
                 Blender context by adding bridge objects to the specified
                 collection.
   :rtype: None


.. py:function:: get_bridges_poly(o)

   Generate and prepare bridge polygons from a Blender object.

   This function checks if the provided object has an attribute for bridge
   polygons. If not, it retrieves the bridge collection, selects all curve
   objects within that collection, duplicates them, and joins them into a
   single object. The resulting shape is then converted to a Shapely
   geometry. The function buffers the resulting polygon to account for the
   cutter diameter and prepares the boundary and polygon for further
   processing.

   :param o: An object containing properties related to bridge
   :type o: object


.. py:function:: use_bridges(ch, o)

   Add bridges to chunks using a collection of bridge objects.

   This function takes a collection of bridge objects and uses the curves
   within it to create bridges over the specified chunks. It calculates the
   necessary points for the bridges based on the height and geometry of the
   chunks and the bridge objects. The function also handles intersections
   with the bridge polygon and adjusts the points accordingly. Finally, it
   generates a mesh for the bridges and converts it into a curve object in
   Blender.

   :param ch: The chunk object to which bridges will be added.
   :type ch: Chunk
   :param o: An object containing options such as bridge height,
             collection name, and other parameters.
   :type o: ObjectOptions

   :returns:

             The function modifies the chunk object in place and does not return a
                 value.
   :rtype: None


.. py:function:: auto_cut_bridge(o)

   Automatically processes a bridge collection.

   This function retrieves a bridge collection by its name from the
   provided object and checks if there are any objects within that
   collection. If there are objects present, it prints "bridges" to the
   console. This function is useful for managing and processing bridge
   collections in a 3D environment.

   :param o: An object that contains the attribute
   :type o: object

   :returns: This function does not return any value.
   :rtype: None


