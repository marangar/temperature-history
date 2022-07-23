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
STATION_ID=160800-99999 data/init_data.sh
```

update data:
```
STATION_ID=160800-99999 data/update_data.py
```
## plot graphs

show average temperature history for different seasons:
```
STATION_ID=160800-99999 OUT_DIR=output ./generate_graphs.py
```

show history of 1-day temperature swing index for different seasons:
```
PLOT_VAR=1 STATION_ID=160800-99999 OUT_DIR=output ./generate_graphs.py
```

## example
something like [this](https://marangar.github.io/temperature-history-site) can be obtained
