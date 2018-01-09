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


def _add_to_lists(i_val, vals, lists):
    for i, v in enumerate(vals):
        if not i:
            lists[i].append(i_val)
        else:
            lists[i].append(v)


def pad_lists(interval, *lsts, **kwargs):
    """
    pad lists using the first list passed adding/removing values so there is 'interval' distance between each point

    Parameters
    ----------
    interval: numeric, required
        the maximum distance between values to be preserved

    keep_end : bool, optional
        keep the last item of lists, even if its less than `interval` distance from prior item

    >>> pad_lists(1, [0, 2, 4, 6], [0, 2, 4, 6])
    [[0, 1, 2, 3, 4, 5, 6], [0, 0, 2, 2, 4, 4, 6]]
    pad_lists(2, [0, 1, 2, 3, 4], [1, 2, 3, 4, 5])
    [[0, 2, 4], [1, 3, 5]]
    """
    # TODO: this is gross. make it better
    keep_end = kwargs.get('keep_end', False)
    prev_val = None
    new_lists = [[] for _ in lsts]
    val_iter = zip(*lsts)
    for idx, vals in enumerate(val_iter):
        if prev_val is None:
            _add_to_lists(vals[0], vals, new_lists)
            prev_val = vals[0]
        if vals[0] - prev_val > interval:
            while vals[0] - prev_val > interval:
                prev_val += interval
                _add_to_lists(prev_val, val_iter[idx - 1], new_lists)
    if keep_end or vals[0] - prev_val >= interval:
        _add_to_lists(vals[0], vals, new_lists)
    return new_lists


def float_div(num, denom):
    """
    try to divide num by denom, return 0 if denom is 0
    """
    try:
        return 1. * num / denom
    except ZeroDivisionError:
        return 0


def merge_nested_dicts(dict1, dict2, new_dict=None):
    """
    merge two nested dictionaries together
    """
    if new_dict is None:
        new_dict = {}
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_nested_dicts(dict1[key], dict2[key], new_dict)
        else:
            new_dict[key] = dict2[key]
    return new_dict


def combine_dicts(dict1, dict2, op_values, operators):
    """
    combine two dictionaries
    """
    new_dict = merge_nested_dicts(dict1, dict2)
    for (op_val, operator) in zip(op_values, operators):
        new_dict[op_val] = operator(dict1.get(op_val, 0), dict2.get(op_val, 0))
    return new_dict
