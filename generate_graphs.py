#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import os
import numpy as np
from subprocess import check_output
from six.moves import range
from utils import date_prefixes
from plotting import plot_season_avg, plot_season_swing
from compute import swing, compute_season_value, moving_average
from db import get_data_frame, get_t_min_max, get_years

PLOT_VAR = os.getenv('PLOT_VAR')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.getenv('OUT_DIR', 'output')
STATIONS_DB = os.path.join(ROOT_DIR, 'data', 'isd-history.txt')
STATION_ID = os.getenv('STATION_ID', '160800-99999')
STATION_KEY = STATION_ID.replace('-', ' ')
STATION_NAME = check_output(['grep', STATION_KEY, STATIONS_DB]).split()[2]
DATA_FILE = os.path.join(ROOT_DIR, 'data', STATION_ID + '.full')
MAW_LEN = 5 # moving average window length

def main():
    # read data-frame
    df = get_data_frame(DATA_FILE)

    # determine oldest and latest years in data file
    start_year, end_year = get_years(df)
    years = list(range(start_year, end_year + 1))

    # for every season, build date prefixes
    spring_pref, summer_pref, autumn_pref, winter_pref = date_prefixes(df, years)

    # for every season, get min and max temps -> one panda-series for every year
    spring_tmins, spring_tmaxs = get_t_min_max(df, years, spring_pref)
    summer_tmins, summer_tmaxs = get_t_min_max(df, years, summer_pref)
    autumn_tmins, autumn_tmaxs = get_t_min_max(df, years, autumn_pref)
    winter_tmins, winter_tmaxs = get_t_min_max(df, years, winter_pref)

    # compute desired value for every serie -> one value for every year
    compute_func = swing if PLOT_VAR else np.mean
    spring_cmpt_mins = compute_season_value(compute_func, spring_tmins)
    summer_cmpt_mins = compute_season_value(compute_func, summer_tmins)
    autumn_cmpt_mins = compute_season_value(compute_func, autumn_tmins)
    winter_cmpt_mins = compute_season_value(compute_func, winter_tmins)
    spring_cmpt_maxs = compute_season_value(compute_func, spring_tmaxs)
    summer_cmpt_maxs = compute_season_value(compute_func, summer_tmaxs)
    autumn_cmpt_maxs = compute_season_value(compute_func, autumn_tmaxs)
    winter_cmpt_maxs = compute_season_value(compute_func, winter_tmaxs)

    # calculate moving-average of previous computed arrays
    spring_mavg_mins = moving_average(spring_cmpt_mins, MAW_LEN)
    summer_mavg_mins = moving_average(summer_cmpt_mins, MAW_LEN)
    autumn_mavg_mins = moving_average(autumn_cmpt_mins, MAW_LEN)
    winter_mavg_mins = moving_average(winter_cmpt_mins, MAW_LEN)
    spring_mavg_maxs = moving_average(spring_cmpt_maxs, MAW_LEN)
    summer_mavg_maxs = moving_average(summer_cmpt_maxs, MAW_LEN)
    autumn_mavg_maxs = moving_average(autumn_cmpt_maxs, MAW_LEN)
    winter_mavg_maxs = moving_average(winter_cmpt_maxs, MAW_LEN)

    # build x-axis labels
    spring_xticks = ['%02d' % (i % 100) for i in years]
    summer_xticks = ['%02d' % (i % 100) for i in years]
    autumn_xticks = ['%02d' % (i % 100) for i in years]
    winter_xticks = ['%02d/%02d' % (i % 100, (i+1) % 100) for i in years]

    # plot
    plot_func = plot_season_swing if PLOT_VAR else plot_season_avg
    plot_func(years, 'Mar-May', STATION_NAME, spring_xticks, spring_cmpt_mins,
              spring_cmpt_maxs, spring_mavg_mins, spring_mavg_maxs,
              os.path.join(OUT_DIR, "spring.svg"))
    plot_func(years, 'Jun-Aug', STATION_NAME, summer_xticks, summer_cmpt_mins,
              summer_cmpt_maxs, summer_mavg_mins, summer_mavg_maxs,
              os.path.join(OUT_DIR, "summer.svg"))
    plot_func(years, 'Sep-Nov', STATION_NAME, autumn_xticks, autumn_cmpt_mins,
              autumn_cmpt_maxs, autumn_mavg_mins, autumn_mavg_maxs,
              os.path.join(OUT_DIR, "autumn.svg"))
    plot_func(years, 'Dec-Feb', STATION_NAME, winter_xticks, winter_cmpt_mins,
              winter_cmpt_maxs, winter_mavg_mins, winter_mavg_maxs,
              os.path.join(OUT_DIR, "winter.svg"))

if __name__ == "__main__":
    main()
