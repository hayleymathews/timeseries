"""
fun with timeseries data


TODO:
to more closer match lists/tuple implementations
tilt/shift/prune/pad should be in place operations
tilted, shifted, pruned, padded can be like sorted and create a new copy
"""
import numpy as np
from utils import index_of, pad_lists, float_div


class TimeSeries(object):
    """
    class to provide basic functionality for working with timeseries data

    Parameters
    ----------
    interpolate: bool, optional
        timeseries will interpolate value if a slice is requested at a time that is not in timeseries
        default False

    use_fv: bool, optional
        timeseries will return first value if a slice is requested before the first time
        default False

    first_val: any basic python type, optional
        timeseries slice will return first_val instead of the first value in timeseries if use_fv is False
        default 0
    """
    def __init__(self, *args, **kwargs):
        # TODO: look into faster sorting here
        if len(args) > 1:
            self._times, self._values = (list(t) for t in zip(*sorted(zip(args[0], args[1]))))
        elif isinstance(args[0], list):
            self._times, self._values = (list(t) for t in zip(*sorted(args[0])))
        elif isinstance(args[0], dict):
            self._times, self._values = (list(t) for t in zip(*sorted(args[0].items())))
        else:
            raise Exception

        self.interpolate = kwargs.get('interpolate', False)
        self.first_val = kwargs.get('first_val', 0)

    @property
    def times(self):
        return self._times

    @property
    def values(self):
        return self._values

    def __repr__(self):
        return 'TimeSeries: {}'.format(zip(self._times, self._values))

    def __len__(self):
        return len(self._times)

    def __iter__(self):
        for time, value in zip(self._times, self._values):
            yield (time, value)

    def __getitem__(self, key):
        times, values = self._new_slice(self._times, self._values, key)
        if not isinstance(times, list):
            return times, values
        return TimeSeries(times, values,
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def __setitem__(self, time, value):
        if time in self._times:
            time_index = index_of(time, self._times)
            self._values[time_index] = value
        else:
            raise Exception('time not in timeseries')

    def __eq__(self, other_timeseries):
        return self.times == other_timeseries.times and self.values == other_timeseries.values

    def __add__(self, other_timeseries):
        return TimeSeries({time: self[time][1] + other_timeseries[time][1]
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def __sub__(self, other_timeseries):
        return TimeSeries({time: self[time][1] - other_timeseries[time][1]
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def __mul__(self, other_timeseries):
        return TimeSeries({time: self[time][1] * other_timeseries[time][1]
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def __div__(self, other_timeseries):
        return TimeSeries({time: float_div(self[time][1], other_timeseries[time][1])
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def __or__(self, other_timeseries):
        # TODO: does this make sense? if conflict, take the other_timeseries values
        tv = dict(zip(self._times, self._values))
        tv.update(dict(zip(other_timeseries.times, other_timeseries.values)))
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times],
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def tilt(self, new_end):
        """
        tilt values of timeseries to meet a new end value

        Parameters
        ----------
        new_end: numeric, required
            the new end point of the values of timeseries
        """
        values = np.array(self._values)
        start = values[0]
        rise, run = 1.0 * (new_end - start), values[-1] - start
        new_slope = rise / run if run else rise / (len(values) - 1)
        self._values = (start + (new_slope * (values - start))).tolist()

    def shift(self, num):
        """
        shift entire timeseries by `num`, rightshift if positive, leftshift if negative

        Parameters
        ----------
        num: numeric, required
            number of steps to shift timeseries over
        """
        if not num:
            self._times, self._values = self._times, self._values
        elif num > 0:
            self._times, self._values = self._times[:-num], self._values[num:]
        else:
            self._times, self._values = self._times[-num:], self._values[:num]

    def prune(self, interval, keep_end=False):
        """
        keep only the times(and their associated values) that are at least `interval` distance apart

        Parameters
        ----------
        interval: numeric, required
            the minimum distance between times to be preserved

        keep_end : bool, optional
            keep the last time and value of the timeseries, even if its less than `interval` distance from prior time
        """
        self._times, self._values = pad_lists(interval, self._times, self._values, keep_end=keep_end)

    def pad(self, interval, keep_end=False):
        """
        pad timeseries so that there is a time(and value) at every interval
        if interpolate, the values will be interpolated, otherwise the previous value will be repeated

        Parameters
        ----------
        interval: numeric, required
            the minimum distance between times to be preserved

        keep_end : bool, optional
            keep the last time and value of the timeseries, even if its less than `interval` distance from prior time
        """
        new_times, new_values = pad_lists(interval, self._times, self._values, keep_end=keep_end)
        if self.interpolate:
            new_values = np.interp(new_times, self._times, self._values).tolist()
        self._times, self._values = new_times, new_values

    def topairs(self):
        """
        convert timeseries into list [(time1, value1), ..., (timeN, valueN)]
        """
        return list(zip(self._times, self._values))

    def tolists(self):
        """
        convert timeseries into lists [[times], [values]]
        """
        return self._times, self._values

    def todict(self):
        """
        convert timeseries into dictionary {time1: value1, ... , timeN: valueN}
        """
        return {self._times[i]: self._values[i] for i in range(len(self._times))}

    def copy(self):
        return TimeSeries(self._times, self._values,
                          interpolate=self.interpolate,
                          first_val=self.first_val)

    def _new_slice(self, times, values, key):
        """
        slicing functionality for timeseries
        """
        try:
            start, stop, step = key.start, key.stop, key.step
            if all(x is None for x in [start, stop, step]):
                # [:] slice, return everything
                return times, values
        except AttributeError:
            start, stop, step = key, False, None

        if start is not None and start < times[0] and self.first_val is not False:
            # add default beginning value to front of list
            times = [start] + times
            values = [self.first_val] + values

        start_idx = index_of(start, times, begin=True)
        if stop is False:
            # slice only wants one value
            if self.interpolate:
                return start, np.interp(start, times, values)
            return start, values[start_idx]

        times, values = times[start_idx:], values[start_idx:]
        slice_times, slice_values = [x for x in times], [x for x in values]
        if start > slice_times[0]:
            # reset first time in slice_times
            slice_times[0] = start

        if step:
            slice_times, slice_values = pad_lists(step, slice_times, slice_values, keep_dist=True)

        stop_idx = index_of(stop, slice_times)
        if not stop or stop > slice_times[stop_idx]:
            # hack to include the last value if stop is past the end of list
            stop_idx += 1

        if self.interpolate:
            return slice_times[:stop_idx], np.interp(slice_times[:stop_idx], times, values).tolist()

        return slice_times[:stop_idx], slice_values[:stop_idx]
