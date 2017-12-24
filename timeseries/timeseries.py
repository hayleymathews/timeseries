"""
fun with timeseries data
"""
import numpy as np
from utils import index_of, prune_lists, pad_lists, float_div


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
        self.use_fv = kwargs.get('use_fv', False)
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
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __setitem__(self, time, value):
        time_index = index_of(time, self._times)
        self._values[time_index] = value

    def __add__(self, other_timeseries):
        return TimeSeries({time: self[time][1] + other_timeseries[time][1]
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __sub__(self, other_timeseries):
        return TimeSeries({time: self[time][1] - other_timeseries[time][1]
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __mul__(self, other_timeseries):
        return TimeSeries({time: self[time][1] * other_timeseries[time][1]
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __div__(self, other_timeseries):
        return TimeSeries({time: float_div(self[time][1], other_timeseries[time][1])
                           for time in sorted(self._times + other_timeseries.times)},
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __and__(self, other_timeseries):
        # TODO: does this make sense? if conflict, take the other_timeseries values
        tv = dict(zip(self._times, self._values))
        tv.update(dict(zip(other_timeseries.times, other_timeseries.values)))
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times],
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
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
        rise = 1.0 * (new_end - start)
        run = values[-1] - start
        if run:
            new_slope = rise / run
            self._values = (start + (new_slope * (values - start))).tolist()
        new_slope = rise / (len(values) - 1)
        return TimeSeries(self._times, [start + new_slope * i for i in range(len(values))],
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def shift(self, num):
        """
        shift entire timeseries by `num`, rightshift if positive, leftshift if negative

        Parameters
        ----------
        num: numeric, required
            number of steps to shift timeseries over
        """
        if not num:
            times, values = self._times, self._values
        elif num > 0:
            times, values = self._times[:-num], self._values[num:]
        else:
            times, values = self._times[-num:], self._values[:num]
        return TimeSeries(times, values,
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def prune(self, interval):
        """
        keep only the times(and their associated values) that are at least `interval` distance apart

        Parameters
        ----------
        interval: numeric, required
            the minimum distance between times to be preserved
        """
        new_times, new_values = prune_lists(interval, self._times, self._values)
        return TimeSeries(new_times, new_values,
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

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
        return TimeSeries(new_times, new_values,
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

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

        if start is not None and start < times[0] and not self.use_fv:
            # add default beginning value to front of list
            times = [start] + times
            values = [self.first_val] + values

        start_idx = index_of(start, times, begin=True)
        if stop is False:
            # slice only wants one value
            if self.interpolate:
                return start, np.interp(start, times, values)
            return start, values[start_idx]

        stop_idx = index_of(stop, times)
        if not stop or stop > times[stop_idx]:
            # hack to include the last value if at end of list
            stop_idx += 1

        if self.interpolate:
            # TODO: figure out a cleaner way to do this
            slice_times = times[start_idx:stop_idx]
            if start > times[start_idx]:
                slice_times[0] = start
            if step:
                if stop <= times[stop_idx] and stop > slice_times[-1]:
                    slice_times[-1] = stop
                slice_times, = prune_lists(step, *pad_lists(1, slice_times))
            return slice_times, np.interp(slice_times, times, values).tolist()

        if step:
            return prune_lists(step, times[start_idx:stop_idx], values[start_idx:])

        return times[start_idx:stop_idx], values[start_idx:stop_idx]
