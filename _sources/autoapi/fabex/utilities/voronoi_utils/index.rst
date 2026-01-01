fabex.utilities.voronoi_utils
=============================

.. py:module:: fabex.utilities.voronoi_utils

.. autoapi-nested-parse::

   Fabex 'voronoi.py'

   Voronoi diagram calculator/ Delaunay triangulator

   - Voronoi Diagram Sweepline algorithm and C code by Steven Fortune, 1987, http://ect.bell-labs.com/who/sjf/
   - Python translation to file voronoi.py by Bill Simons, 2005, http://www.oxfish.com/
   - Additional changes for QGIS by Carson Farmer added November 2010
   - 2012 Ported to Python 3 and additional clip functions by domlysz at gmail.com

   Calculate Delaunay triangulation or the Voronoi polygons for a set of
   2D input points.

   Derived from code bearing the following notice:

   The author of this software is Steven Fortune.  Copyright (c) 1994 by AT&T
   Bell Laboratories.
   Permission to use, copy, modify, and distribute this software for any
   purpose without fee is hereby granted, provided that this entire notice
   is included in all copies of any software which is or includes a copy
   or modification of this software and in all copies of the supporting
   documentation for such software.
   THIS SOFTWARE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
   WARRANTY.  IN PARTICULAR, NEITHER THE AUTHORS NOR AT&T MAKE ANY
   REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY
   OF THIS SOFTWARE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.

   Comments were incorporated from Shane O'Sullivan's translation of the
   original code into C++ (http://mapviewer.skynet.ie/voronoi.html)

   Steve Fortune's homepage: http://netlib.bell-labs.com/cm/cs/who/sjf/index.html



Classes
-------

.. autoapisummary::

   fabex.utilities.voronoi_utils.Context
   fabex.utilities.voronoi_utils.Site
   fabex.utilities.voronoi_utils.Edge
   fabex.utilities.voronoi_utils.Halfedge
   fabex.utilities.voronoi_utils.EdgeList
   fabex.utilities.voronoi_utils.PriorityQueue
   fabex.utilities.voronoi_utils.SiteList


Functions
---------

.. autoapisummary::

   fabex.utilities.voronoi_utils.voronoi
   fabex.utilities.voronoi_utils.is_equal
   fabex.utilities.voronoi_utils.compute_voronoi_diagram
   fabex.utilities.voronoi_utils.format_edges_output
   fabex.utilities.voronoi_utils.format_polygons_output
   fabex.utilities.voronoi_utils.compute_delaunay_triangulation


Module Contents
---------------

.. py:class:: Context

   Bases: :py:obj:`object`


   .. py:attribute:: doPrint
      :value: 0



   .. py:attribute:: debug
      :value: 0



   .. py:attribute:: extent
      :value: ()



   .. py:attribute:: triangulate
      :value: False



   .. py:attribute:: vertices
      :value: []



   .. py:attribute:: lines
      :value: []



   .. py:attribute:: edges
      :value: []



   .. py:attribute:: triangles
      :value: []



   .. py:attribute:: polygons


   .. py:method:: get_clip_edges()

      Get the clipped edges based on the current extent.

      This function iterates through the edges of a geometric shape and
      determines which edges are within the specified extent. It handles both
      finite and infinite lines, clipping them as necessary to fit within the
      defined boundaries. For finite lines, it checks if both endpoints are
      within the extent, and if not, it calculates the intersection points
      using the line equations. For infinite lines, it checks if at least one
      endpoint is within the extent and clips accordingly.

      :returns:

                A list of tuples, where each tuple contains two points representing the
                    clipped edges.
      :rtype: list



   .. py:method:: get_clip_polygons(closePoly)

      Get clipped polygons based on the provided edges.

      This function processes a set of polygons defined by their edges and
      vertices, clipping them according to the specified extent. It checks
      whether each edge is finite or infinite and determines if the endpoints
      of each edge are within the defined extent. If they are not, the
      function calculates the intersection points with the extent boundaries.
      The resulting clipped edges are then used to create polygons, which are
      returned as a dictionary. The user can specify whether to close the
      polygons or leave them open.

      :param closePoly: A flag indicating whether to close the polygons.
      :type closePoly: bool

      :returns:

                A dictionary where keys are polygon indices and values are lists of
                    points defining the clipped polygons.
      :rtype: dict



   .. py:method:: clip_line(x1, y1, equation, leftDir)

      Clip a line segment defined by its endpoints against a bounding box.

      This function calculates the intersection points of a line defined by
      the given equation with the bounding box defined by the extent of the
      object. Depending on the direction specified (left or right), it will
      return the appropriate intersection point that lies within the bounds.

      :param x1: The x-coordinate of the first endpoint of the line.
      :type x1: float
      :param y1: The y-coordinate of the first endpoint of the line.
      :type y1: float
      :param equation: A tuple containing the coefficients (a, b, c) of
                       the line equation in the form ax + by + c = 0.
      :type equation: tuple
      :param leftDir: A boolean indicating the direction to clip the line.
                      If True, clip towards the left; otherwise, clip
                      towards the right.
      :type leftDir: bool

      :returns: The coordinates of the clipped point as (x, y).
      :rtype: tuple



   .. py:method:: in_extent(x, y)

      Check if a point is within the defined extent.

      This function determines whether the given coordinates (x, y) fall
      within the boundaries defined by the extent of the object. The extent is
      defined by its minimum and maximum x and y values (xmin, xmax, ymin,
      ymax). The function returns True if the point is within these bounds,
      and False otherwise.

      :param x: The x-coordinate of the point to check.
      :type x: float
      :param y: The y-coordinate of the point to check.
      :type y: float

      :returns: True if the point (x, y) is within the extent, False otherwise.
      :rtype: bool



   .. py:method:: order_points(edges)

      Order points to form a polygon.

      This function takes a list of edges, where each edge is represented as a
      pair of points, and orders the points to create a polygon. It identifies
      the starting and ending points of the polygon and ensures that the
      points are connected in the correct order. If all points are duplicates,
      it recognizes that the polygon is complete and handles it accordingly.

      :param edges: A list of edges, where each edge is a tuple or list containing two
                    points.
      :type edges: list

      :returns:

                A tuple containing:
                    - list: The ordered list of polygon points.
                    - bool: A flag indicating whether the polygon is complete.
      :rtype: tuple



   .. py:method:: set_clip_buffer(xpourcent, ypourcent)

      Set the clipping buffer based on percentage adjustments.

      This function modifies the clipping extent of an object by adjusting its
      boundaries according to the specified percentage values for both the x
      and y axes. It calculates the new minimum and maximum values for the x
      and y coordinates by applying the given percentages to the current
      extent.

      :param xpourcent: The percentage adjustment for the x-axis.
      :type xpourcent: float
      :param ypourcent: The percentage adjustment for the y-axis.
      :type ypourcent: float

      :returns: This function does not return a value; it modifies the
                object's extent in place.
      :rtype: None



   .. py:method:: out_site(s)

      Handle output for a site object.

      This function processes the output based on the current settings of the
      instance. If debugging is enabled, it prints the site number and its
      coordinates. If triangulation is enabled, no action is taken. If
      printing is enabled, it prints the coordinates of the site.

      :param s: An object representing a site, which should have
                attributes 'sitenum', 'x', and 'y'.
      :type s: object

      :returns: This function does not return a value.
      :rtype: None



   .. py:method:: out_vertex(s)

      Add a vertex to the list of vertices.

      This function appends the coordinates of a given vertex to the internal
      list of vertices. Depending on the state of the debug, triangulate, and
      doPrint flags, it may also print debug information or vertex coordinates
      to the console.

      :param s: An object containing the attributes `x`, `y`, and
                `sitenum` which represent the coordinates and
                identifier of the vertex.
      :type s: object

      :returns: This function does not return a value.
      :rtype: None



   .. py:method:: out_triple(s1, s2, s3)

      Add a triangle defined by three site numbers to the list of triangles.

      This function takes three site objects, extracts their site numbers, and
      appends a tuple of these site numbers to the `triangles` list. If
      debugging is enabled, it prints the site numbers to the console.
      Additionally, if triangulation is enabled and printing is allowed, it
      prints the site numbers in a formatted manner.

      :param s1: The first site object.
      :type s1: Site
      :param s2: The second site object.
      :type s2: Site
      :param s3: The third site object.
      :type s3: Site

      :returns: This function does not return a value.
      :rtype: None



   .. py:method:: out_bisector(edge)

      Process and log the outbisector of a given edge.

      This function appends the parameters of the edge (a, b, c) to the lines
      list and optionally prints debugging information or the parameters based
      on the state of the debug and doPrint flags. The function is designed to
      handle geometric edges and their properties in a computational geometry
      context.

      :param edge: An object representing an edge with attributes
                   a, b, c, edgenum, and reg.
      :type edge: Edge

      :returns: This function does not return a value.
      :rtype: None



   .. py:method:: out_edge(edge)

      Process an edge and update the associated polygons and edges.

      This function takes an edge as input and retrieves the site numbers
      associated with its left and right endpoints. It then updates the
      polygons dictionary to include the edge information for the regions
      associated with the edge. If the regions are not already present in the
      polygons dictionary, they are initialized. The function also appends the
      edge information to the edges list. If triangulation is not enabled, it
      prints the edge number and its associated site numbers.

      :param edge: An instance of the Edge class containing information
      :type edge: Edge

      :returns: This function does not return a value.
      :rtype: None



.. py:function:: voronoi(siteList, context)

   Generate a Voronoi diagram from a list of sites.

   This function computes the Voronoi diagram for a given list of sites. It
   utilizes a sweep line algorithm to process site events and circle
   events, maintaining a priority queue and edge list to manage the
   geometric relationships between the sites. The function outputs the
   resulting edges, vertices, and bisectors to the provided context.

   :param siteList: A list of sites represented by their coordinates.
   :type siteList: SiteList
   :param context: An object that handles the output of the Voronoi diagram
                   elements, including sites, edges, and vertices.
   :type context: Context

   :returns:

             This function does not return a value; it outputs results directly
                 to the context provided.
   :rtype: None


.. py:function:: is_equal(a, b, relativeError=TOLERANCE)

   Check if two values are nearly equal within a specified relative error.

   This function determines if the absolute difference between two values
   is within a specified relative error of the larger of the two values. It
   is useful for comparing floating-point numbers where precision issues
   may arise.

   :param a: The first value to compare.
   :type a: float
   :param b: The second value to compare.
   :type b: float
   :param relativeError: The allowed relative error for the comparison.
   :type relativeError: float

   :returns: True if the values are considered nearly equal, False otherwise.
   :rtype: bool


.. py:class:: Site(x=0.0, y=0.0, sitenum=0)

   Bases: :py:obj:`object`


   .. py:attribute:: x
      :value: 0.0



   .. py:attribute:: y
      :value: 0.0



   .. py:attribute:: sitenum
      :value: 0



   .. py:method:: dump()

      Dump the site information.

      This function prints the site number along with its x and y coordinates
      in a formatted string. It is primarily used for debugging or logging
      purposes to provide a quick overview of the site's attributes.

      :returns: This function does not return any value.
      :rtype: None



   .. py:method:: __lt__(other)

      Compare two objects based on their coordinates.

      This method implements the less-than comparison for objects that have x
      and y attributes. It first compares the y coordinates; if they are
      equal, it then compares the x coordinates. The method returns True if
      the current object is considered less than the other object based on
      these comparisons.

      :param other: The object to compare against, which must have
                    x and y attributes.
      :type other: object

      :returns:

                True if the current object is less than the other object,
                    otherwise False.
      :rtype: bool



   .. py:method:: __eq__(other)

      Determine equality between two objects.

      This method checks if the current object is equal to another object by
      comparing their 'x' and 'y' attributes. If both attributes are equal for
      the two objects, it returns True; otherwise, it returns False.

      :param other: The object to compare with the current object.
      :type other: object

      :returns: True if both objects are equal, False otherwise.
      :rtype: bool



   .. py:method:: distance(other)

      Calculate the distance between two points in a 2D space.

      This function computes the Euclidean distance between the current point
      (represented by the instance's coordinates) and another point provided
      as an argument. It uses the Pythagorean theorem to calculate the
      distance based on the differences in the x and y coordinates of the two
      points.

      :param other: Another point in 2D space to calculate the distance from.
      :type other: Point

      :returns: The Euclidean distance between the two points.
      :rtype: float



.. py:class:: Edge

   Bases: :py:obj:`object`


   .. py:attribute:: LE
      :value: 0



   .. py:attribute:: RE
      :value: 1



   .. py:attribute:: EDGE_NUM
      :value: 0



   .. py:attribute:: DELETED


   .. py:attribute:: a
      :value: 0.0



   .. py:attribute:: b
      :value: 0.0



   .. py:attribute:: c
      :value: 0.0



   .. py:attribute:: ep
      :value: [None, None]



   .. py:attribute:: reg
      :value: [None, None]



   .. py:attribute:: edgenum
      :value: 0



   .. py:method:: dump()

      Dump the current state of the object.

      This function prints the values of the object's attributes, including
      the edge number, and the values of a, b, c, as well as the ep and reg
      attributes. It is useful for debugging purposes to understand the
      current state of the object.

      .. attribute:: edgenum

         The edge number of the object.

         :type: int

      .. attribute:: a

         The value of attribute a.

         :type: float

      .. attribute:: b

         The value of attribute b.

         :type: float

      .. attribute:: c

         The value of attribute c.

         :type: float

      .. attribute:: ep

         The value of the ep attribute.

      .. attribute:: reg

         The value of the reg attribute.



   .. py:method:: set_endpoint(lrFlag, site)

      Set the endpoint for a given flag.

      This function assigns a site to the specified endpoint flag. It checks
      if the corresponding endpoint for the opposite flag is not set to None.
      If it is None, the function returns False; otherwise, it returns True.

      :param lrFlag: The flag indicating which endpoint to set.
      :type lrFlag: int
      :param site: The site to be assigned to the specified endpoint.
      :type site: str

      :returns: True if the opposite endpoint is set, False otherwise.
      :rtype: bool



   .. py:method:: bisect(s1, s2)
      :staticmethod:


      Bisect two sites to create a new edge.

      This function takes two site objects and computes the bisector edge
      between them. It calculates the slope and intercept of the line that
      bisects the two sites, storing the necessary parameters in a new edge
      object. The edge is initialized with no endpoints, as it extends to
      infinity. The function determines whether to fix x or y based on the
      relative distances between the sites.

      :param s1: The first site to be bisected.
      :type s1: Site
      :param s2: The second site to be bisected.
      :type s2: Site

      :returns: A new edge object representing the bisector between the two sites.
      :rtype: Edge



.. py:class:: Halfedge(edge=None, pm=Edge.LE)

   Bases: :py:obj:`object`


   .. py:attribute:: left
      :value: None



   .. py:attribute:: right
      :value: None



   .. py:attribute:: qnext
      :value: None



   .. py:attribute:: edge
      :value: None



   .. py:attribute:: pm
      :value: 0



   .. py:attribute:: vertex
      :value: None



   .. py:attribute:: ystar
      :value: 1e+38



   .. py:method:: dump()

      Dump the internal state of the object.

      This function prints the current values of the object's attributes,
      including left, right, edge, pm, vertex, and ystar. If the vertex
      attribute is present and has a dump method, it will call that method to
      print the vertex's internal state. Otherwise, it will print "None" for
      the vertex.

      .. attribute:: left

         The left halfedge associated with this object.

      .. attribute:: right

         The right halfedge associated with this object.

      .. attribute:: edge

         The edge associated with this object.

      .. attribute:: pm

         The PM associated with this object.

      .. attribute:: vertex

         The vertex associated with this object, which may have its
         own dump method.

      .. attribute:: ystar

         The ystar value associated with this object.



   .. py:method:: __lt__(other)

      Compare two objects based on their ystar and vertex attributes.

      This method implements the less-than comparison for objects. It first
      compares the `ystar` attributes of the two objects. If they are equal,
      it then compares the x-coordinate of their `vertex` attributes to
      determine the order.

      :param other: The object to compare against.
      :type other: YourClass

      :returns:

                True if the current object is less than the other object, False
                    otherwise.
      :rtype: bool



   .. py:method:: __eq__(other)

      Check equality of two objects.

      This method compares the current object with another object to determine
      if they are equal. It checks if the 'ystar' attribute and the 'x'
      coordinate of the 'vertex' attribute are the same for both objects.

      :param other: The object to compare with the current instance.
      :type other: object

      :returns: True if both objects are considered equal, False otherwise.
      :rtype: bool



   .. py:method:: left_reg(default)

      Retrieve the left registration value based on the edge state.

      This function checks the state of the edge attribute. If the edge is not
      set, it returns the provided default value. If the edge is set and its
      property indicates a left edge (Edge.LE), it returns the left
      registration value. Otherwise, it returns the right registration value.

      :param default: The value to return if the edge is not set.

      :returns: The left registration value if applicable, otherwise the default value.



   .. py:method:: right_reg(default)

      Retrieve the appropriate registration value based on the edge state.

      This function checks if the current edge is set. If it is not set, it
      returns the provided default value. If the edge is set and the current
      state is Edge.LE, it returns the registration value associated with
      Edge.RE. Otherwise, it returns the registration value associated with
      Edge.LE.

      :param default: The value to return if there is no edge set.

      :returns:

                The registration value corresponding to the current edge state or the
                    default value if no edge is set.



   .. py:method:: is_point_right_of(pt)

      Determine if a point is to the right of a half-edge.

      This function checks whether the given point `pt` is located to the
      right of the half-edge represented by the current object. It takes into
      account the position of the top site of the edge and various geometric
      properties to make this determination. The function uses the edge's
      parameters to evaluate the relationship between the point and the half-
      edge.

      :param pt: A point object with x and y coordinates.
      :type pt: Point

      :returns: True if the point is to the right of the half-edge, False otherwise.
      :rtype: bool



   .. py:method:: intersect(other)

      Create a new site where two edges intersect.

      This function calculates the intersection point of two edges,
      represented by the current instance and another instance passed as an
      argument. It first checks if either edge is None, and if they belong to
      the same parent region. If the edges are parallel or do not intersect,
      it returns None. If an intersection point is found, it creates and
      returns a new Site object at the intersection coordinates.

      :param other: Another edge to intersect with the current edge.
      :type other: Edge

      :returns: A Site object representing the intersection point
                if an intersection occurs; otherwise, None.
      :rtype: Site or None



.. py:class:: EdgeList(xmin, xmax, nsites)

   Bases: :py:obj:`object`


   .. py:attribute:: hashsize


   .. py:attribute:: xmin


   .. py:attribute:: deltax


   .. py:attribute:: hash


   .. py:attribute:: leftend


   .. py:attribute:: rightend


   .. py:method:: insert(left, he)

      Insert a node into a doubly linked list.

      This function takes a node and inserts it into the list immediately
      after the specified left node. It updates the pointers of the
      surrounding nodes to maintain the integrity of the doubly linked list.

      :param left: The node after which the new node will be inserted.
      :type left: Node
      :param he: The new node to be inserted into the list.
      :type he: Node



   .. py:method:: delete(he)

      Delete a node from a doubly linked list.

      This function updates the pointers of the neighboring nodes to remove
      the specified node from the list. It also marks the node as deleted by
      setting its edge attribute to Edge.DELETED.

      :param he: The node to be deleted from the list.
      :type he: Node



   .. py:method:: get_hash(b)

      Retrieve an entry from the hash table, ignoring deleted nodes.

      This function checks if the provided index is within the valid range of
      the hash table. If the index is valid, it retrieves the corresponding
      entry. If the entry is marked as deleted, it updates the hash table to
      remove the reference to the deleted entry and returns None.

      :param b: The index in the hash table to retrieve the entry from.
      :type b: int

      :returns: The entry at the specified index, or None if the index is out of bounds
                or if the entry is marked as deleted.
      :rtype: object



   .. py:method:: left_bnd(pt)

      Find the left boundary half-edge for a given point.

      This function computes the appropriate half-edge that is to the left of
      the specified point. It utilizes a hash table to quickly locate the
      half-edge that is closest to the desired position based on the
      x-coordinate of the point. If the initial bucket derived from the
      point's x-coordinate does not contain a valid half-edge, the function
      will search adjacent buckets until it finds one. Once a half-edge is
      located, it will traverse through the linked list of half-edges to find
      the correct one that lies to the left of the point.

      :param pt: A point object containing x and y coordinates.
      :type pt: Point

      :returns: The half-edge that is to the left of the given point.
      :rtype: HalfEdge



.. py:class:: PriorityQueue(ymin, ymax, nsites)

   Bases: :py:obj:`object`


   .. py:attribute:: ymin


   .. py:attribute:: deltay


   .. py:attribute:: hashsize


   .. py:attribute:: count
      :value: 0



   .. py:attribute:: minidx
      :value: 0



   .. py:attribute:: hash
      :value: []



   .. py:method:: __len__()

      Return the length of the object.

      This method returns the count of items in the object, which is useful
      for determining how many elements are present. It is typically used to
      support the built-in `len()` function.

      :returns: The number of items in the object.
      :rtype: int



   .. py:method:: is_empty()

      Check if the object is empty.

      This method determines whether the object contains any elements by
      checking the value of the count attribute. If the count is zero, the
      object is considered empty; otherwise, it is not.

      :returns: True if the object is empty, False otherwise.
      :rtype: bool



   .. py:method:: insert(he, site, offset)

      Insert a new element into the data structure.

      This function inserts a new element represented by `he` into the
      appropriate position in the data structure based on its value. It
      updates the `ystar` attribute of the element and links it to the next
      element in the list. The function also manages the count of elements in
      the structure.

      :param he: The element to be inserted, which contains a vertex and
                 a y-coordinate.
      :type he: Element
      :param site: The site object that provides the y-coordinate for the
                   insertion.
      :type site: Site
      :param offset: The offset to be added to the y-coordinate of the site.
      :type offset: float

      :returns: This function does not return a value.
      :rtype: None



   .. py:method:: delete(he)

      Delete a specified element from the data structure.

      This function removes the specified element (he) from the linked list
      associated with the corresponding bucket in the hash table. It traverses
      the linked list until it finds the element to delete, updates the
      pointers to bypass the deleted element, and decrements the count of
      elements in the structure. If the element is found and deleted, its
      vertex is set to None to indicate that it is no longer valid.

      :param he: The element to be deleted from the data structure.
      :type he: Element



   .. py:method:: get_bucket(he)

      Get the appropriate bucket index for a given value.

      This function calculates the bucket index based on the provided value
      and the object's parameters. It ensures that the bucket index is within
      the valid range, adjusting it if necessary. The calculation is based on
      the difference between a specified value and a minimum value, scaled by
      a delta value and the size of the hash table. The function also updates
      the minimum index if the calculated bucket is lower than the current
      minimum index.

      :param he: An object that contains the attribute `ystar`, which is used
                 in the bucket calculation.

      :returns: The calculated bucket index, constrained within the valid range.
      :rtype: int



   .. py:method:: get_min_point()

      Retrieve the minimum point from a hash table.

      This function iterates through the hash table starting from the current
      minimum index and finds the next non-null entry. It then extracts the
      coordinates (x, y) of the vertex associated with that entry and returns
      it as a Site object.

      :returns: An object representing the minimum point with x and y coordinates.
      :rtype: Site



   .. py:method:: pop_min_halfedge()

      Remove and return the minimum half-edge from the data structure.

      This function retrieves the minimum half-edge from a hash table, updates
      the necessary pointers to maintain the integrity of the data structure,
      and decrements the count of half-edges. It effectively removes the
      minimum half-edge while ensuring that the next half-edge in the sequence
      is correctly linked.

      :returns: The minimum half-edge that was removed from the data structure.
      :rtype: HalfEdge



.. py:class:: SiteList(pointList)

   Bases: :py:obj:`object`


   .. py:attribute:: __sites
      :value: []



   .. py:attribute:: __sitenum
      :value: 0



   .. py:attribute:: __xmin


   .. py:attribute:: __ymin


   .. py:attribute:: __xmax


   .. py:attribute:: __ymax


   .. py:attribute:: __extent


   .. py:method:: set_site_number(site)

      Set the site number for a given site.

      This function assigns a unique site number to the provided site object.
      It updates the site object's 'sitenum' attribute with the current value
      of the instance's private '__sitenum' attribute and then increments the
      '__sitenum' for the next site.

      :param site: An object representing a site that has a 'sitenum' attribute.
      :type site: object

      :returns: This function does not return a value.
      :rtype: None



   .. py:class:: Iterator(lst)

      Bases: :py:obj:`object`


      .. py:method:: __iter__()

         Return the iterator object itself.

         This method is part of the iterator protocol. It allows an object to be
         iterable by returning the iterator object itself when the `__iter__`
         method is called. This is typically used in conjunction with the
         `__next__` method to iterate over the elements of the object.

         :returns: The iterator object itself.
         :rtype: self



      .. py:method:: next()

         Retrieve the next item from a generator.

         This function attempts to get the next value from the provided
         generator. It handles both Python 2 and Python 3 syntax for retrieving
         the next item. If the generator is exhausted, it returns None instead of
         raising an exception.

         :param this: An object that contains a generator attribute.
         :type this: object

         :returns: The next item from the generator, or None if the generator is exhausted.
         :rtype: object




   .. py:method:: iterator()

      Create an iterator for the sites.

      This function returns an iterator object that allows iteration over the
      collection of sites stored in the instance. It utilizes the
      SiteList.Iterator class to facilitate the iteration process.

      :returns: An iterator for the sites in the SiteList.
      :rtype: Iterator



   .. py:method:: __iter__()

      Iterate over the sites in the SiteList.

      This method returns an iterator for the SiteList, allowing for traversal
      of the contained sites. It utilizes the internal Iterator class to
      manage the iteration process.

      :returns: An iterator for the sites in the SiteList.
      :rtype: Iterator



   .. py:method:: __len__()

      Return the number of sites.

      This method returns the length of the internal list of sites. It is used
      to determine how many sites are currently stored in the object. The
      length is calculated using the built-in `len()` function on the
      `__sites` attribute.

      :returns: The number of sites in the object.
      :rtype: int



   .. py:method:: _getxmin()

      Retrieve the minimum x-coordinate value.

      This function accesses and returns the private attribute __xmin, which
      holds the minimum x-coordinate value for the object. It is typically
      used in contexts where the minimum x value is needed for calculations or
      comparisons.

      :returns: The minimum x-coordinate value.
      :rtype: float



   .. py:method:: _getymin()

      Retrieve the minimum y-coordinate value.

      This function returns the minimum y-coordinate value stored in the
      instance variable `__ymin`. It is typically used in contexts where the
      minimum y-value is needed for calculations or comparisons.

      :returns: The minimum y-coordinate value.
      :rtype: float



   .. py:method:: _getxmax()

      Retrieve the maximum x value.

      This function returns the maximum x value stored in the instance. It is
      a private method intended for internal use within the class and provides
      access to the __xmax attribute.

      :returns: The maximum x value.
      :rtype: float



   .. py:method:: _getymax()

      Retrieve the maximum y-coordinate value.

      This function accesses and returns the private attribute __ymax, which
      represents the maximum y-coordinate value stored in the instance.

      :returns: The maximum y-coordinate value.
      :rtype: float



   .. py:method:: _getextent()

      Retrieve the extent of the object.

      This function returns the current extent of the object, which is
      typically a representation of its boundaries or limits. The extent is
      stored as a private attribute and can be used for various purposes such
      as rendering, collision detection, or spatial analysis.

      :returns: The extent of the object, which may be in a specific format depending
                on the implementation (e.g., a tuple, list, or custom object).



   .. py:attribute:: xmin


   .. py:attribute:: ymin


   .. py:attribute:: xmax


   .. py:attribute:: ymax


   .. py:attribute:: extent


.. py:function:: compute_voronoi_diagram(points, xBuff=0, yBuff=0, polygonsOutput=False, formatOutput=False, closePoly=True)

   Compute the Voronoi diagram for a set of points.

   This function takes a list of point objects and computes the Voronoi
   diagram, which partitions the plane into regions based on the distance
   to the input points. The function allows for optional buffering of the
   bounding box and can return various formats of the output, including
   edges or polygons of the Voronoi diagram.

   :param points: A list of point objects, each having 'x' and 'y' attributes.
   :type points: list
   :param xBuff: The expansion percentage of the bounding box in the x-direction.
                 Defaults to 0.
   :type xBuff: float?
   :param yBuff: The expansion percentage of the bounding box in the y-direction.
                 Defaults to 0.
   :type yBuff: float?
   :param polygonsOutput: If True, returns polygons instead of edges. Defaults to False.
   :type polygonsOutput: bool?
   :param formatOutput: If True, formats the output to include vertex coordinates. Defaults to
                        False.
   :type formatOutput: bool?
   :param closePoly: If True, closes the polygons by repeating the first point at the end.
                     Defaults to True.
   :type closePoly: bool?

   :returns:     - list: A list of 2-tuples representing the edges of the Voronoi
                 diagram,
                 where each tuple contains the x and y coordinates of the points.
                 If `formatOutput` is True:
                 - tuple: A list of 2-tuples for vertex coordinates and a list of edges
                 indices.
             If `polygonsOutput` is True:
                 - dict: A dictionary where keys are indices of input points and values
                 are n-tuples
                 representing the vertices of each Voronoi polygon.
                 If `formatOutput` is True:
                 - tuple: A list of 2-tuples for vertex coordinates and a dictionary of
                 polygon vertex indices.
   :rtype: If `polygonsOutput` is False


.. py:function:: format_edges_output(edges)

   Format edges output for a list of edges.

   This function takes a list of edges, where each edge is represented as a
   tuple of points. It extracts unique points from the edges and creates a
   mapping of these points to their corresponding indices. The function
   then returns a list of unique points and a list of edges represented by
   their indices.

   :param edges: A list of edges, where each edge is a tuple containing points.
   :type edges: list

   :returns:

             A tuple containing:
                 - list: A list of unique points extracted from the edges.
                 - list: A list of edges represented by their corresponding indices.
   :rtype: tuple


.. py:function:: format_polygons_output(polygons)

   Format the output of polygons into a standardized structure.

   This function takes a dictionary of polygons, where each polygon is
   represented as a list of points. It extracts unique points from all
   polygons and creates an index mapping for these points. The output
   consists of a list of unique points and a dictionary that maps each
   polygon's original indices to their corresponding indices in the unique
   points list.

   :param polygons: A dictionary where keys are polygon identifiers and values
                    are lists of points (tuples) representing the vertices of
                    the polygons.
   :type polygons: dict

   :returns:

             A tuple containing:
                 - list: A list of unique points (tuples) extracted from the input
                 polygons.
                 - dict: A dictionary mapping each polygon's identifier to a list of
                 indices
                 corresponding to the unique points.
   :rtype: tuple


.. py:function:: compute_delaunay_triangulation(points)

   Compute the Delaunay triangulation for a set of points.

   This function takes a list of point objects, each of which must have 'x'
   and 'y' fields. It computes the Delaunay triangulation and returns a
   list of 3-tuples, where each tuple contains the indices of the points
   that form a Delaunay triangle. The triangulation is performed using the
   Voronoi diagram method.

   :param points: A list of point objects with 'x' and 'y' attributes.
   :type points: list

   :returns:

             A list of 3-tuples representing the indices of points that
                 form Delaunay triangles.
   :rtype: list


