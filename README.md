# tugmeteo
TÜBİTAK National Observatory Meteorology Library

## Examples

```python
from tugmeteo import TugMeteo

met = TugMeteo()

raw_meteos = met.get_last_meteo('RTT150')
print(raw_meteos)
```

```json
{
    "timestamp": "2019-05-30T18:45:31",
    "Temperature": 16.6,
    "Dome Temperature": 18.3,
    "Coude Temperature": 12.8,
    "Humidity": 45.0,
    "Dome Humidity": 51.0,
    "Coude Humidity": 55.3,
    "Barometer": 759.8,
    "Wind": 0.0,
    "Wind Chill": 16.6,
    "Dewpoint": 4.6,
    "High Temperature": 18.3,
    "Low Temperature": 14.1,
    "High Humidity": 47.0,
    "Low Humidity": 24.0,
    "High Barometer": 761.3,
    "Low Barometer": 759.5,
    "High Wind": 82.0,
    "Est. Cumulus Base": 1499.0,
}
```

```python
t = met.get_temperature()
print(t)
```

```json
{
    "timestamp": "2019-05-30T18:52:12",
    "info": "Temperature",
    "RTT150": 16.7,
    "T100": 16.7,
    "T60": 17.3,
}
```

```python
table = met.get_meteo_archives(start_date='2019-02-10', end_date='2019-05-31')
print(table)
```

```
                Timestamp  Temp  Chill HIndex Humid Dewpt  ... WindDir  Rain    Barom Solar     ET UV
0     2019-02-10 00:05:00  -6.6  -10.5   -6.6    91  -7.8  ...     337  0.00  748.766     0  0.000  0
1     2019-02-10 00:10:00  -6.6   -6.6   -6.6    91  -7.8  ...     337  0.00  748.699     0  0.000  0
2     2019-02-10 00:15:00  -6.6   -6.6   -6.6    91  -7.8  ...     337  0.00  748.699     0  0.000  0
3     2019-02-10 00:20:00  -6.6   -9.8   -6.6    91  -7.8  ...     337  0.00  748.733     0  0.000  0
4     2019-02-10 00:25:00  -6.6  -10.4   -6.6    92  -7.6  ...     337  0.00  748.699     0  0.000  0
...                   ...   ...    ...    ...   ...   ...  ...     ...   ...      ...   ...    ... ..
31552 2019-05-30 23:35:00  13.1   13.1   13.1    47   2.1  ...      67  0.00  759.637     0  0.000  0
31553 2019-05-30 23:40:00  13.1   13.1   13.1    47   2.1  ...      67  0.00  759.806     0  0.000  0
31554 2019-05-30 23:45:00  13.1   13.1   13.1    48   2.3  ...      67  0.00  759.738     0  0.000  0
31555 2019-05-30 23:50:00  13.1   13.1   13.1    48   2.3  ...      67  0.00  759.705     0  0.000  0
31556 2019-05-30 23:55:00  13.1   13.1   13.1    49   2.6  ...      90  0.00  759.705     0  0.000  0
```
