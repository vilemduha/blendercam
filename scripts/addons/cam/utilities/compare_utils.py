"""Fabex 'compare_utils.py' © 2012 Vilem Novak
"""

from mathutils import Vector


def compare_z_level(x):
    return x[5]


def overlaps(bb1, bb2):
    """Determine if one bounding box is a child of another.

    This function checks if the first bounding box (bb1) is completely
    contained within the second bounding box (bb2). It does this by
    comparing the coordinates of both bounding boxes to see if all corners
    of bb1 are within the bounds of bb2.

    Args:
        bb1 (tuple): A tuple representing the coordinates of the first bounding box
            in the format (x_min, y_min, x_max, y_max).
        bb2 (tuple): A tuple representing the coordinates of the second bounding box
            in the format (x_min, y_min, x_max, y_max).

    Returns:
        bool: True if bb1 is a child of bb2, otherwise False.
    """
    # true if bb1 is child of bb2
    ch1 = bb1
    ch2 = bb2
    if ch2[1] > ch1[1] > ch1[0] > ch2[0] and ch2[3] > ch1[3] > ch1[2] > ch2[2]:
        return True


# most right vector from a set regarding angle..
def get_vector_right(lastv, verts):
    """Get the index of the vector that is most to the right based on angle.

    This function calculates the angle between a reference vector (formed by
    the last two vectors in `lastv`) and each vector in the `verts` list. It
    identifies the vector that has the smallest angle with respect to the
    reference vector, indicating that it is the most rightward vector in
    relation to the specified direction.

    Args:
        lastv (list): A list containing two vectors, where each vector is
            represented as a tuple or list of coordinates.
        verts (list): A list of vectors represented as tuples or lists of
            coordinates.

    Returns:
        int: The index of the vector in `verts` that is most to the right
            based on the calculated angle.
    """

    defa = 100
    v1 = Vector(lastv[0])
    v2 = Vector(lastv[1])
    va = v2 - v1
    for i, v in enumerate(verts):
        if v != lastv[0]:
            vb = Vector(v) - v2
            a = va.angle_signed(Vector(vb))

            if a < defa:
                defa = a
                returnvec = i
    return returnvec


def unique(L):
    """Return a list of unhashable elements in L, but without duplicates.

    This function processes a list of lists, specifically designed to handle
    unhashable elements. It sorts the input list and removes duplicates by
    comparing the elements based on their coordinates. The function counts
    the number of duplicate vertices and the number of collinear points
    along the Z-axis.

    Args:
        L (list): A list of lists, where each inner list represents a point

    Returns:
        tuple: A tuple containing two integers:
            - The first integer represents the count of duplicate vertices.
            - The second integer represents the count of Z-collinear points.
    """
    # For unhashable objects, you can sort the sequence and then scan from the end of the list,
    # deleting duplicates as you go
    nDupli = 0
    nZcolinear = 0
    # sort() brings the equal elements together; then duplicates are easy to weed out in a single pass.
    L.sort()
    last = L[-1]
    for i in range(len(L) - 2, -1, -1):
        if last[:2] == L[i][:2]:  # XY coordinates compararison
            if last[2] == L[i][2]:  # Z coordinates compararison
                nDupli += 1  # duplicates vertices
            else:  # Z colinear
                nZcolinear += 1
            del L[i]
        else:
            last = L[i]
    return (nDupli, nZcolinear)  # list data type is mutable,
    # input list will automatically update and doesn't need to be returned


def check_equal(lst):
    return lst[1:] == lst[:-1]
