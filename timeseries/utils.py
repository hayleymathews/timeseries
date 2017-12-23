"""
helper functions for timeseries
"""


def index_of(val, array):
    """
    returns index in presorted array where val would be inserted (to left)

    >>> index_of(3, [1, 2, 3, 4, 5])
    2
    """
    low, high = 0, len(array) - 1
    if val is None:
        return high
    while low <= high:
        mid = (high + low) // 2
        if array[mid] == val:
            return mid
        elif val < array[mid]:
            high = mid - 1
        else:
            low = mid + 1
    return low - 1 if low else low


def prune_lists(interval, *lsts, **kwargs):
    """
    prune lists using the first list passed keeping only items that are at least `interval` distance apart

    Parameters
    ----------
    interval: numeric, required
        the minimum distance between values to be preserved

    keep_end : bool, optional
        keep the last item of lists, even if its less than `interval` distance from prior item

    >>> prune_lists(2, [0, 1, 2, 3, 4], [1, 2, 3, 4, 5])
    [[0, 2, 4], [1, 3, 5]]
    """
    new_lists = [[] for _ in lsts]
    last_idx = len(lsts[0]) - 1 if kwargs.get('keep_end') else None
    prev_val = None
    for idx, vals in enumerate(zip(*lsts)):
        if idx in [0, last_idx]:
            prev_val = vals[0]
            for i, v in enumerate(vals):
                new_lists[i].append(v)
        elif vals[0] - prev_val >= interval:
            prev_val = vals[0]
            for i, v in enumerate(vals):
                new_lists[i].append(v)
    return new_lists
