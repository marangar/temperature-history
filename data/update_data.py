#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import os
from subprocess import check_output
from ftplib import FTP, error_perm
from gzip import GzipFile
from datetime import datetime, date, timedelta
from io import BytesIO
from six.moves import range

NOAA_FTP_SERVER = 'ftp.ncdc.noaa.gov'
NOAA_FTP_DIR = '/pub/data/gsod'
STATION_ID = os.getenv('STATION_ID', '160800-99999')
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(DATA_DIR, STATION_ID + '.full')

last_line = check_output(['tail', '-1', DATA_FILE])
last_date_str = last_line.split()[2]
last_year = int(last_date_str[:4])
last_month = int(last_date_str[4:6])
last_day = int(last_date_str[6:])
last_date = date(last_year, last_month, last_day)
curr_date = datetime.now().date()
delta_date = curr_date - last_date
delta_days = []
for i in range(1, delta_date.days + 1):
    day = last_date + timedelta(days=i)
    day_str = day.strftime('%Y%m%d')
    delta_days.append(day_str)
delta_years = curr_date.year - last_date.year
delta_years_data = []

ftp = FTP(NOAA_FTP_SERVER)
ftp.login()
for i in range(delta_years + 1):
    year = str(last_year + i)
    try:
        ftp.cwd(os.path.join(NOAA_FTP_DIR, year))
    except error_perm:
        print('Cannot find data for year ' +  year)
        continue
    remote_file = STATION_ID + '-' + year + '.op'
    remote_gz_file = remote_file + '.gz'
    mem_file = BytesIO()
    try:
        ftp.retrbinary('RETR ' + remote_gz_file, mem_file.write)
        print('Downloaded ' + remote_gz_file)
    except error_perm:
        print('Cannot download data for year ' +  year)
        continue
    mem_file.seek(0)
    content = GzipFile(fileobj=mem_file, mode='rb').read().decode('utf-8')
    content_lines = content.splitlines(True)
    content_lines = content_lines[1:]
    delta_years_data.extend(content_lines)
ftp.close()

print('Writing data file ...')
with open(DATA_FILE, "a") as f:
    for day in delta_days:
        for line in delta_years_data:
            if day in line:
                f.write(line.replace('* ', '  '))
