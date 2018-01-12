"""
test timeseriesdict class
"""
from unittest import TestCase
from timeseries.timeseriesdict import TimeSeriesDict


class TestTimeSeries(TestCase):
    def test_aligned_add(self):
        t = TimeSeriesDict([0, 1, 2], [{'v': 0, 'by': 'me'}, {'v': 1, 'by': 'you'}, {'v': 2}])
        t += t
        self.assertEqual(t.times, [0, 1, 2])
        self.assertEqual(t.values, [{'v': 0, 'by': 'me'}, {'v': 2, 'by': 'you'}, {'v': 4}])

    def test_misaligned_add(self):
        t = TimeSeriesDict([0, 1, 2], [{'v': 0, 'by': 'me'}, {'v': 1, 'by': 'you'}, {'v': 2}])
        t2 = TimeSeriesDict([0, 2, 3], [{'v': 4, 'by': 'you'}, {'v': 5, 'by': 'you'}, {'v': 7, 'by': 'me'}])
        t3 = t + t2
        self.assertEqual(t3.times, [0, 1, 2, 3])
        self.assertEqual(t3.values, [{'v': 4, 'by': 'you'}, {'v': 5, 'by': 'you'},
                                     {'by': 'you', 'v': 7}, {'v': 9, 'by': 'me'}])

    def test_single_slice(self):
        t = TimeSeriesDict([1, 2, 3], [{'v': 1, 'by': 'me'}, {'v': 2, 'k': 2, 'by': 'you'}, {'v': 3}],
                           val_keys=['v', 'k'])
        self.assertEqual(t[0], (0, {'v': 0, 'k': 0}))
        self.assertEqual(t[1], (1, {'k': 0, 'by': 'me', 'v': 1}))
        self.assertEqual(t[2], (2, {'k': 2, 'by': 'you', 'v': 2}))
        self.assertEqual(t[3], (3, {'k': 2, 'v': 3}))

    def test_slice_with_interpolation(self):
        t = TimeSeriesDict(range(0, 6, 2), [{'v': 0, 'k': 1}, {'v': 2, 'k': 3}, {'v': 4, 'k': 5}],
                           interpolate=True, val_keys=['v', 'k'])
        self.assertEqual(t[1], (1, {'k': 2.0, 'v': 1.0}))
        t_slice = t[1:4:2]
        self.assertEqual(t_slice.times, [1, 3])
        self.assertEqual(t_slice.values, [{'k': 2.0, 'v': 1.0}, {'k': 4.0, 'v': 3.0}])
