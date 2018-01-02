"""
helper functions for timeseries
"""


def index_of(val, array, begin=False):
    """
    returns index in presorted array where val would be inserted (to left)

    Parameters
    ----------
    val: numeric, required
        the value to find the index of

    array : list, required
        a sorted list

    >>> index_of(3, [1, 2, 3, 4, 5])
    2
    """
    low, high = 0, len(array) - 1
    if val is None:
        return low if begin else high
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


def pad_lists(interval, *lsts, **kwargs):
    """
    pad lists using the first list passed adding additional values so there is at most 'interval' between each point

    Parameters
    ----------
    interval: numeric, required
        the maximum distance between values to be preserved

    keep_end : bool, optional
        keep the last item of lists, even if its less than `interval` distance from prior item

    >>> pad_lists(1, [0, 2, 4, 6], [0, 2, 4, 6])
    [[0, 1, 2, 3, 4, 5, 6], [0, 2, 2, 4, 4, 6, 6]]
    """
    new_lists = [[] for _ in lsts]
    last_idx = len(lsts[0]) - 1 if kwargs.get('keep_end') else None
    prev_val = None
    for idx, vals in enumerate(zip(*lsts)):
        curr_val = vals[0]
        if idx in [0, last_idx]:
            prev_val = vals[0]
            for i, v in enumerate(vals):
                new_lists[i].append(v)
            continue

        while curr_val - prev_val > interval:
            prev_val += interval
            for i, v in enumerate(vals):
                if not i:
                    new_lists[i].append(prev_val)
                else:
                    new_lists[i].append(v)
        for i, v in enumerate(vals):
            new_lists[i].append(v)

        prev_val = curr_val

    return new_lists


def float_div(num, denom):
    """
    try to divide num by denom, return 0 if denom is 0
    """
    try:
        return 1. * num / denom
    except ZeroDivisionError:
        return 0


def merge_nested_dicts(dict1, dict2):
    """
    merge two nested dictionaries together
    """
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_nested_dicts(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1

def combine_dicts(dict1, dict2, op_values, operators):
    """
    combine two dictionaries
    """
    dict1 = {k: v for k, v in dict1.iteritems()}
    dict2 = {k: v for k, v in dict2.iteritems()}
    new_dict = merge_nested_dicts(dict1, dict2)
    for (op_val, operator) in zip(op_values, operators):
        new_dict[op_val] = operator(dict1.get(op_val, 0), dict2.get(op_val, 0))
    return new_dict
