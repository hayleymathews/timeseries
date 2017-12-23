"""
test timeseries class
"""
from unittest import TestCase
from timeseries.timeseries import TimeSeries


class TestTimeSeries(TestCase):
    def test_creation_from_lists(self):
        t = TimeSeries(range(5), range(5))
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 2, 3, 4])

    def test_creation_from_tuples(self):
        t = TimeSeries(zip(range(5), range(5)))
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 2, 3, 4])

    def test_creation_from_dict(self):
        t = TimeSeries({x: x for x in range(5)})
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 2, 3, 4])

    def test_single_slice(self):
        t = TimeSeries(range(2, 6, 2), range(2, 6, 2))
        self.assertEqual(t[0], 0)
        self.assertEqual(t[1], 0)
        self.assertEqual(t[2], 2)
        self.assertEqual(t[3], 2)

    def test_sincle_slice_with_first_val(self):
        t = TimeSeries(range(2, 6, 2), range(2, 6, 2), use_fv=False, first_val=-1)
        self.assertEqual(t[0], -1)
        self.assertEqual(t[1], -1)
        self.assertEqual(t[2], 2)

    def test_sincle_slice_with_interpolation(self):
        t = TimeSeries(range(2, 6, 2), range(2, 6, 2), interpolate=True)
        self.assertEqual(t[0], 0)
        self.assertEqual(t[2], 2)
        self.assertEqual(t[3], 3)

    def test_range_slice(self):
        t = TimeSeries(range(2, 10, 2), range(2, 10, 2))
        self.assertEqual(t[2:], [2, 4, 6, 8])
        self.assertEqual(t[2:8], [2, 4, 6])

    def test_range_slice_with_first_val(self):
        t = TimeSeries(range(2, 10, 2), range(2, 10, 2), use_fv=False, first_val=-1)
        self.assertEqual(t[0:6], [-1, 2, 4])
        self.assertEqual(t[0:], [-1, 2, 4, 6, 8])

    def test_range_slice_with_interpolation(self):
        pass
        # TODO: fix bugs in slicer and finish me
        # t = TimeSeries(range(2, 10, 2), range(2, 10, 2), interpolate=True)
        # self.assertEqual(t[3:6], [3, 4])

    def test_range_slice_with_step(self):
        t = TimeSeries(range(0, 10), range(0, 10))
        self.assertEqual(t[0:8:2], [0, 2, 4, 6])

    def test_aligned_add(self):
        t = TimeSeries(range(5), range(5)) + TimeSeries(range(5), range(5))
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 2, 4, 6, 8])

    def test_misaligned_add(self):
        t = TimeSeries([0, 2, 4], [0, 2, 4]) + TimeSeries([1, 2, 3], [1, 2, 3])
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 4, 5, 7])

    def test_aligned_subtract(self):
        t = TimeSeries(range(5), range(5)) - TimeSeries(range(5), range(5))
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 0, 0, 0, 0])

    def test_misaligned_subtract(self):
        t = TimeSeries([0, 2, 4], [0, 2, 4]) - TimeSeries([1, 2, 3], [1, 2, 3])
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, -1, 0, -1, 1])

    def test_aligned_multiply(self):
        t = TimeSeries(range(5), range(5)) * TimeSeries(range(5), range(5))
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 4, 9, 16])

    def test_misaligned_multiply(self):
        t = TimeSeries([0, 2, 4], [0, 2, 4]) * TimeSeries([1, 2, 3], [1, 2, 3])
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 0, 4, 6, 12])

    def test_aligned_divide(self):
        t = TimeSeries(range(5), range(5)) / TimeSeries(range(5), range(5))
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 1, 1, 1])

    def test_misaligned_divide(self):
        t = TimeSeries([0, 2, 4], [0, 2, 4]) / TimeSeries([1, 2, 3], [1, 2, 3])
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 0, 1, 2./3, 4./3])

    def test_combine(self):
        t = TimeSeries([0, 2, 4], [0, 2, 4]) & TimeSeries([1, 2, 3], [1, 2, 3])
        self.assertEqual(t.times,  [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 2, 3, 4])

    def test_combine_with_conflicting_value(self):
        t = TimeSeries([0, 2, 4], [0, 2, 4]) & TimeSeries([1, 2, 3], [1, 100, 3])
        self.assertEqual(t.times, [0, 1, 2, 3, 4])
        self.assertEqual(t.values, [0, 1, 100, 3, 4])
