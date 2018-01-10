"""
all the same fun of regular TimeSeries, but values can be dictionaries


need to figure out the right behavior for slicing
general idea is you have a timeseries where the vals are dictionaries
TimeSeries: [(0, {'v': 1,
                  'by': 'me'}),
             (1, {'v': 2,
                  'k': 2,
                  'by': 'you'}),
             (2, {'v': 3})]
some of the keys in the dictionary are data keys that you care about ('v', 'k')
and some of them are just sort of bonus contextual info ('by')
slicing should keep track of the data keys the same way a timeseries of lists
so t[2] = (2, {'v': 3,
               'k': 2})
k was unchanged since its last entry, and so is still 2, we dont care about by so it didnt pad out..


should do its best to keep log n for slicing. it ... does not do that right now

"""
from timeseries import TimeSeries
from utils import combine_dicts, float_div, index_of, pad_lists
import numpy as np
from operator import add, mul, sub
from collections import defaultdict


class TimeSeriesDict(TimeSeries):
    """
    work with timeseries data where the values are dictionaries

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

    val_keys: list, optional
        list of keys that are data keys in timeseries, these keys are the ones used in add/sub/etc operations
        default ['v']
    """
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            ts_iter = sorted(zip(args[0], args[1]))
        elif isinstance(args[0], list):
            ts_iter = sorted(args[0])
        elif isinstance(args[0], dict):
            ts_iter = sorted(args[0].items())
        else:
            raise Exception

        self.interpolate = kwargs.get('interpolate', False)
        self.first_val = kwargs.get('first_val', 0)
        self.val_keys = kwargs.get('val_keys', ['v'])
        self._times, self._values = [None] * len(ts_iter), [None] * len(ts_iter)
        self._dict = defaultdict(lambda: ([], []))

        # TODO: this is a crappy implementaton
        # kills the benefit of having sparse data in order to get single slices accurate
        # and slices are slow because it has to slice each of these
        for i, (ts, val) in enumerate(ts_iter):
            self._times[i], self._values[i] = ts, val
            for k, v in val.iteritems():
                if k in self.val_keys:
                    self._dict[k][0].append(ts)
                    self._dict[k][1].append(v)

    def __getitem__(self, key):
        times, values = self._new_slice(self._times, self._values, key)
        if not isinstance(times, list):
            return times, values
        return TimeSeriesDict(times, values,
                              interpolate=self.interpolate,
                              first_val=self.first_val,
                              val_keys=self.val_keys)

    def __add__(self, other_timeseries):
        return TimeSeriesDict(self._times_values_op(other_timeseries, add),
                              interpolate=self.interpolate,
                              first_val=self.first_val,
                              val_keys=self.val_keys)

    def __sub__(self, other_timeseries):
        return TimeSeriesDict(self._times_values_op(other_timeseries, sub),
                              interpolate=self.interpolate,
                              first_val=self.first_val,
                              val_keys=self.val_keys)

    def __mul__(self, other_timeseries):
        return TimeSeriesDict(self._times_values_op(other_timeseries, mul),
                              interpolate=self.interpolate,
                              first_val=self.first_val,
                              val_keys=self.val_keys)

    def __div__(self, other_timeseries):
        return TimeSeriesDict(self._times_values_op(other_timeseries, float_div),
                              interpolate=self.interpolate,
                              first_val=self.first_val,
                              val_keys=self.val_keys)

    def __or__(self, other_timeseries):
        tv = dict(zip(self._times, self._values))
        tv.update(dict(zip(other_timeseries.times, other_timeseries.values)))
        return TimeSeriesDict(tv,
                              interpolate=self.interpolate,
                              first_val=self.first_val,
                              val_keys=self.val_keys)

    def _new_slice(self, times, values, key):
        """
        slicing functionality for timeseries
        """
        # TODO: yikes.
        try:
            start, stop, step = key.start, key.stop, key.step
            if all(x is None for x in [start, stop, step]):
                # [:] slice, return everything
                return times, values
        except AttributeError:
            start, stop, step = key, False, None

        start_idx = index_of(start, times, begin=True)
        if stop is False:
            slice_dict = values[start_idx]
            for key_val, (times, values) in self._dict.iteritems():
                if start is not None and start < times[0] and self.first_val is not False:
                    # add default beginning value to front of list
                    times = [start] + times
                    values = [self.first_val] + values
                if self.interpolate:
                    slice_dict[key_val] = np.interp(start, times, values)
                else:
                    slice_dict[key_val] = values[index_of(start, times, begin=True)]
            return start, slice_dict
        raise NotImplementedError

    def _times_values_op(self, other_timeseries, op):
        """
        helper function to perform operations on timeseries
        """
        tv = {}
        val_keys = set(self.val_keys) | set(other_timeseries.val_keys)
        op_list = [op] * len(val_keys)
        for time in sorted(self._times + other_timeseries.times):
            s_values, o_values = self[time][1], other_timeseries[time][1]
            tv[time] = combine_dicts(s_values, o_values, val_keys, op_list)
        return tv
