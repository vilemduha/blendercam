# from shapely.geometry import Point
from shapely.strtree import STRtree


def parent_child_distance(parents, children, o, distance=None):
    # parenting based on x,y distance between chunks
    # hierarchy works like this: - children get milled first.
    if distance is None:
        dlim = o.distance_between_paths * 2

        if o.strategy in ["PARALLEL", "CROSS"] and o.movement.parallel_step_back:
            dlim = dlim * 2
    else:
        dlim = distance

    # For small chunk counts brute force is faster than the STRtree build overhead.
    # Only use the spatial index when the pair count justifies it.
    use_tree = len(parents) * len(children) > 2500  # ~50×50 break-even

    if not use_tree:
        for child in children:
            for parent in parents:
                if parent != child and parent.x_y_distance_within(child, cutoff=dlim):
                    parent.children.append(child)
                    child.parents.append(parent)
        return

    # Build a spatial index over parents to avoid O(n²) pairwise distance checks.
    # Each parent polygon is buffered by dlim so a simple bbox query is sufficient
    # to find all candidates; the exact check is still done by x_y_distance_within.
    indexed_parents = []
    parent_geoms = []
    for parent in parents:
        if parent.poly is None:
            parent.update_poly()
        if parent.poly is not None:
            indexed_parents.append(parent)
            parent_geoms.append(parent.poly.buffer(dlim))

    if not indexed_parents:
        # Fall back to brute force when no polygons are available
        for child in children:
            for parent in parents:
                if parent != child and parent.x_y_distance_within(child, cutoff=dlim):
                    parent.children.append(child)
                    child.parents.append(parent)
        return

    tree = STRtree(parent_geoms)

    for child in children:
        if child.poly is None:
            child.update_poly()
        if child.poly is None:
            # No polygon — fall back to checking all indexed parents for this child
            for parent in indexed_parents:
                if parent != child and parent.x_y_distance_within(child, cutoff=dlim):
                    parent.children.append(child)
                    child.parents.append(parent)
            continue
        for hit_idx in tree.query(child.poly):
            parent = indexed_parents[hit_idx]
            if parent != child and parent.x_y_distance_within(child, cutoff=dlim):
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
                parent_x = parent.poly.bounds[0]
                parent_z = parent.poly.bounds[2]
                child_x = child.poly.bounds[0]
                child_z = child.poly.bounds[2]

                if (
                    parent_x <= child_x
                    and parent_z >= child_z
                    and parent.poly.contains(child.poly.representative_point())
                ):
                    parent.children.append(child)
                    child.parents.append(parent)
