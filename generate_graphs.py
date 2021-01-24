#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import os
import numpy as np
import pandas
import matplotlib.pyplot as plt
import math
from subprocess import check_output
from six.moves import range
from smooth import smooth

PLOT_VAR = os.getenv('PLOT_VAR')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIONS_DB = os.path.join(ROOT_DIR, 'data', 'isd-history.txt')
STATION_ID = os.getenv('STATION_ID', '160800-99999')
STATION_KEY = STATION_ID.replace('-', ' ')
STATION_NAME = check_output(['grep', STATION_KEY, STATIONS_DB]).split()[2]
DATA_FILE = os.path.join(ROOT_DIR, 'data', STATION_ID + '.full')
MAW_LEN = 5 # moving average window length

def f2c(t):
    """
    fahrenheit to celsius
    """
    return (t - 32) / 1.8

def replace_nan_with_mean(arr):
    """
    replace NaN with mean of not-NaN
    """
    arr_mean = np.mean(arr[np.argwhere(~np.isnan(arr))])
    arr_nonan = np.array(arr, copy=True)
    arr_nonan[np.argwhere(np.isnan(arr_nonan))] = arr_mean
    return arr_nonan

def replace_nan_with_nearest(arr):
    """
    replace NaN with nearest not-NaN
    """
    arr_clean = np.array(arr, copy=True)
    nan_positions = np.argwhere(np.isnan(arr))
    nonan_positions = np.argwhere(~np.isnan(arr))
    for nan_pos in nan_positions:
        nearest = np.abs(nonan_positions - nan_pos).argmin()
        arr_clean[nan_pos] = arr[nonan_positions[nearest]]
    return arr_clean

def replace_nan(arr):
    return replace_nan_with_nearest(arr)

def valid_elements(arr):
    """
    9999.99 means temperature not available
    """
    return arr[arr != 9999.9]

def plot_season_avg(years, period, station_name, xticks, avg_mins, avg_maxs,
                mavg_mins, mavg_maxs):
    title = 'Average of min/max temperature-values over ' + \
            r'$\bf{' + period + '}$' + ' for every year (' + \
            r'$\bf{' + station_name + '}$' + ')'
    xwidth = 0.3
    # plot bars and moving-avg
    plt.figure()
    plt.bar(years, avg_mins, xwidth, color='blue',
            label='avg of min')
    plt.bar([y + xwidth for y in years], avg_maxs, xwidth, color='red',
            label='avg of max')
    plt.plot(years, mavg_mins, color='deepskyblue',
             label='moving-avg of min')
    plt.plot([y + xwidth for y in years], mavg_maxs, color='magenta',
             label='moving-avg of max')
    # setup x/y axis, title and labels
    abs_min = math.floor(np.nanmin(avg_mins) - 1)
    abs_max = math.ceil(np.nanmax(avg_maxs) + 1)
    plt.xticks([y + xwidth/2 for y in years], xticks, rotation=90)
    plt.xlabel('Year')
    plt.ylim(bottom=abs_min)
    plt.yticks(np.arange(abs_min, abs_max, 1.0))
    plt.ylabel('Temperature ($^\circ$C)')
    plt.title(title)
    plt.legend()
    plt.grid()
    # color background around mean
    avg_avg_max = np.nanmean(avg_maxs)
    plt.axhspan(avg_avg_max, avg_avg_max + 2, facecolor='orange', alpha=0.2)
    plt.axhspan(avg_avg_max - 2 , avg_avg_max, facecolor='yellow', alpha=0.2)
    avg_avg_min = np.nanmean(avg_mins)
    plt.axhspan(avg_avg_min, avg_avg_min + 2, facecolor='green', alpha=0.2)
    plt.axhspan(avg_avg_min - 2 , avg_avg_min, facecolor='blue', alpha=0.2)
    # show
    plt.show()

def plot_season_swing(years, period, station_name, xticks, avg_mins, avg_maxs,
                mavg_mins, mavg_maxs):
    title = 'Daily variability of min/max temperature-values over ' + \
            r'$\bf{' + period + '}$' + ' for every year (' + \
            r'$\bf{' + station_name + '}$' + ')'
    xwidth = 0.3
    # plot bars and moving-avg
    plt.figure()
    plt.bar(years, avg_mins, xwidth, color='blue',
            label='variability-index of min')
    plt.bar([y + xwidth for y in years], avg_maxs, xwidth, color='red',
            label='variability-index of max')
    plt.plot(years, mavg_mins, color='deepskyblue',
             label='moving-avg of min variability')
    plt.plot([y + xwidth for y in years], mavg_maxs, color='magenta',
             label='moving-avg of max variability')
    # setup x/y axis, title and labels
    abs_min = 0
    abs_max = np.nanmax([np.nanmax(avg_mins), np.nanmax(avg_maxs)]) + 0.01
    plt.xticks([y + xwidth/2 for y in years], xticks, rotation=90)
    plt.xlabel('Year')
    plt.ylim(bottom=abs_min)
    plt.yticks(np.arange(abs_min, abs_max, 0.01))
    plt.ylabel('Variability index (spectral centroid)')
    plt.title(title)
    plt.legend()
    plt.grid()
    # show
    plt.show()

def swing(temps):
    days = len(temps)
    if days == 0:
        return np.nan
    spectrum = np.abs(np.fft.rfft(temps))
    freq = np.fft.rfftfreq(days)
    return np.average(freq, weights=spectrum)

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
    spring_pref = {}
    summer_pref = {}
    autumn_pref = {}
    winter_pref = {}
    for year in years:
        year_s = str(year)
        nyear_s = str(year + 1)
        all_dates = df['YEARMODA'].values
        # spring
        if year_s + '0301' in all_dates and \
           year_s + '0531' in all_dates:
            spring_pref[year] = (year_s + '03', year_s + '04', year_s + '05')
        else:
            spring_pref[year] = 'xxxxxxxx'
        # summer
        if year_s + '0601' in all_dates and \
           year_s + '0831' in all_dates:
            summer_pref[year] = (year_s + '06', year_s + '07', year_s + '08')
        else:
            summer_pref[year] = 'xxxxxxxx'
        # autumn
        if year_s + '0901' in all_dates and \
           year_s + '1130' in all_dates:
            autumn_pref[year] = (year_s + '09', year_s + '10', year_s + '11')
        else:
            autumn_pref[year] = 'xxxxxxxx'
        # winter
        if year_s + '1201' in all_dates and \
           nyear_s + '0228' in all_dates:
            winter_pref[year] = (year_s + '12', nyear_s + '01', nyear_s + '02')
        else:
            winter_pref[year] = 'xxxxxxxx'

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
