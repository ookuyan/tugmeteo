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
    'timestamp': '2019-05-30T18:45:31',
    'Temperature': 16.6,
    'Dome Temperature': 18.3,
    'Coude Temperature': 12.8,
    'Humidity': 45.0,
    'Dome Humidity': 51.0,
    'Coude Humidity': 55.3,
    'Barometer': 759.8,
    'Wind': 0.0,
    'Wind Chill': 16.6,
    'Dewpoint': 4.6,
    'High Temperature': 18.3,
    'Low Temperature': 14.1,
    'High Humidity': 47.0,
    'Low Humidity': 24.0,
    'High Barometer': 761.3,
    'Low Barometer': 759.5,
    'High Wind': 82.0,
    'Est. Cumulus Base': 1499.0,
}
```

```python
t = met.get_temperature()
print(t)
```

```json
{
    'timestamp': '2019-05-30T18:52:12',
    'info': 'Temperature',
    'RTT150': 16.7,
    'T100': 16.7,
    'T60': 17.3,
}
```
