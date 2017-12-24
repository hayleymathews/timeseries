# TimeSeries
play around with timeseries data

### Install  
```python setup.py install```  

### Test  
```python setup.py test```

### Use  
```
python
>>> from timeseries.timeseries import TimeSeries
>>> t = TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
>>> t
TimeSeries: [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
>>> t[1] # get a single slice to see the time and value
(1, 1)
>>> t[1] = 2 # edit values in place
>>> t
TimeSeries: [(0, 0), (1, 2), (2, 2), (3, 3), (4, 4), (5, 5)]
>>> t[1:5] # slice a range and get a TimeSeries back
TimeSeries: [(1, 2), (2, 2), (3, 3), (4, 4)]
>>> t2 = TimeSeries(zip(range(0, 10), range(0, 10))) # create TimeSeries from tuples too
>>> t3 = TimeSeries({x:x for x in range(5)}) # or dictionaries
>>> t + t2 # add TimeSeries together
TimeSeries: [(0, 0), (1, 3), (2, 4), (3, 6), (4, 8), (5, 10), (6, 11), (7, 12), (8, 13), (9, 14)]
>>> t * t3
TimeSeries: [(0, 0), (1, 2), (2, 4), (3, 9), (4, 16), (5, 20)]
>>> t & t2 # or combine
TimeSeries: [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
>>> t4 = TimeSeries({x:x for x in range(0, 10, 2)})
>>> t5 = TimeSeries({x:x for x in range(0, 10, 2)}, interpolate=True)
>>> t4[1:6:2]
TimeSeries: [(0, 0), (2, 2), (4, 4)]
>>> t5[1:6:2] # get interpolated slices
TimeSeries: [(1, 1.0), (3, 3.0), (5, 5.0)]
>>> t4.pad(1) # pad TimeSeries with missing data
TimeSeries: [(0, 0), (1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 6), (7, 8), (8, 8)]
>>> t5.pad(1)
TimeSeries: [(0, 0.0), (1, 1.0), (2, 2.0), (3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0), (7, 7.0), (8, 8.0)]
>>> t5.tolists()
([0, 2, 4, 6, 8], [0, 2, 4, 6, 8])
>>> t5.topairs()
[(0, 0), (2, 2), (4, 4), (6, 6), (8, 8)]
>>> t5.todict()
{0: 0, 8: 8, 2: 2, 4: 4, 6: 6}
```
