#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import os
import numpy as np
import pandas
from subprocess import check_output
from six.moves import range
from utils import f2c, replace_nan, valid_elements, date_prefixes
from plotting import plot_season_avg, plot_season_swing
from compute import smooth, swing

PLOT_VAR = os.getenv('PLOT_VAR')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIONS_DB = os.path.join(ROOT_DIR, 'data', 'isd-history.txt')
STATION_ID = os.getenv('STATION_ID', '160800-99999')
STATION_KEY = STATION_ID.replace('-', ' ')
STATION_NAME = check_output(['grep', STATION_KEY, STATIONS_DB]).split()[2]
DATA_FILE = os.path.join(ROOT_DIR, 'data', STATION_ID + '.full')
MAW_LEN = 5 # moving average window length

if __name__ == "__main__":
    # parse data file
    df = pandas.read_csv(filepath_or_buffer=DATA_FILE,
                         delim_whitespace=True, header=None,
                         names=['STN---', 'WBAN', 'YEARMODA', 'TEMP',
                                'TEMP_CNT', 'DEWP', 'DWEP_CNT', 'SLP',
                                'SLP_CNT', 'STP', 'STP_CNT', 'VISIB',
                                'VISIB_CNT', 'WDSP', 'WDSP_CNT', 'MXSPD',
                                'GUST', 'MAX', 'MIN', 'PRCP', 'SNDP', 'FRSHTT'])

    # determine oldest and latest years in data file
    start_year = int(df['YEARMODA'].values[1][:4])
    end_year = int(df['YEARMODA'].values[-1][:4])
    years = list(range(start_year, end_year + 1))

    # for every season, build date prefixes
    spring_pref, summer_pref, autumn_pref, winter_pref = date_prefixes(df, years)

    # for every season, build list of pandas-series -> one serie for every year
    match_criterion = df['YEARMODA'].str.startswith
    spring_tmins = [df.loc[match_criterion(spring_pref[y])]['MIN']
                    for y in years]
    spring_tmaxs = [df.loc[match_criterion(spring_pref[y])]['MAX']
                    for y in years]
    summer_tmins = [df.loc[match_criterion(summer_pref[y])]['MIN']
                    for y in years]
    summer_tmaxs = [df.loc[match_criterion(summer_pref[y])]['MAX']
                    for y in years]
    autumn_tmins = [df.loc[match_criterion(autumn_pref[y])]['MIN']
                    for y in years]
    autumn_tmaxs = [df.loc[match_criterion(autumn_pref[y])]['MAX']
                    for y in years]
    winter_tmins = [df.loc[match_criterion(winter_pref[y])]['MIN']
                    for y in years]
    winter_tmaxs = [df.loc[match_criterion(winter_pref[y])]['MAX']
                    for y in years]

    # compute value for every serie -> one value for every year
    compute_func = swing if PLOT_VAR else np.mean
    spring_avg_mins = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in spring_tmins])
    summer_avg_mins = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in summer_tmins])
    autumn_avg_mins = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in autumn_tmins])
    winter_avg_mins = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in winter_tmins])
    spring_avg_maxs = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in spring_tmaxs])
    summer_avg_maxs = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in summer_tmaxs])
    autumn_avg_maxs = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in autumn_tmaxs])
    winter_avg_maxs = np.array([compute_func(f2c(valid_elements(temps)))
                                for temps in winter_tmaxs])

    # calculate moving-average of previous arrays
    spring_mavg_mins = smooth(replace_nan(spring_avg_mins), MAW_LEN, 'flat')
    summer_mavg_mins = smooth(replace_nan(summer_avg_mins), MAW_LEN, 'flat')
    autumn_mavg_mins = smooth(replace_nan(autumn_avg_mins), MAW_LEN, 'flat')
    winter_mavg_mins = smooth(replace_nan(winter_avg_mins), MAW_LEN, 'flat')
    spring_mavg_maxs = smooth(replace_nan(spring_avg_maxs), MAW_LEN, 'flat')
    summer_mavg_maxs = smooth(replace_nan(summer_avg_maxs), MAW_LEN, 'flat')
    autumn_mavg_maxs = smooth(replace_nan(autumn_avg_maxs), MAW_LEN, 'flat')
    winter_mavg_maxs = smooth(replace_nan(winter_avg_maxs), MAW_LEN, 'flat')

    # build x-axis labels
    spring_xticks = ['%02d' % (i % 100) for i in years]
    summer_xticks = ['%02d' % (i % 100) for i in years]
    autumn_xticks = ['%02d' % (i % 100) for i in years]
    winter_xticks = ['%02d/%02d' % (i % 100, (i+1) % 100) for i in years]

    # plot
    plot_func = plot_season_swing if PLOT_VAR else plot_season_avg
    plot_func(years, 'Mar-May', STATION_NAME, spring_xticks, spring_avg_mins,
              spring_avg_maxs, spring_mavg_mins, spring_mavg_maxs)
    plot_func(years, 'Jun-Aug', STATION_NAME, summer_xticks, summer_avg_mins,
              summer_avg_maxs, summer_mavg_mins, summer_mavg_maxs)
    plot_func(years, 'Sep-Nov', STATION_NAME, autumn_xticks, autumn_avg_mins,
              autumn_avg_maxs, autumn_mavg_mins, autumn_mavg_maxs)
    plot_func(years, 'Dec-Feb', STATION_NAME, winter_xticks, winter_avg_mins,
              winter_avg_maxs, winter_mavg_mins, winter_mavg_maxs)
