from shapely.geometry import Point


def parent_child_distance(parents, children, o, distance=None):
    # parenting based on x,y distance between chunks
    # hierarchy works like this: - children get milled first.
    if distance is None:
        dlim = o.distance_between_paths * 2

        if o.strategy in ["PARALLEL", "CROSS"] and o.movement.parallel_step_back:
            dlim = dlim * 2
    else:
        dlim = distance

    for child in children:
        for parent in parents:
            isrelation = False

            if parent != child:
                if parent.x_y_distance_within(child, cutoff=dlim):
                    parent.children.append(child)
                    child.parents.append(parent)


def parent_child(parents, children, o):
    # connect all children to all parents. Useful for any type of defining hierarchy.
    # hierarchy works like this: - children get milled first.
    for child in children:
        for parent in parents:
            if parent != child:
                parent.children.append(child)
                child.parents.append(parent)


def parent_child_poly(parents, children, o):
    # hierarchy based on polygons - a polygon inside another is his child.
    # hierarchy works like this: - children get milled first.
    for parent in parents:
        if parent.poly is None:
            parent.update_poly()
        for child in children:
            if child.poly is None:
                child.update_poly()
            if child != parent:
                if parent.poly.contains(Point(child.poly.boundary.coords[0])):
                    parent.children.append(child)
                    child.parents.append(parent)
