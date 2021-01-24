# temperature-history
statistics about historical temperatures from NOAA data

## setup
create and activate python virtual environment:
```
virtualenv venv
source venv/bin/activate
```

install dependencies:
```
pip install -r requirements.txt
```

find desired station from `data/isd-history.txt` (default `160800-99999`, MILANO LINATE)

initialize data (from 1951):
```
STATION_ID=160800-99999 data/init_data.py
```

update data:
```
STATION_ID=160800-99999 data/update_data.py
```
## plot graphs

```
STATION_ID=160800-99999 ./generate_graphs.py
```
