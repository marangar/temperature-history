from __future__ import absolute_import
from __future__ import print_function
import numpy as np

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

def date_prefixes(df, years):
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
    return spring_pref, summer_pref, autumn_pref, winter_pref
