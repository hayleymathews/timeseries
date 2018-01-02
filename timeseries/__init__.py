"""
TODO: better module organization
"""


def tilted(timeseries, new_end):
    """
    create a new timeseries with values tilted to meet a new end value

    Parameters
    ----------
    timeseries: timeseries, required
        instance of timeseries class

    new_end: numeric, required
        the new end point of the values of timeseries
    """
    new_timeseries = timeseries.copy()
    new_timeseries.tilt(new_end)
    return new_timeseries


def shifted(timeseries, num):
    """
    create a new timeseries with times and values shifted by `num`
    rightshift if positive, leftshift if negative

    Parameters
    ----------
    timeseries: timeseries, required
        instance of timeseries class

    num: numeric, required
        number of steps to shift timeseries over
    """
    new_timeseries = timeseries.copy()
    new_timeseries.shift(num)
    return new_timeseries


def pruned(timeseries, interval):
    """
    create a new timeseries keeping only the times(and their associated values)
    that are at least `interval` distance apart

    Parameters
    ----------
    timeseries: timeseries, required
        instance of timeseries class

    interval: numeric, required
        the minimum distance between times to be preserved
    """
    new_timeseries = timeseries.copy()
    new_timeseries.prune(interval)
    return new_timeseries


def padded(timeseries, interval, keep_end=False):
    """
    create a new timeseries so that there is a time(and value) at every interval
    if interpolate, the values will be interpolated, otherwise the previous value will be repeated

    Parameters
    ----------
    timeseries: timeseries, required
        instance of timeseries class

    interval: numeric, required
        the minimum distance between times to be preserved

    keep_end : bool, optional
        keep the last time and value of the timeseries, even if its less than `interval` distance from prior time
    """
    new_timeseries = timeseries.copy()
    new_timeseries.pad(interval, keep_end)
    return new_timeseries
