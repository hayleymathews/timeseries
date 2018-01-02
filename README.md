# TimeSeries
play around with timeseries data

### Install  
```python setup.py install```  

### Test  
```python setup.py test```

### Use
#### instantiation
create timeseries from lists, tuples, or dictionaries  
TimeSeries will sort all entries based on time

```
python
>>> from timeseries.timeseries import TimeSeries
>>> t1 = TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
>>> t2 = TimeSeries([(0, 0), (5, 5), (2, 2), (3, 3), (4, 4), (1, 1)])
>>> t3 = TimeSeries({0: 0, 5: 5, 2: 2, 3: 3, 4: 4, 1: 1})
>>> t1 == t2 == t3
True
>>> t1
TimeSeries: [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
```


#### slicing
single slices return time and value at that time  
slices before the first time return 0  (gets weird with negatives)  
slices after the last time return the last value  
range slices return a new TimeSeries object

```
python
>>> t1 = TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
>>> t1[1]
(1, 1)
>>> t1[-1]
(-1, 0)
>>> t1[6]
(6, 5)
>>> t1[1:5]
TimeSeries: [(1, 2), (2, 2), (3, 3), (4, 4)]
>>> t1[1:5:2]
TimeSeries: [(1, 1), (3, 3)]
```
slicing will work for any data type that supports addition, subtraction, and value comparison

```
python
>>> t2 = TimeSeries([date(2018, 1, 1), date(2018, 1, 6), date(2018, 1, 3), date(2018, 1, 4), date(2018, 1, 5), date(2018, 1, 2)], [1, 6, 3, 4, 5, 2])
>>> t2[date(2018, 1, 2)]
(datetime.date(2018, 1, 2), 2)
>>> t2[date(2018, 1, 7)]
(datetime.date(2018, 1, 7), 6)
>>> t2[date(2018, 1, 2)::timedelta(2)]
TimeSeries: [(datetime.date(2018, 1, 2), 2), (datetime.date(2018, 1, 4), 4), (datetime.date(2018, 1, 6), 6)]
```

slicing also supports interpolation

```
python
>>> t3 = TimeSeries([0, 2, 4, 6, 8], [0, 2, 4, 6, 8], interpolate=True)
>>> t3[1]
(1, 1.0)
>>> t3[1:8:2]
TimeSeries: [(1, 1.0), (3, 3.0), (5, 5.0), (7, 7.0)]
```

#### operators
```
python
>>> t1 = TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
>>> t2 = TimeSeries([0, 2, 4, 6, 8], [0, 2, 4, 6, 8])
>>> t1 + t2
TimeSeries: [(0, 0), (1, 1), (2, 4), (3, 5), (4, 8), (5, 9), (6, 11), (8, 13)]
>>> t1 - t1
TimeSeries: [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
>>> t1 * t1
TimeSeries: [(0, 0), (1, 1), (2, 4), (3, 9), (4, 16), (5, 25)]
>>> t2 / t1
TimeSeries: [(0, 0), (1, 0.0), (2, 1.0), (3, 0.6666666666666666), (4, 1.0), (5, 0.8), (6, 1.2), (8, 1.6)]
>>> t1 | t2
TimeSeries: [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (8, 8)]
```


#### mutators
```
python
>>> from timeseries import tilted, padded, pruned, shifted
>>> t1 = TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
>>> t2 = TimeSeries([0, 2, 4, 6, 8], [0, 2, 4, 6, 8])
>>> t3 = TimeSeries([0, 2, 4, 6, 8], [0, 2, 4, 6, 8], interpolate=True)
>>> tilted(t1, 10) # creates a new timeseries
TimeSeries: [(0, 0.0), (1, 2.0), (2, 4.0), (3, 6.0), (4, 8.0), (5, 10.0)]
>>> t1.tilt(10) # tilts values in place
>>> t1
TimeSeries: [(0, 0.0), (1, 2.0), (2, 4.0), (3, 6.0), (4, 8.0), (5, 10.0)]
>>> padded(t2, 1)
TimeSeries: [(0, 0), (1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 6), (7, 8), (8, 8)]
>>> t3.pad(1)
>>> t3 # interpolated padding
TimeSeries: [(0, 0.0), (1, 1.0), (2, 2.0), (3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0), (7, 7.0), (8, 8.0)]
>>> pruned(t3[1:], 2)
TimeSeries: [(1, 1.0), (3, 3.0), (5, 5.0), (7, 7.0)]
>>> shifted(t1, -1)
TimeSeries: [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)]
>>> t1.shift(2)
>>> t1
TimeSeries: [(0, 2), (1, 3), (2, 4), (3, 5)]
```

#### utilities
```
python
>>> t1 = TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
>>> t1.times
[0, 1, 2, 3, 4, 5]
>>> t1.values
[0, 1, 2, 3, 4, 5]
>>> t1[2] = 8
>>> t1
TimeSeries: [(0, 0), (1, 1), (2, 8), (3, 3), (4, 4), (5, 5)]
>>> t1.tolists()
([0, 1, 2, 3, 4, 5], [0, 1, 8, 3, 4, 5])
>>> t1.topairs()
[(0, 0), (1, 1), (2, 8), (3, 3), (4, 4), (5, 5)]
>>> t1.todict()
{0: 0, 1: 1, 2: 8, 3: 3, 4: 4, 5: 5}
```
