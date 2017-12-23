# timeseries
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
>>> t[1]
(1, 1)
>>> t[1:5]
TimeSeries: [(1, 1), (2, 2), (3, 3), (4, 4)]
>>> t + TimeSeries([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5])
TimeSeries: [(0, 0), (1, 2), (2, 4), (3, 6), (4, 8), (5, 10)]
>>> t & TimeSeries([6, 7, 8], [6, 7, 8])
TimeSeries: [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)]
```
