#!/bin/bash
set -eux

wget "ftp://ftp.ncdc.noaa.gov/pub/data/gsod/1951/${STATION_ID}-1951.op.gz"
gunzip ${STATION_ID}-1951.op.gz
mv ${STATION_ID}-1951.op ${STATION_ID}.full
sed -i 's/\* /  /g' ${STATION_ID}.full
