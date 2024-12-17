"""Fabex 'dict_utils.py' © 2012 Vilem Novak
"""


def dict_cleanup(ndict):
    """Remove lonely points from a dictionary.

    This function iterates over the keys of the provided dictionary and
    removes any entries that contain one or fewer associated values. It
    continues to check for and remove "lonely" points until no more can be
    found. The process is repeated until all such entries are eliminated
    from the dictionary.

    Args:
        ndict (dict): A dictionary where keys are associated with lists of values.

    Returns:
        None: This function modifies the input dictionary in place and does not return
            a value.
    """

    # now it should delete all junk first, iterate over lonely verts.
    print("Removing Lonely Points")
    # found_solitaires=True
    # while found_solitaires:
    found_solitaires = False
    keys = []
    keys.extend(ndict.keys())
    removed = 0
    for k in keys:
        print(k)
        print(ndict[k])
        if len(ndict[k]) <= 1:
            newcheck = [k]
            while len(newcheck) > 0:
                v = newcheck.pop()
                if len(ndict[v]) <= 1:
                    for v1 in ndict[v]:
                        newcheck.append(v)
                    dict_remove(ndict, v)
            removed += 1
            found_solitaires = True
    print(removed)


def dict_remove(dict, val):
    """Remove a key and its associated values from a dictionary.

    This function takes a dictionary and a key (val) as input. It iterates
    through the list of values associated with the given key and removes the
    key from each of those values' lists. Finally, it removes the key itself
    from the dictionary.

    Args:
        dict (dict): A dictionary where the key is associated with a list of values.
        val: The key to be removed from the dictionary and from the lists of its
            associated values.
    """

    for v in dict[val]:
        dict[v].remove(val)
    dict.pop(val)
