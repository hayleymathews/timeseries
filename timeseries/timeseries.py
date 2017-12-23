"""
fun with timeseries data
"""
import numpy as np
from utils import index_of, prune_lists


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
        if len(args) > 1:
            self._times = args[0]
            self._values = args[1]
        elif isinstance(args[0], list):
            self._times = [x[0] for x in args[0]]
            self._values = [x[1] for x in args[0]]
        elif isinstance(args[0], dict):
            self._times = sorted(args[0].keys())
            self._values = [args[0][x] for x in self._times]
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

    def __str__(self):
        return 'TimeSeries: [{}], [{}]'.format(self._times, self._values)

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
        # TODO: this feels wrong. dont like exposing a way to mutate the value
        time_index = index_of(time, self._times)
        self._values[time_index] = value

    def __add__(self, other_timeseries):
        tv = {}
        for time in self._times + other_timeseries.times:
            tv[time] = self[time][1] + other_timeseries[time][1]
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times],
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __sub__(self, other_timeseries):
        tv = {}
        for time in self._times + other_timeseries.times:
            tv[time] = self[time][1] - other_timeseries[time][1]
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times],
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __mul__(self, other_timeseries):
        tv = {}
        for time in self._times + other_timeseries.times:
            tv[time] = self[time][1] * other_timeseries[time][1]
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times],
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __div__(self, other_timeseries):
        tv = {}
        for time in self._times + other_timeseries.times:
            try:
                tv[time] = 1. * self[time][1] / other_timeseries[time][1]
            except ZeroDivisionError:
                tv[time] = 0
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times],
                          interpolate=self.interpolate,
                          use_fv=self.use_fv,
                          first_val=self.first_val)

    def __and__(self, other_timeseries):
        # TODO: does this make sense, if conflict, take the other_timeseries values
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
            return TimeSeries(self._times, self._values,
                              interpolate=self.interpolate,
                              use_fv=self.use_fv,
                              first_val=self.first_val)
        if num > 0:
            return TimeSeries(self._times[:-num], self._values[num:],
                              interpolate=self.interpolate,
                              use_fv=self.use_fv,
                              first_val=self.first_val)
        return TimeSeries(self._times[-num:], self._values[:num],
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
        padded_times, padded_values = [], []
        prev_time = None
        last_val = self._values[-1]
        for i, curr_time in enumerate(self._times):
            # BUG: this is looking into the future
            curr_val = self._values[i]
            while prev_time is not None and curr_time - prev_time > interval:
                prev_time = prev_time + interval
                if not keep_end or last_val - curr_val >= interval:
                    padded_times.append(prev_time)
                    padded_values.append(curr_val)
            padded_times.append(curr_time)
            padded_values.append(curr_val)
            prev_time = curr_time
        if self.interpolate:
            values = np.interp(padded_times, self._times, self._values).tolist()
            return TimeSeries(padded_times, values,
                              interpolate=self.interpolate,
                              use_fv=self.use_fv,
                              first_val=self.first_val)
        return TimeSeries(padded_times, padded_values,
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

        if start < times[0] and not self.use_fv:
            # add default beginning value to front of list
            times = [start] + times
            values = [self.first_val] + values

        # BUG: [::2] type slice will fail with index_of None returning end of list
        start_idx = index_of(start, times)
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
            # BUG: if start/stop not in list this will get the wrong slice times
            slice_times = times[start_idx:stop_idx]
            if step:
                slice_times, = prune_lists(step, times)
            return slice_times, np.interp(slice_times, times, values).tolist()

        if step:
            return prune_lists(step, times[start_idx:stop_idx], values[start_idx:])

        return times[start_idx:stop_idx], values[start_idx:stop_idx]
