"""
"""
import numpy as np
from utils import index_of, prune_lists


class TimeSeries(object):
    """
    class to provide basic functionality for working with timeseries data

    Parameters
    ----------
    use_fv : bool, optional
        timeseries will return first value if a slice is requested before the first time
        default False

    interpolate : bool, optional
        timeseries will interpolate value if a slice is requested at a time that is not in timeseries
        default False

    """
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.times = args[0]
            self.values = args[1]
        elif isinstance(args[0], list):
            self.times = [x[0] for x in args[0]]
            self.values = [x[1] for x in args[0]]
        elif isinstance(args[0], dict):
            self.times = sorted(args[0].keys())
            self.values = [args[0][x] for x in self.times]
        else:
            raise Exception
        self.use_fv = kwargs.get('use_fv', False)
        self.interpolate = kwargs.get('interpolate', False)
        self.first_val = kwargs.get('first_val', 0)

    def __repr__(self):
        return 'TimeSeries: {}'.format(zip(self.times, self.values))

    def __str__(self):
        return 'TimeSeries: [{}], [{}]'.format(self.times, self.values)

    def __len__(self):
        return len(self.times)

    def __iter__(self):
        for time, value in zip(self.times, self.values):
            yield (time, value)

    def __getitem__(self, key):
        return self._new_slice(self.times, self.values, key)

    def __setitem__(self, time, value):
        # TODO: this feels wrong. dont like exposing a way to mutate the value
        time_index = index_of(time, self.times)
        self.values[time_index] = value

    def __add__(self, other_timeseries):
        tv = {}
        for time in self.times + other_timeseries.times:
            tv[time] = self[time] + other_timeseries[time]
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times])

    def __sub__(self, other_timeseries):
        tv = {}
        for time in self.times + other_timeseries.times:
            tv[time] = self[time] - other_timeseries[time]
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times])

    def __mul__(self, other_timeseries):
        tv = {}
        for time in self.times + other_timeseries.times:
            tv[time] = self[time] * other_timeseries[time]
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times])

    def __div__(self, other_timeseries):
        tv = {}
        for time in self.times + other_timeseries.times:
            try:
                tv[time] = 1. * self[time] / other_timeseries[time]
            except ZeroDivisionError:
                tv[time] = 0
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times])

    def __and__(self, other_timeseries):
        # TODO: does this make sense, if conflict, take the other_timeseries values
        tv = dict(zip(self.times, self.values))
        tv.update(dict(zip(other_timeseries.times, other_timeseries.values)))
        times = sorted(tv)
        return TimeSeries(times, [tv[time] for time in times])

    def tilt(self, new_end):
        """
        tilt values of timeseries to meet a new end value

        Parameters
        ----------
        new_end: numeric, required
            the
        """
        values = np.array(self.values)
        start = values[0]
        rise = 1.0 * (new_end - start)
        run = values[-1] - start
        if run:
            new_slope = rise / run
            self.values = (start + (new_slope * (values - start))).tolist()
        new_slope = rise / (len(values) - 1)
        return TimeSeries(self.times, [start + new_slope * i for i in range(len(values))])

    def prune(self, interval):
        """
        keep only the times(and their associated values) that are at least interval distance apart
        """
        new_times, new_values = prune_lists(interval, self.times, self.values)
        return TimeSeries(new_times, new_values)

    def shift(self, num):
        """
        shift entire timeseries by num, rightshift if positive, leftshift if negative
        """
        if not num:
            return TimeSeries(self.times, self.values)
        if num > 0:
            return TimeSeries(self.times[num:], self.values[:-num])
        return TimeSeries(self.times[:num], self.values[-num:])

    def pad(self, interval, interpolate=True, keep_end=False):
        """
        pad timeseries so that there is a time (and value) at every interval
        if interpolate, the values will be interpolated, otherwise the previous value will be repeated
        """
        padded_times, padded_values = [], []
        prev_time = None
        last_val = self.values[-1]
        for i, curr_time in enumerate(self.times):
            curr_val = self.values[i]
            while prev_time is not None and curr_time - prev_time > interval:
                prev_time = prev_time + interval
                if not keep_end or last_val - curr_val >= interval:
                    padded_times.append(prev_time)
                    padded_values.append(curr_val)
            padded_times.append(curr_time)
            padded_values.append(curr_val)
            prev_time = curr_time
        if interpolate:
            return TimeSeries(padded_times, np.interp(padded_times, self.times, self.values).tolist())
        return TimeSeries(padded_times, padded_values)

    def topairs(self):
        return list(zip(self.times, self.values))

    def tolists(self):
        return self.times, self.values

    def todict(self):
        return {self.times[i]: self.values[i] for i in range(len(self.times))}

    def _new_slice(self, times, values, key):
        """
        slicing functionality for timeseries
        """
        try:
            start, stop, step = key.start, key.stop, key.step
            if all(x is None for x in [start, stop, step]):
                # [:] slice, return everything
                return values
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
                return np.interp(start, times, values)
            return values[start_idx]

        stop_idx = index_of(stop, times)
        if not stop or stop > times[stop_idx]:
            # hack to include the last value if at end of list
            stop_idx += 1

        if self.interpolate:
            # BUG: if start/stop not in list this will get the wrong slice times
            slice_times = times[start_idx:stop_idx]
            if step:
                slice_times, = prune_lists(step, times)
            return np.interp(slice_times, times, values).tolist()

        if step:
            _, values = prune_lists(step, times[start_idx:stop_idx], values[start_idx:])
            return values

        return values[start_idx: stop_idx]
