"""Fabex 'voronoi.py'

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


For programmatic use two functions are available:

computeVoronoiDiagram(points, xBuff, yBuff, polygonsOutput=False, formatOutput=False) :
Takes :
	- a list of point objects (which must have x and y fields).
	- x and y buffer values which are the expansion percentages of the bounding box rectangle including all input points.
	Returns :
	- With default options :
	  A list of 2-tuples, representing the two points of each Voronoi diagram edge.
	  Each point contains 2-tuples which are the x,y coordinates of point.
	  if formatOutput is True, returns :
			- a list of 2-tuples, which are the x,y coordinates of the Voronoi diagram vertices.
			- and a list of 2-tuples (v1, v2) representing edges of the Voronoi diagram.
			  v1 and v2 are the indices of the vertices at the end of the edge.
	- If polygonsOutput option is True, returns :
	  A dictionary of polygons, keys are the indices of the input points,
	  values contains n-tuples representing the n points of each Voronoi diagram polygon.
	  Each point contains 2-tuples which are the x,y coordinates of point.
	  if formatOutput is True, returns :
			- A list of 2-tuples, which are the x,y coordinates of the Voronoi diagram vertices.
			- and a dictionary of input points indices. Values contains n-tuples representing the n points of each Voronoi diagram polygon.
			  Each tuple contains the vertex indices of the polygon vertices.

computeDelaunayTriangulation(points):
	Takes a list of point objects (which must have x and y fields).
	Returns a list of 3-tuples: the indices of the points that form a Delaunay triangle.
"""

import math

from .constants import (
    TOLERANCE,
    BIG_FLOAT,
    PY3,
)


class Context(object):
    def __init__(self):
        """Init function."""
        self.doPrint = 0
        self.debug = 0
        self.extent = ()  # tuple (xmin, xmax, ymin, ymax)
        self.triangulate = False
        self.vertices = []  # list of vertex 2-tuples: (x,y)
        # equation of line 3-tuple (a b c), for the equation of the line a*x+b*y = c
        self.lines = []
        # edge 3-tuple: (line index, vertex 1 index, vertex 2 index)	if either vertex index is -1, the edge extends to infinity
        self.edges = []
        self.triangles = []  # 3-tuple of vertex indices
        self.polygons = {}  # a dict of site:[edges] pairs

    ########Clip functions########
    def get_clip_edges(self):
        """Get the clipped edges based on the current extent.

        This function iterates through the edges of a geometric shape and
        determines which edges are within the specified extent. It handles both
        finite and infinite lines, clipping them as necessary to fit within the
        defined boundaries. For finite lines, it checks if both endpoints are
        within the extent, and if not, it calculates the intersection points
        using the line equations. For infinite lines, it checks if at least one
        endpoint is within the extent and clips accordingly.

        Returns:
            list: A list of tuples, where each tuple contains two points representing the
                clipped edges.
        """
        xmin, xmax, ymin, ymax = self.extent
        clipEdges = []
        for edge in self.edges:
            equation = self.lines[edge[0]]  # line equation
            if edge[1] != -1 and edge[2] != -1:  # finite line
                x1, y1 = self.vertices[edge[1]][0], self.vertices[edge[1]][1]
                x2, y2 = self.vertices[edge[2]][0], self.vertices[edge[2]][1]
                pt1, pt2 = (x1, y1), (x2, y2)
                inExtentP1, inExtentP2 = self.in_extent(x1, y1), self.in_extent(x2, y2)
                if inExtentP1 and inExtentP2:
                    clipEdges.append((pt1, pt2))
                elif inExtentP1 and not inExtentP2:
                    pt2 = self.clip_line(x1, y1, equation, leftDir=False)
                    clipEdges.append((pt1, pt2))
                elif not inExtentP1 and inExtentP2:
                    pt1 = self.clip_line(x2, y2, equation, leftDir=True)
                    clipEdges.append((pt1, pt2))
            else:  # infinite line
                if edge[1] != -1:
                    x1, y1 = self.vertices[edge[1]][0], self.vertices[edge[1]][1]
                    leftDir = False
                else:
                    x1, y1 = self.vertices[edge[2]][0], self.vertices[edge[2]][1]
                    leftDir = True
                if self.in_extent(x1, y1):
                    pt1 = (x1, y1)
                    pt2 = self.clip_line(x1, y1, equation, leftDir)
                    clipEdges.append((pt1, pt2))
        return clipEdges

    def get_clip_polygons(self, closePoly):
        """Get clipped polygons based on the provided edges.

        This function processes a set of polygons defined by their edges and
        vertices, clipping them according to the specified extent. It checks
        whether each edge is finite or infinite and determines if the endpoints
        of each edge are within the defined extent. If they are not, the
        function calculates the intersection points with the extent boundaries.
        The resulting clipped edges are then used to create polygons, which are
        returned as a dictionary. The user can specify whether to close the
        polygons or leave them open.

        Args:
            closePoly (bool): A flag indicating whether to close the polygons.

        Returns:
            dict: A dictionary where keys are polygon indices and values are lists of
                points defining the clipped polygons.
        """
        xmin, xmax, ymin, ymax = self.extent
        poly = {}
        for inPtsIdx, edges in self.polygons.items():
            clipEdges = []
            for edge in edges:
                equation = self.lines[edge[0]]  # line equation
                if edge[1] != -1 and edge[2] != -1:  # finite line
                    x1, y1 = self.vertices[edge[1]][0], self.vertices[edge[1]][1]
                    x2, y2 = self.vertices[edge[2]][0], self.vertices[edge[2]][1]
                    pt1, pt2 = (x1, y1), (x2, y2)
                    inExtentP1, inExtentP2 = self.in_extent(x1, y1), self.in_extent(x2, y2)
                    if inExtentP1 and inExtentP2:
                        clipEdges.append((pt1, pt2))
                    elif inExtentP1 and not inExtentP2:
                        pt2 = self.clip_line(x1, y1, equation, leftDir=False)
                        clipEdges.append((pt1, pt2))
                    elif not inExtentP1 and inExtentP2:
                        pt1 = self.clip_line(x2, y2, equation, leftDir=True)
                        clipEdges.append((pt1, pt2))
                else:  # infinite line
                    if edge[1] != -1:
                        x1, y1 = self.vertices[edge[1]][0], self.vertices[edge[1]][1]
                        leftDir = False
                    else:
                        x1, y1 = self.vertices[edge[2]][0], self.vertices[edge[2]][1]
                        leftDir = True
                    if self.in_extent(x1, y1):
                        pt1 = (x1, y1)
                        pt2 = self.clip_line(x1, y1, equation, leftDir)
                        clipEdges.append((pt1, pt2))
            # create polygon definition from edges and check if polygon is completely closed
            polyPts, complete = self.order_points(clipEdges)
            if not complete:
                startPt = polyPts[0]
                endPt = polyPts[-1]
                if startPt[0] == endPt[0] or startPt[1] == endPt[1]:
                    # if start & end points are collinear then they are along an extent border
                    polyPts.append(polyPts[0])  # simple close
                else:  # close at extent corner
                    if (startPt[0] == xmin and endPt[1] == ymax) or (
                        endPt[0] == xmin and startPt[1] == ymax
                    ):  # upper left
                        polyPts.append((xmin, ymax))  # corner point
                        polyPts.append(polyPts[0])  # close polygon
                    if (startPt[0] == xmax and endPt[1] == ymax) or (
                        endPt[0] == xmax and startPt[1] == ymax
                    ):  # upper right
                        polyPts.append((xmax, ymax))
                        polyPts.append(polyPts[0])
                    if (startPt[0] == xmax and endPt[1] == ymin) or (
                        endPt[0] == xmax and startPt[1] == ymin
                    ):  # bottom right
                        polyPts.append((xmax, ymin))
                        polyPts.append(polyPts[0])
                    if (startPt[0] == xmin and endPt[1] == ymin) or (
                        endPt[0] == xmin and startPt[1] == ymin
                    ):  # bottom left
                        polyPts.append((xmin, ymin))
                        polyPts.append(polyPts[0])
            if not closePoly:  # unclose polygon
                polyPts = polyPts[:-1]
            poly[inPtsIdx] = polyPts
        return poly

    def clip_line(self, x1, y1, equation, leftDir):
        """Clip a line segment defined by its endpoints against a bounding box.

        This function calculates the intersection points of a line defined by
        the given equation with the bounding box defined by the extent of the
        object. Depending on the direction specified (left or right), it will
        return the appropriate intersection point that lies within the bounds.

        Args:
            x1 (float): The x-coordinate of the first endpoint of the line.
            y1 (float): The y-coordinate of the first endpoint of the line.
            equation (tuple): A tuple containing the coefficients (a, b, c) of
                the line equation in the form ax + by + c = 0.
            leftDir (bool): A boolean indicating the direction to clip the line.
                If True, clip towards the left; otherwise, clip
                towards the right.

        Returns:
            tuple: The coordinates of the clipped point as (x, y).
        """
        xmin, xmax, ymin, ymax = self.extent
        a, b, c = equation
        if b == 0:  # vertical line
            if leftDir:  # left is bottom of vertical line
                return (x1, ymax)
            else:
                return (x1, ymin)
        elif a == 0:  # horizontal line
            if leftDir:
                return (xmin, y1)
            else:
                return (xmax, y1)
        else:
            y2_at_xmin = (c - a * xmin) / b
            y2_at_xmax = (c - a * xmax) / b
            x2_at_ymin = (c - b * ymin) / a
            x2_at_ymax = (c - b * ymax) / a
            intersectPts = []
            if ymin <= y2_at_xmin <= ymax:  # valid intersect point
                intersectPts.append((xmin, y2_at_xmin))
            if ymin <= y2_at_xmax <= ymax:
                intersectPts.append((xmax, y2_at_xmax))
            if xmin <= x2_at_ymin <= xmax:
                intersectPts.append((x2_at_ymin, ymin))
            if xmin <= x2_at_ymax <= xmax:
                intersectPts.append((x2_at_ymax, ymax))
            # delete duplicate (happens if intersect point is at extent corner)
            intersectPts = set(intersectPts)
            # choose target intersect point
            if leftDir:
                pt = min(intersectPts)  # smaller x value
            else:
                pt = max(intersectPts)
            return pt

    def in_extent(self, x, y):
        """Check if a point is within the defined extent.

        This function determines whether the given coordinates (x, y) fall
        within the boundaries defined by the extent of the object. The extent is
        defined by its minimum and maximum x and y values (xmin, xmax, ymin,
        ymax). The function returns True if the point is within these bounds,
        and False otherwise.

        Args:
            x (float): The x-coordinate of the point to check.
            y (float): The y-coordinate of the point to check.

        Returns:
            bool: True if the point (x, y) is within the extent, False otherwise.
        """
        xmin, xmax, ymin, ymax = self.extent
        return x >= xmin and x <= xmax and y >= ymin and y <= ymax

    def order_points(self, edges):
        """Order points to form a polygon.

        This function takes a list of edges, where each edge is represented as a
        pair of points, and orders the points to create a polygon. It identifies
        the starting and ending points of the polygon and ensures that the
        points are connected in the correct order. If all points are duplicates,
        it recognizes that the polygon is complete and handles it accordingly.

        Args:
            edges (list): A list of edges, where each edge is a tuple or list containing two
                points.

        Returns:
            tuple: A tuple containing:
                - list: The ordered list of polygon points.
                - bool: A flag indicating whether the polygon is complete.
        """
        poly = []  # returned polygon points list [pt1, pt2, pt3, pt4 ....]
        pts = []
        # get points list
        for edge in edges:
            pts.extend([pt for pt in edge])
        # try to get start & end point
        try:
            # start and end point aren't duplicate
            startPt, endPt = [pt for pt in pts if pts.count(pt) < 2]
        except:  # all points are duplicate --> polygon is complete --> append some or other edge points
            complete = True
            firstIdx = 0
            poly.append(edges[0][0])
            poly.append(edges[0][1])
        else:  # incomplete --> append the first edge points
            complete = False
            # search first edge
            for i, edge in enumerate(edges):
                if startPt in edge:  # find
                    firstIdx = i
                    break
            poly.append(edges[firstIdx][0])
            poly.append(edges[firstIdx][1])
            if poly[0] != startPt:
                poly.reverse()
        # append next points in list
        del edges[firstIdx]
        while edges:  # all points will be treated when edges list will be empty
            currentPt = poly[-1]  # last item
            for i, edge in enumerate(edges):
                if currentPt == edge[0]:
                    poly.append(edge[1])
                    break
                elif currentPt == edge[1]:
                    poly.append(edge[0])
                    break
            del edges[i]
        return poly, complete

    def set_clip_buffer(self, xpourcent, ypourcent):
        """Set the clipping buffer based on percentage adjustments.

        This function modifies the clipping extent of an object by adjusting its
        boundaries according to the specified percentage values for both the x
        and y axes. It calculates the new minimum and maximum values for the x
        and y coordinates by applying the given percentages to the current
        extent.

        Args:
            xpourcent (float): The percentage adjustment for the x-axis.
            ypourcent (float): The percentage adjustment for the y-axis.

        Returns:
            None: This function does not return a value; it modifies the
            object's extent in place.
        """
        xmin, xmax, ymin, ymax = self.extent
        witdh = xmax - xmin
        height = ymax - ymin
        xmin = xmin - witdh * xpourcent / 100
        xmax = xmax + witdh * xpourcent / 100
        ymin = ymin - height * ypourcent / 100
        ymax = ymax + height * ypourcent / 100
        self.extent = xmin, xmax, ymin, ymax

    # End clip functions########

    def out_site(self, s):
        """Handle output for a site object.

        This function processes the output based on the current settings of the
        instance. If debugging is enabled, it prints the site number and its
        coordinates. If triangulation is enabled, no action is taken. If
        printing is enabled, it prints the coordinates of the site.

        Args:
            s (object): An object representing a site, which should have
                attributes 'sitenum', 'x', and 'y'.

        Returns:
            None: This function does not return a value.
        """
        if self.debug:
            print("site (%d) at %f %f" % (s.sitenum, s.x, s.y))
        elif self.triangulate:
            pass
        elif self.doPrint:
            print("s %f %f" % (s.x, s.y))

    def out_vertex(self, s):
        """Add a vertex to the list of vertices.

        This function appends the coordinates of a given vertex to the internal
        list of vertices. Depending on the state of the debug, triangulate, and
        doPrint flags, it may also print debug information or vertex coordinates
        to the console.

        Args:
            s (object): An object containing the attributes `x`, `y`, and
                `sitenum` which represent the coordinates and
                identifier of the vertex.

        Returns:
            None: This function does not return a value.
        """
        self.vertices.append((s.x, s.y))
        if self.debug:
            print("vertex(%d) at %f %f" % (s.sitenum, s.x, s.y))
        elif self.triangulate:
            pass
        elif self.doPrint:
            print("v %f %f" % (s.x, s.y))

    def out_triple(self, s1, s2, s3):
        """Add a triangle defined by three site numbers to the list of triangles.

        This function takes three site objects, extracts their site numbers, and
        appends a tuple of these site numbers to the `triangles` list. If
        debugging is enabled, it prints the site numbers to the console.
        Additionally, if triangulation is enabled and printing is allowed, it
        prints the site numbers in a formatted manner.

        Args:
            s1 (Site): The first site object.
            s2 (Site): The second site object.
            s3 (Site): The third site object.

        Returns:
            None: This function does not return a value.
        """
        self.triangles.append((s1.sitenum, s2.sitenum, s3.sitenum))
        if self.debug:
            print(
                "circle through left=%d right=%d bottom=%d" % (s1.sitenum, s2.sitenum, s3.sitenum)
            )
        elif self.triangulate and self.doPrint:
            print("%d %d %d" % (s1.sitenum, s2.sitenum, s3.sitenum))

    def out_bisector(self, edge):
        """Process and log the outbisector of a given edge.

        This function appends the parameters of the edge (a, b, c) to the lines
        list and optionally prints debugging information or the parameters based
        on the state of the debug and doPrint flags. The function is designed to
        handle geometric edges and their properties in a computational geometry
        context.

        Args:
            edge (Edge): An object representing an edge with attributes
                a, b, c, edgenum, and reg.

        Returns:
            None: This function does not return a value.
        """
        self.lines.append((edge.a, edge.b, edge.c))
        if self.debug:
            print(
                "line(%d) %gx+%gy=%g, bisecting %d %d"
                % (edge.edgenum, edge.a, edge.b, edge.c, edge.reg[0].sitenum, edge.reg[1].sitenum)
            )
        elif self.doPrint:
            print("l %f %f %f" % (edge.a, edge.b, edge.c))

    def out_edge(self, edge):
        """Process an edge and update the associated polygons and edges.

        This function takes an edge as input and retrieves the site numbers
        associated with its left and right endpoints. It then updates the
        polygons dictionary to include the edge information for the regions
        associated with the edge. If the regions are not already present in the
        polygons dictionary, they are initialized. The function also appends the
        edge information to the edges list. If triangulation is not enabled, it
        prints the edge number and its associated site numbers.

        Args:
            edge (Edge): An instance of the Edge class containing information

        Returns:
            None: This function does not return a value.
        """
        sitenumL = -1
        if edge.ep[Edge.LE] is not None:
            sitenumL = edge.ep[Edge.LE].sitenum
        sitenumR = -1
        if edge.ep[Edge.RE] is not None:
            sitenumR = edge.ep[Edge.RE].sitenum

        # polygons dict add by CF
        if edge.reg[0].sitenum not in self.polygons:
            self.polygons[edge.reg[0].sitenum] = []
        if edge.reg[1].sitenum not in self.polygons:
            self.polygons[edge.reg[1].sitenum] = []
        self.polygons[edge.reg[0].sitenum].append((edge.edgenum, sitenumL, sitenumR))
        self.polygons[edge.reg[1].sitenum].append((edge.edgenum, sitenumL, sitenumR))

        self.edges.append((edge.edgenum, sitenumL, sitenumR))

        if not self.triangulate:
            if self.doPrint:
                print("e %d" % edge.edgenum)
                print(" %d " % sitenumL)
                print("%d" % sitenumR)


def voronoi(siteList, context):
    """Generate a Voronoi diagram from a list of sites.

    This function computes the Voronoi diagram for a given list of sites. It
    utilizes a sweep line algorithm to process site events and circle
    events, maintaining a priority queue and edge list to manage the
    geometric relationships between the sites. The function outputs the
    resulting edges, vertices, and bisectors to the provided context.

    Args:
        siteList (SiteList): A list of sites represented by their coordinates.
        context (Context): An object that handles the output of the Voronoi diagram
            elements, including sites, edges, and vertices.

    Returns:
        None: This function does not return a value; it outputs results directly
            to the context provided.
    """
    context.extent = siteList.extent
    edgeList = EdgeList(siteList.xmin, siteList.xmax, len(siteList))
    priorityQ = PriorityQueue(siteList.ymin, siteList.ymax, len(siteList))
    siteIter = siteList.iterator()

    bottomsite = siteIter.next()
    context.out_site(bottomsite)
    newsite = siteIter.next()
    minpt = Site(-BIG_FLOAT, -BIG_FLOAT)
    while True:
        if not priorityQ.is_empty():
            minpt = priorityQ.get_min_point()

        if newsite and (priorityQ.is_empty() or newsite < minpt):
            # newsite is smallest -  this is a site event
            context.out_site(newsite)

            # get first Halfedge to the LEFT and RIGHT of the new site
            lbnd = edgeList.left_bnd(newsite)
            rbnd = lbnd.right

            # if this halfedge has no edge, bot = bottom site (whatever that is)
            # create a new edge that bisects
            bot = lbnd.right_reg(bottomsite)
            edge = Edge.bisect(bot, newsite)
            context.out_bisector(edge)

            # create a new Halfedge, setting its pm field to 0 and insert
            # this new bisector edge between the left and right vectors in
            # a linked list
            bisector = Halfedge(edge, Edge.LE)
            edgeList.insert(lbnd, bisector)

            # if the new bisector intersects with the left edge, remove
            # the left edge's vertex, and put in the new one
            p = lbnd.intersect(bisector)
            if p is not None:
                priorityQ.delete(lbnd)
                priorityQ.insert(lbnd, p, newsite.distance(p))

            # create a new Halfedge, setting its pm field to 1
            # insert the new Halfedge to the right of the original bisector
            lbnd = bisector
            bisector = Halfedge(edge, Edge.RE)
            edgeList.insert(lbnd, bisector)

            # if this new bisector intersects with the right Halfedge
            p = bisector.intersect(rbnd)
            if p is not None:
                # push the Halfedge into the ordered linked list of vertices
                priorityQ.insert(bisector, p, newsite.distance(p))

            newsite = siteIter.next()

        elif not priorityQ.is_empty():
            # intersection is smallest - this is a vector (circle) event

            # pop the Halfedge with the lowest vector off the ordered list of
            # vectors.  Get the Halfedge to the left and right of the above HE
            # and also the Halfedge to the right of the right HE
            lbnd = priorityQ.pop_min_halfedge()
            llbnd = lbnd.left
            rbnd = lbnd.right
            rrbnd = rbnd.right

            # get the Site to the left of the left HE and to the right of
            # the right HE which it bisects
            bot = lbnd.left_reg(bottomsite)
            top = rbnd.right_reg(bottomsite)

            # output the triple of sites, stating that a circle goes through them
            mid = lbnd.right_reg(bottomsite)
            context.out_triple(bot, top, mid)

            # get the vertex that caused this event and set the vertex number
            # couldn't do this earlier since we didn't know when it would be processed
            v = lbnd.vertex
            siteList.set_site_number(v)
            context.out_vertex(v)

            # set the endpoint of the left and right Halfedge to be this vector
            if lbnd.edge.set_endpoint(lbnd.pm, v):
                context.out_edge(lbnd.edge)

            if rbnd.edge.set_endpoint(rbnd.pm, v):
                context.out_edge(rbnd.edge)

            # delete the lowest HE, remove all vertex events to do with the
            # right HE and delete the right HE
            edgeList.delete(lbnd)
            priorityQ.delete(rbnd)
            edgeList.delete(rbnd)

            # if the site to the left of the event is higher than the Site
            # to the right of it, then swap them and set 'pm' to RIGHT
            pm = Edge.LE
            if bot.y > top.y:
                bot, top = top, bot
                pm = Edge.RE

            # Create an Edge (or line) that is between the two Sites.  This
            # creates the formula of the line, and assigns a line number to it
            edge = Edge.bisect(bot, top)
            context.out_bisector(edge)

            # create a HE from the edge
            bisector = Halfedge(edge, pm)

            # insert the new bisector to the right of the left HE
            # set one endpoint to the new edge to be the vector point 'v'
            # If the site to the left of this bisector is higher than the right
            # Site, then this endpoint is put in position 0; otherwise in pos 1
            edgeList.insert(llbnd, bisector)
            if edge.set_endpoint(Edge.RE - pm, v):
                context.out_edge(edge)

            # if left HE and the new bisector don't intersect, then delete
            # the left HE, and reinsert it
            p = llbnd.intersect(bisector)
            if p is not None:
                priorityQ.delete(llbnd)
                priorityQ.insert(llbnd, p, bot.distance(p))

            # if right HE and the new bisector don't intersect, then reinsert it
            p = bisector.intersect(rrbnd)
            if p is not None:
                priorityQ.insert(bisector, p, bot.distance(p))
        else:
            break

    he = edgeList.leftend.right
    while he is not edgeList.rightend:
        context.out_edge(he.edge)
        he = he.right
    Edge.EDGE_NUM = 0  # CF


def is_equal(a, b, relativeError=TOLERANCE):
    """Check if two values are nearly equal within a specified relative error.

    This function determines if the absolute difference between two values
    is within a specified relative error of the larger of the two values. It
    is useful for comparing floating-point numbers where precision issues
    may arise.

    Args:
        a (float): The first value to compare.
        b (float): The second value to compare.
        relativeError (float): The allowed relative error for the comparison.

    Returns:
        bool: True if the values are considered nearly equal, False otherwise.
    """
    # is nearly equal to within the allowed relative error
    norm = max(abs(a), abs(b))
    return (norm < relativeError) or (abs(a - b) < (relativeError * norm))


class Site(object):
    def __init__(self, x=0.0, y=0.0, sitenum=0):
        """Init function."""
        self.x = x
        self.y = y
        self.sitenum = sitenum

    def dump(self):
        """Dump the site information.

        This function prints the site number along with its x and y coordinates
        in a formatted string. It is primarily used for debugging or logging
        purposes to provide a quick overview of the site's attributes.

        Returns:
            None: This function does not return any value.
        """
        print("Site #%d (%g, %g)" % (self.sitenum, self.x, self.y))

    def __lt__(self, other):
        """Compare two objects based on their coordinates.

        This method implements the less-than comparison for objects that have x
        and y attributes. It first compares the y coordinates; if they are
        equal, it then compares the x coordinates. The method returns True if
        the current object is considered less than the other object based on
        these comparisons.

        Args:
            other (object): The object to compare against, which must have
                x and y attributes.

        Returns:
            bool: True if the current object is less than the other object,
                otherwise False.
        """
        if self.y < other.y:
            return True
        elif self.y > other.y:
            return False
        elif self.x < other.x:
            return True
        elif self.x > other.x:
            return False
        else:
            return False

    def __eq__(self, other):
        """Determine equality between two objects.

        This method checks if the current object is equal to another object by
        comparing their 'x' and 'y' attributes. If both attributes are equal for
        the two objects, it returns True; otherwise, it returns False.

        Args:
            other (object): The object to compare with the current object.

        Returns:
            bool: True if both objects are equal, False otherwise.
        """
        if self.y == other.y and self.x == other.x:
            return True

    def distance(self, other):
        """Calculate the distance between two points in a 2D space.

        This function computes the Euclidean distance between the current point
        (represented by the instance's coordinates) and another point provided
        as an argument. It uses the Pythagorean theorem to calculate the
        distance based on the differences in the x and y coordinates of the two
        points.

        Args:
            other (Point): Another point in 2D space to calculate the distance from.

        Returns:
            float: The Euclidean distance between the two points.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


class Edge(object):
    LE = 0  # left end indice --> edge.ep[Edge.LE]
    RE = 1  # right end indice
    EDGE_NUM = 0
    DELETED = {}  # marker value

    def __init__(self):
        """Init function."""
        self.a = 0.0  # equation of the line a*x+b*y = c
        self.b = 0.0
        self.c = 0.0
        self.ep = [None, None]  # end point (2 tuples of site)
        self.reg = [None, None]
        self.edgenum = 0

    def dump(self):
        """Dump the current state of the object.

        This function prints the values of the object's attributes, including
        the edge number, and the values of a, b, c, as well as the ep and reg
        attributes. It is useful for debugging purposes to understand the
        current state of the object.

        Attributes:
            edgenum (int): The edge number of the object.
            a (float): The value of attribute a.
            b (float): The value of attribute b.
            c (float): The value of attribute c.
            ep: The value of the ep attribute.
            reg: The value of the reg attribute.
        """
        print("(#%d a=%g, b=%g, c=%g)" % (self.edgenum, self.a, self.b, self.c))
        print("ep", self.ep)
        print("reg", self.reg)

    def set_endpoint(self, lrFlag, site):
        """Set the endpoint for a given flag.

        This function assigns a site to the specified endpoint flag. It checks
        if the corresponding endpoint for the opposite flag is not set to None.
        If it is None, the function returns False; otherwise, it returns True.

        Args:
            lrFlag (int): The flag indicating which endpoint to set.
            site (str): The site to be assigned to the specified endpoint.

        Returns:
            bool: True if the opposite endpoint is set, False otherwise.
        """
        self.ep[lrFlag] = site
        if self.ep[Edge.RE - lrFlag] is None:
            return False
        return True

    @staticmethod
    def bisect(s1, s2):
        """Bisect two sites to create a new edge.

        This function takes two site objects and computes the bisector edge
        between them. It calculates the slope and intercept of the line that
        bisects the two sites, storing the necessary parameters in a new edge
        object. The edge is initialized with no endpoints, as it extends to
        infinity. The function determines whether to fix x or y based on the
        relative distances between the sites.

        Args:
            s1 (Site): The first site to be bisected.
            s2 (Site): The second site to be bisected.

        Returns:
            Edge: A new edge object representing the bisector between the two sites.
        """
        newedge = Edge()
        newedge.reg[0] = s1  # store the sites that this edge is bisecting
        newedge.reg[1] = s2

        # to begin with, there are no endpoints on the bisector - it goes to infinity
        # ep[0] and ep[1] are None

        # get the difference in x dist between the sites
        dx = float(s2.x - s1.x)
        dy = float(s2.y - s1.y)
        adx = abs(dx)  # make sure that the difference in positive
        ady = abs(dy)

        # get the slope of the line
        newedge.c = float(s1.x * dx + s1.y * dy + (dx * dx + dy * dy) * 0.5)
        if adx > ady:
            # set formula of line, with x fixed to 1
            newedge.a = 1.0
            newedge.b = dy / dx
            newedge.c /= dx
        else:
            # set formula of line, with y fixed to 1
            newedge.b = 1.0
            newedge.a = dx / dy
            newedge.c /= dy

        newedge.edgenum = Edge.EDGE_NUM
        Edge.EDGE_NUM += 1
        return newedge


class Halfedge(object):
    def __init__(self, edge=None, pm=Edge.LE):
        """Init function."""
        self.left = None  # left Halfedge in the edge list
        self.right = None  # right Halfedge in the edge list
        self.qnext = None  # priority queue linked list pointer
        self.edge = edge  # edge list Edge
        self.pm = pm
        self.vertex = None  # Site()
        self.ystar = BIG_FLOAT

    def dump(self):
        """Dump the internal state of the object.

        This function prints the current values of the object's attributes,
        including left, right, edge, pm, vertex, and ystar. If the vertex
        attribute is present and has a dump method, it will call that method to
        print the vertex's internal state. Otherwise, it will print "None" for
        the vertex.

        Attributes:
            left: The left halfedge associated with this object.
            right: The right halfedge associated with this object.
            edge: The edge associated with this object.
            pm: The PM associated with this object.
            vertex: The vertex associated with this object, which may have its
                own dump method.
            ystar: The ystar value associated with this object.
        """
        print("Halfedge--------------------------")
        print("Left: ", self.left)
        print("Right: ", self.right)
        print("Edge: ", self.edge)
        print("PM: ", self.pm)
        print("Vertex: "),
        if self.vertex:
            self.vertex.dump()
        else:
            print("None")
        print("Ystar: ", self.ystar)

    def __lt__(self, other):
        """Compare two objects based on their ystar and vertex attributes.

        This method implements the less-than comparison for objects. It first
        compares the `ystar` attributes of the two objects. If they are equal,
        it then compares the x-coordinate of their `vertex` attributes to
        determine the order.

        Args:
            other (YourClass): The object to compare against.

        Returns:
            bool: True if the current object is less than the other object, False
                otherwise.
        """
        if self.ystar < other.ystar:
            return True
        elif self.ystar > other.ystar:
            return False
        elif self.vertex.x < other.vertex.x:
            return True
        elif self.vertex.x > other.vertex.x:
            return False
        else:
            return False

    def __eq__(self, other):
        """Check equality of two objects.

        This method compares the current object with another object to determine
        if they are equal. It checks if the 'ystar' attribute and the 'x'
        coordinate of the 'vertex' attribute are the same for both objects.

        Args:
            other (object): The object to compare with the current instance.

        Returns:
            bool: True if both objects are considered equal, False otherwise.
        """
        if self.ystar == other.ystar and self.vertex.x == other.vertex.x:
            return True

    def left_reg(self, default):
        """Retrieve the left registration value based on the edge state.

        This function checks the state of the edge attribute. If the edge is not
        set, it returns the provided default value. If the edge is set and its
        property indicates a left edge (Edge.LE), it returns the left
        registration value. Otherwise, it returns the right registration value.

        Args:
            default: The value to return if the edge is not set.

        Returns:
            The left registration value if applicable, otherwise the default value.
        """
        if not self.edge:
            return default
        elif self.pm == Edge.LE:
            return self.edge.reg[Edge.LE]
        else:
            return self.edge.reg[Edge.RE]

    def right_reg(self, default):
        """Retrieve the appropriate registration value based on the edge state.

        This function checks if the current edge is set. If it is not set, it
        returns the provided default value. If the edge is set and the current
        state is Edge.LE, it returns the registration value associated with
        Edge.RE. Otherwise, it returns the registration value associated with
        Edge.LE.

        Args:
            default: The value to return if there is no edge set.

        Returns:
            The registration value corresponding to the current edge state or the
                default value if no edge is set.
        """
        if not self.edge:
            return default
        elif self.pm == Edge.LE:
            return self.edge.reg[Edge.RE]
        else:
            return self.edge.reg[Edge.LE]

    # returns True if p is to right of halfedge self
    def is_point_right_of(self, pt):
        """Determine if a point is to the right of a half-edge.

        This function checks whether the given point `pt` is located to the
        right of the half-edge represented by the current object. It takes into
        account the position of the top site of the edge and various geometric
        properties to make this determination. The function uses the edge's
        parameters to evaluate the relationship between the point and the half-
        edge.

        Args:
            pt (Point): A point object with x and y coordinates.

        Returns:
            bool: True if the point is to the right of the half-edge, False otherwise.
        """
        e = self.edge
        topsite = e.reg[1]
        right_of_site = pt.x > topsite.x

        if right_of_site and self.pm == Edge.LE:
            return True

        if not right_of_site and self.pm == Edge.RE:
            return False

        if e.a == 1.0:
            dyp = pt.y - topsite.y
            dxp = pt.x - topsite.x
            fast = 0
            if (not right_of_site and e.b < 0.0) or (right_of_site and e.b >= 0.0):
                above = dyp >= e.b * dxp
                fast = above
            else:
                above = pt.x + pt.y * e.b > e.c
                if e.b < 0.0:
                    above = not above
                if not above:
                    fast = 1
            if not fast:
                dxs = topsite.x - (e.reg[0]).x
                above = e.b * (dxp * dxp - dyp * dyp) < dxs * dyp * (
                    1.0 + 2.0 * dxp / dxs + e.b * e.b
                )
                if e.b < 0.0:
                    above = not above
        else:  # e.b == 1.0
            yl = e.c - e.a * pt.x
            t1 = pt.y - yl
            t2 = pt.x - topsite.x
            t3 = yl - topsite.y
            above = t1 * t1 > t2 * t2 + t3 * t3

        if self.pm == Edge.LE:
            return above
        else:
            return not above

    # create a new site where the Halfedges el1 and el2 intersect
    def intersect(self, other):
        """Create a new site where two edges intersect.

        This function calculates the intersection point of two edges,
        represented by the current instance and another instance passed as an
        argument. It first checks if either edge is None, and if they belong to
        the same parent region. If the edges are parallel or do not intersect,
        it returns None. If an intersection point is found, it creates and
        returns a new Site object at the intersection coordinates.

        Args:
            other (Edge): Another edge to intersect with the current edge.

        Returns:
            Site or None: A Site object representing the intersection point
            if an intersection occurs; otherwise, None.
        """
        e1 = self.edge
        e2 = other.edge
        if (e1 is None) or (e2 is None):
            return None

        # if the two edges bisect the same parent return None
        if e1.reg[1] is e2.reg[1]:
            return None

        d = e1.a * e2.b - e1.b * e2.a
        if is_equal(d, 0.0):
            return None

        xint = (e1.c * e2.b - e2.c * e1.b) / d
        yint = (e2.c * e1.a - e1.c * e2.a) / d
        if e1.reg[1] < e2.reg[1]:
            he = self
            e = e1
        else:
            he = other
            e = e2

        rightOfSite = xint >= e.reg[1].x
        if (rightOfSite and he.pm == Edge.LE) or (not rightOfSite and he.pm == Edge.RE):
            return None

        # create a new site at the point of intersection - this is a new
        # vector event waiting to happen
        return Site(xint, yint)


class EdgeList(object):
    def __init__(self, xmin, xmax, nsites):
        """Init function."""
        if xmin > xmax:
            xmin, xmax = xmax, xmin
        self.hashsize = int(2 * math.sqrt(nsites + 4))

        self.xmin = xmin
        self.deltax = float(xmax - xmin)
        self.hash = [None] * self.hashsize

        self.leftend = Halfedge()
        self.rightend = Halfedge()
        self.leftend.right = self.rightend
        self.rightend.left = self.leftend
        self.hash[0] = self.leftend
        self.hash[-1] = self.rightend

    def insert(self, left, he):
        """Insert a node into a doubly linked list.

        This function takes a node and inserts it into the list immediately
        after the specified left node. It updates the pointers of the
        surrounding nodes to maintain the integrity of the doubly linked list.

        Args:
            left (Node): The node after which the new node will be inserted.
            he (Node): The new node to be inserted into the list.
        """
        he.left = left
        he.right = left.right
        left.right.left = he
        left.right = he

    def delete(self, he):
        """Delete a node from a doubly linked list.

        This function updates the pointers of the neighboring nodes to remove
        the specified node from the list. It also marks the node as deleted by
        setting its edge attribute to Edge.DELETED.

        Args:
            he (Node): The node to be deleted from the list.
        """
        he.left.right = he.right
        he.right.left = he.left
        he.edge = Edge.DELETED

    # Get entry from hash table, pruning any deleted nodes
    def get_hash(self, b):
        """Retrieve an entry from the hash table, ignoring deleted nodes.

        This function checks if the provided index is within the valid range of
        the hash table. If the index is valid, it retrieves the corresponding
        entry. If the entry is marked as deleted, it updates the hash table to
        remove the reference to the deleted entry and returns None.

        Args:
            b (int): The index in the hash table to retrieve the entry from.

        Returns:
            object: The entry at the specified index, or None if the index is out of bounds
            or if the entry is marked as deleted.
        """
        if b < 0 or b >= self.hashsize:
            return None
        he = self.hash[b]
        if he is None or he.edge is not Edge.DELETED:
            return he

        #  Hash table points to deleted half edge.  Patch as necessary.
        self.hash[b] = None
        return None

    def left_bnd(self, pt):
        """Find the left boundary half-edge for a given point.

        This function computes the appropriate half-edge that is to the left of
        the specified point. It utilizes a hash table to quickly locate the
        half-edge that is closest to the desired position based on the
        x-coordinate of the point. If the initial bucket derived from the
        point's x-coordinate does not contain a valid half-edge, the function
        will search adjacent buckets until it finds one. Once a half-edge is
        located, it will traverse through the linked list of half-edges to find
        the correct one that lies to the left of the point.

        Args:
            pt (Point): A point object containing x and y coordinates.

        Returns:
            HalfEdge: The half-edge that is to the left of the given point.
        """
        # Use hash table to get close to desired halfedge
        bucket = int(((pt.x - self.xmin) / self.deltax * self.hashsize))

        if bucket < 0:
            bucket = 0

        if bucket >= self.hashsize:
            bucket = self.hashsize - 1

        he = self.get_hash(bucket)
        if he is None:
            i = 1
            while True:
                he = self.get_hash(bucket - i)
                if he is not None:
                    break
                he = self.get_hash(bucket + i)
                if he is not None:
                    break
                i += 1

        # Now search linear list of halfedges for the corect one
        if (he is self.leftend) or (he is not self.rightend and he.is_point_right_of(pt)):
            he = he.right
            while he is not self.rightend and he.is_point_right_of(pt):
                he = he.right
            he = he.left
        else:
            he = he.left
            while he is not self.leftend and not he.is_point_right_of(pt):
                he = he.left

        # Update hash table and reference counts
        if bucket > 0 and bucket < self.hashsize - 1:
            self.hash[bucket] = he
        return he


class PriorityQueue(object):
    def __init__(self, ymin, ymax, nsites):
        """Init function."""
        self.ymin = ymin
        self.deltay = ymax - ymin
        self.hashsize = int(4 * math.sqrt(nsites))
        self.count = 0
        self.minidx = 0
        self.hash = []
        for i in range(self.hashsize):
            self.hash.append(Halfedge())

    def __len__(self):
        """Return the length of the object.

        This method returns the count of items in the object, which is useful
        for determining how many elements are present. It is typically used to
        support the built-in `len()` function.

        Returns:
            int: The number of items in the object.
        """
        return self.count

    def is_empty(self):
        """Check if the object is empty.

        This method determines whether the object contains any elements by
        checking the value of the count attribute. If the count is zero, the
        object is considered empty; otherwise, it is not.

        Returns:
            bool: True if the object is empty, False otherwise.
        """
        return self.count == 0

    def insert(self, he, site, offset):
        """Insert a new element into the data structure.

        This function inserts a new element represented by `he` into the
        appropriate position in the data structure based on its value. It
        updates the `ystar` attribute of the element and links it to the next
        element in the list. The function also manages the count of elements in
        the structure.

        Args:
            he (Element): The element to be inserted, which contains a vertex and
                a y-coordinate.
            site (Site): The site object that provides the y-coordinate for the
                insertion.
            offset (float): The offset to be added to the y-coordinate of the site.

        Returns:
            None: This function does not return a value.
        """
        he.vertex = site
        he.ystar = site.y + offset
        last = self.hash[self.get_bucket(he)]
        next = last.qnext
        while (next is not None) and he > next:
            last = next
            next = last.qnext
        he.qnext = last.qnext
        last.qnext = he
        self.count += 1

    def delete(self, he):
        """Delete a specified element from the data structure.

        This function removes the specified element (he) from the linked list
        associated with the corresponding bucket in the hash table. It traverses
        the linked list until it finds the element to delete, updates the
        pointers to bypass the deleted element, and decrements the count of
        elements in the structure. If the element is found and deleted, its
        vertex is set to None to indicate that it is no longer valid.

        Args:
            he (Element): The element to be deleted from the data structure.
        """
        if he.vertex is not None:
            last = self.hash[self.get_bucket(he)]
            while last.qnext is not he:
                last = last.qnext
            last.qnext = he.qnext
            self.count -= 1
            he.vertex = None

    def get_bucket(self, he):
        """Get the appropriate bucket index for a given value.

        This function calculates the bucket index based on the provided value
        and the object's parameters. It ensures that the bucket index is within
        the valid range, adjusting it if necessary. The calculation is based on
        the difference between a specified value and a minimum value, scaled by
        a delta value and the size of the hash table. The function also updates
        the minimum index if the calculated bucket is lower than the current
        minimum index.

        Args:
            he: An object that contains the attribute `ystar`, which is used
                in the bucket calculation.

        Returns:
            int: The calculated bucket index, constrained within the valid range.
        """
        bucket = int(((he.ystar - self.ymin) / self.deltay) * self.hashsize)
        if bucket < 0:
            bucket = 0
        if bucket >= self.hashsize:
            bucket = self.hashsize - 1
        if bucket < self.minidx:
            self.minidx = bucket
        return bucket

    def get_min_point(self):
        """Retrieve the minimum point from a hash table.

        This function iterates through the hash table starting from the current
        minimum index and finds the next non-null entry. It then extracts the
        coordinates (x, y) of the vertex associated with that entry and returns
        it as a Site object.

        Returns:
            Site: An object representing the minimum point with x and y coordinates.
        """
        while self.hash[self.minidx].qnext is None:
            self.minidx += 1
        he = self.hash[self.minidx].qnext
        x = he.vertex.x
        y = he.ystar
        return Site(x, y)

    def pop_min_halfedge(self):
        """Remove and return the minimum half-edge from the data structure.

        This function retrieves the minimum half-edge from a hash table, updates
        the necessary pointers to maintain the integrity of the data structure,
        and decrements the count of half-edges. It effectively removes the
        minimum half-edge while ensuring that the next half-edge in the sequence
        is correctly linked.

        Returns:
            HalfEdge: The minimum half-edge that was removed from the data structure.
        """
        curr = self.hash[self.minidx].qnext
        self.hash[self.minidx].qnext = curr.qnext
        self.count -= 1
        return curr


class SiteList(object):
    def __init__(self, pointList):
        """Init function."""
        self.__sites = []
        self.__sitenum = 0

        self.__xmin = min([pt.x for pt in pointList])
        self.__ymin = min([pt.y for pt in pointList])
        self.__xmax = max([pt.x for pt in pointList])
        self.__ymax = max([pt.y for pt in pointList])
        self.__extent = (self.__xmin, self.__xmax, self.__ymin, self.__ymax)

        for i, pt in enumerate(pointList):
            self.__sites.append(Site(pt.x, pt.y, i))
        self.__sites.sort()

    def set_site_number(self, site):
        """Set the site number for a given site.

        This function assigns a unique site number to the provided site object.
        It updates the site object's 'sitenum' attribute with the current value
        of the instance's private '__sitenum' attribute and then increments the
        '__sitenum' for the next site.

        Args:
            site (object): An object representing a site that has a 'sitenum' attribute.

        Returns:
            None: This function does not return a value.
        """
        site.sitenum = self.__sitenum
        self.__sitenum += 1

    class Iterator(object):
        def __init__(this, lst):
            """Init function."""
            this.generator = (s for s in lst)

        def __iter__(this):
            """Return the iterator object itself.

            This method is part of the iterator protocol. It allows an object to be
            iterable by returning the iterator object itself when the `__iter__`
            method is called. This is typically used in conjunction with the
            `__next__` method to iterate over the elements of the object.

            Returns:
                self: The iterator object itself.
            """
            return this

        def next(this):
            """Retrieve the next item from a generator.

            This function attempts to get the next value from the provided
            generator. It handles both Python 2 and Python 3 syntax for retrieving
            the next item. If the generator is exhausted, it returns None instead of
            raising an exception.

            Args:
                this (object): An object that contains a generator attribute.

            Returns:
                object: The next item from the generator, or None if the generator is exhausted.
            """
            try:
                if PY3:
                    return this.generator.__next__()
                else:
                    return this.generator.next()
            except StopIteration:
                return None

    def iterator(self):
        """Create an iterator for the sites.

        This function returns an iterator object that allows iteration over the
        collection of sites stored in the instance. It utilizes the
        SiteList.Iterator class to facilitate the iteration process.

        Returns:
            Iterator: An iterator for the sites in the SiteList.
        """
        return SiteList.Iterator(self.__sites)

    def __iter__(self):
        """Iterate over the sites in the SiteList.

        This method returns an iterator for the SiteList, allowing for traversal
        of the contained sites. It utilizes the internal Iterator class to
        manage the iteration process.

        Returns:
            Iterator: An iterator for the sites in the SiteList.
        """
        return SiteList.Iterator(self.__sites)

    def __len__(self):
        """Return the number of sites.

        This method returns the length of the internal list of sites. It is used
        to determine how many sites are currently stored in the object. The
        length is calculated using the built-in `len()` function on the
        `__sites` attribute.

        Returns:
            int: The number of sites in the object.
        """
        return len(self.__sites)

    def _getxmin(self):
        """Retrieve the minimum x-coordinate value.

        This function accesses and returns the private attribute __xmin, which
        holds the minimum x-coordinate value for the object. It is typically
        used in contexts where the minimum x value is needed for calculations or
        comparisons.

        Returns:
            float: The minimum x-coordinate value.
        """
        return self.__xmin

    def _getymin(self):
        """Retrieve the minimum y-coordinate value.

        This function returns the minimum y-coordinate value stored in the
        instance variable `__ymin`. It is typically used in contexts where the
        minimum y-value is needed for calculations or comparisons.

        Returns:
            float: The minimum y-coordinate value.
        """
        return self.__ymin

    def _getxmax(self):
        """Retrieve the maximum x value.

        This function returns the maximum x value stored in the instance. It is
        a private method intended for internal use within the class and provides
        access to the __xmax attribute.

        Returns:
            float: The maximum x value.
        """
        return self.__xmax

    def _getymax(self):
        """Retrieve the maximum y-coordinate value.

        This function accesses and returns the private attribute __ymax, which
        represents the maximum y-coordinate value stored in the instance.

        Returns:
            float: The maximum y-coordinate value.
        """
        return self.__ymax

    def _getextent(self):
        """Retrieve the extent of the object.

        This function returns the current extent of the object, which is
        typically a representation of its boundaries or limits. The extent is
        stored as a private attribute and can be used for various purposes such
        as rendering, collision detection, or spatial analysis.

        Returns:
            The extent of the object, which may be in a specific format depending
            on the implementation (e.g., a tuple, list, or custom object).
        """
        return self.__extent

    xmin = property(_getxmin)
    ymin = property(_getymin)
    xmax = property(_getxmax)
    ymax = property(_getymax)
    extent = property(_getextent)


def compute_voronoi_diagram(
    points, xBuff=0, yBuff=0, polygonsOutput=False, formatOutput=False, closePoly=True
):
    """Compute the Voronoi diagram for a set of points.

    This function takes a list of point objects and computes the Voronoi
    diagram, which partitions the plane into regions based on the distance
    to the input points. The function allows for optional buffering of the
    bounding box and can return various formats of the output, including
    edges or polygons of the Voronoi diagram.

    Args:
        points (list): A list of point objects, each having 'x' and 'y' attributes.
        xBuff (float?): The expansion percentage of the bounding box in the x-direction.
            Defaults to 0.
        yBuff (float?): The expansion percentage of the bounding box in the y-direction.
            Defaults to 0.
        polygonsOutput (bool?): If True, returns polygons instead of edges. Defaults to False.
        formatOutput (bool?): If True, formats the output to include vertex coordinates. Defaults to
            False.
        closePoly (bool?): If True, closes the polygons by repeating the first point at the end.
            Defaults to True.

    Returns:
        If `polygonsOutput` is False:
            - list: A list of 2-tuples representing the edges of the Voronoi
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
    """
    siteList = SiteList(points)
    context = Context()
    voronoi(siteList, context)
    context.set_clip_buffer(xBuff, yBuff)
    if not polygonsOutput:
        clipEdges = context.get_clip_edges()
        if formatOutput:
            vertices, edgesIdx = format_edges_output(clipEdges)
            return vertices, edgesIdx
        else:
            return clipEdges
    else:
        clipPolygons = context.get_clip_polygons(closePoly)
        if formatOutput:
            vertices, polyIdx = format_polygons_output(clipPolygons)
            return vertices, polyIdx
        else:
            return clipPolygons


def format_edges_output(edges):
    """Format edges output for a list of edges.

    This function takes a list of edges, where each edge is represented as a
    tuple of points. It extracts unique points from the edges and creates a
    mapping of these points to their corresponding indices. The function
    then returns a list of unique points and a list of edges represented by
    their indices.

    Args:
        edges (list): A list of edges, where each edge is a tuple containing points.

    Returns:
        tuple: A tuple containing:
            - list: A list of unique points extracted from the edges.
            - list: A list of edges represented by their corresponding indices.
    """
    # get list of points
    pts = []
    for edge in edges:
        pts.extend(edge)
    # get unique values
    pts = set(pts)  # unique values (tuples are hashable)
    # get dict {values:index}
    valuesIdxDict = dict(zip(pts, range(len(pts))))
    # get edges index reference
    edgesIdx = []
    for edge in edges:
        edgesIdx.append([valuesIdxDict[pt] for pt in edge])
    return list(pts), edgesIdx


def format_polygons_output(polygons):
    """Format the output of polygons into a standardized structure.

    This function takes a dictionary of polygons, where each polygon is
    represented as a list of points. It extracts unique points from all
    polygons and creates an index mapping for these points. The output
    consists of a list of unique points and a dictionary that maps each
    polygon's original indices to their corresponding indices in the unique
    points list.

    Args:
        polygons (dict): A dictionary where keys are polygon identifiers and values
            are lists of points (tuples) representing the vertices of
            the polygons.

    Returns:
        tuple: A tuple containing:
            - list: A list of unique points (tuples) extracted from the input
            polygons.
            - dict: A dictionary mapping each polygon's identifier to a list of
            indices
            corresponding to the unique points.
    """
    # get list of points
    pts = []
    for poly in polygons.values():
        pts.extend(poly)
    # get unique values
    pts = set(pts)  # unique values (tuples are hashable)
    # get dict {values:index}
    valuesIdxDict = dict(zip(pts, range(len(pts))))
    # get polygons index reference
    polygonsIdx = {}
    for inPtsIdx, poly in polygons.items():
        polygonsIdx[inPtsIdx] = [valuesIdxDict[pt] for pt in poly]
    return list(pts), polygonsIdx


# ------------------------------------------------------------------
def compute_delaunay_triangulation(points):
    """Compute the Delaunay triangulation for a set of points.

    This function takes a list of point objects, each of which must have 'x'
    and 'y' fields. It computes the Delaunay triangulation and returns a
    list of 3-tuples, where each tuple contains the indices of the points
    that form a Delaunay triangle. The triangulation is performed using the
    Voronoi diagram method.

    Args:
        points (list): A list of point objects with 'x' and 'y' attributes.

    Returns:
        list: A list of 3-tuples representing the indices of points that
            form Delaunay triangles.
    """
    siteList = SiteList(points)
    context = Context()
    context.triangulate = True
    voronoi(siteList, context)
    return context.triangles
