from shapely.geometry import LineString

from .shapely_utils import shapely_to_curve


def find_slope(p1, p2):
    """returns slope of a vector

    Args:
        p1 (tuple): point 1 x,y coordinates
        p2 (tuple): point 2 x,y coordinates
    """
    return (p2[1] - p1[1]) / max(p2[0] - p1[0], 0.00001)


def slope_array(loop):
    """Returns an array of slopes from loop coordinates.

    Args:
        loop (list of tuples): list of coordinates for a curve
    """

    remove_multiple("-")
    coords = list(loop.coords)
    #    pnt_amount = round(length / resolution)
    sarray = []
    dsarray = []
    for i, p in enumerate(coords):
        distance = loop.project(Point(p))
        if i != 0:
            slope = find_slope(p, oldp)
            sarray.append((distance, slope * -0.001))
        oldp = p
    for i, p in enumerate(sarray):
        distance = p[0]
        if i != 0:
            slope = find_slope(p, oldp)
            if abs(slope) > 10:
                log.info(distance)
            dsarray.append((distance, slope * -0.00001))
        oldp = p
    derivative = LineString(sarray)
    dderivative = LineString(dsarray)
    shapely_to_curve("-derivative", derivative, 0.0)
    shapely_to_curve("-doublederivative", dderivative, 0.0)
    return sarray


def d_slope_array(loop, resolution=0.001):
    """Returns a double derivative array or slope of the slope

    Args:
        loop (list of tuples): list of coordinates for a curve
        resolution (float): granular resolution of the array
    """
    length = loop.length
    pnt_amount = round(length / resolution)
    sarray = []
    dsarray = []
    for i in range(pnt_amount):
        distance = i * resolution
        pt = loop.interpolate(distance)
        p = (pt.x, pt.y)
        if i != 0:
            slope = abs(angle(p, oldp))
            sarray.append((distance, slope * -0.01))
        oldp = p
    for i, p in enumerate(sarray):
        distance = p[0]
        if i != 0:
            slope = find_slope(p, oldp)
            if abs(slope) > 10:
                log.info(distance)
            dsarray.append((distance, slope * -0.1))
        oldp = p
    dderivative = LineString(dsarray)
    shapely_to_curve("doublederivative", dderivative, 0.0)
    return sarray
