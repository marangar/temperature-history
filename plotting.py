from __future__ import absolute_import
import numpy as np
import matplotlib.pyplot as plt
import math

def plot_season_avg(years, period, station_name, xticks, avg_mins, avg_maxs,
                    mavg_mins, mavg_maxs, out_svg_file=None):
    title = 'Average of min/max temperature-values over ' + \
            r'$\bf{' + period + '}$' + ' for every year (' + \
            r'$\bf{' + station_name + '}$' + ')'
    xwidth = 0.3
    # plot bars and moving-avg
    plt.figure(figsize=(11,6))
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
    plt.ylabel('Temperature ($^\circ$C)') #pylint: disable=anomalous-backslash-in-string
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
    if not out_svg_file:
        plt.show()
    else:
        plt.savefig(out_svg_file, format="svg", bbox_inches='tight')

def plot_season_swing(years, period, station_name, xticks, swng_mins, swng_maxs,
                      mavg_mins, mavg_maxs, out_svg_file=None, nr_days=1):
    title = r'${' + str(nr_days) + '}$-day variability of min/max temperature-values over ' + \
            r'$\bf{' + period + '}$' + ' for every year (' + \
            r'$\bf{' + station_name + '}$' + ')'
    xwidth = 0.3
    # plot bars and moving-avg
    plt.figure(figsize=(11,6))
    plt.bar(years, swng_mins, xwidth, color='blue',
            label='variability-index of min temps')
    plt.bar([y + xwidth for y in years], swng_maxs, xwidth, color='red',
            label='variability-index of max temps')
    plt.plot(years, mavg_mins, color='deepskyblue',
             label='moving-avg of min-temps variability')
    plt.plot([y + xwidth for y in years], mavg_maxs, color='magenta',
             label='moving-avg of max-temps variability')
    # setup x/y axis, title and labels
    abs_min = 0
    abs_max = np.nanmax([np.nanmax(swng_mins), np.nanmax(swng_maxs)]) + 0.01
    plt.xticks([y + xwidth/2 for y in years], xticks, rotation=90)
    plt.xlabel('Year')
    plt.ylim(bottom=abs_min)
    plt.yticks(np.arange(abs_min, abs_max, 0.01))
    plt.ylabel('Variability index (spectral centroid)')
    plt.title(title)
    plt.legend()
    plt.grid()
    # show
    if not out_svg_file:
        plt.show()
    else:
        plt.savefig(out_svg_file, format="svg", bbox_inches='tight')
