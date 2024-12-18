"""Fabex 'loop_utils.py' © 2012 Vilem Novak
"""


def add_loop(parentloop, start, end):
    """Add a loop to a parent loop structure.

    This function recursively checks if the specified start and end values
    can be added as a new loop to the parent loop. If an existing loop
    encompasses the new loop, it will call itself on that loop. If no such
    loop exists, it appends the new loop defined by the start and end values
    to the parent loop's list of loops.

    Args:
        parentloop (list): A list representing the parent loop, where the
            third element is a list of child loops.
        start (int): The starting value of the new loop to be added.
        end (int): The ending value of the new loop to be added.

    Returns:
        None: This function modifies the parentloop in place and does not
            return a value.
    """

    added = False
    for l in parentloop[2]:
        if l[0] < start and l[1] > end:
            add_loop(l, start, end)
            return
    parentloop[2].append([start, end, []])


def cut_loops(csource, parentloop, loops):
    """Cut loops from a source code segment.

    This function takes a source code segment and a parent loop defined by
    its start and end indices, along with a list of nested loops. It creates
    a copy of the source code segment and removes the specified nested loops
    from it. The modified segment is then appended to the provided list of
    loops. The function also recursively processes any nested loops found
    within the parent loop.

    Args:
        csource (str): The source code from which loops will be cut.
        parentloop (tuple): A tuple containing the start index, end index, and a list of nested
            loops.
            The list of nested loops should contain tuples with start and end
            indices for each loop.
        loops (list): A list that will be populated with the modified source code segments
            after
            removing the specified loops.

    Returns:
        None: This function modifies the `loops` list in place and does not return a
            value.
    """

    copy = csource[parentloop[0] : parentloop[1]]

    for li in range(len(parentloop[2]) - 1, -1, -1):
        l = parentloop[2][li]
        # print(l)
        copy = copy[: l[0] - parentloop[0]] + copy[l[1] - parentloop[0] :]
    loops.append(copy)
    for l in parentloop[2]:
        cut_loops(csource, l, loops)
