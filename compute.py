from __future__ import absolute_import
import numpy as np
from utils import f2c, valid_elements, replace_nan

def compute_season_value(compute_func, season_temps, **kwargs):
    return np.array([compute_func(f2c(valid_elements(temps)), **kwargs)
                     for temps in season_temps])

def moving_average(cmpt_values, maw_len):
    return smooth(replace_nan(cmpt_values), maw_len, 'flat')

def swing(temps, nr_days=1):
    """ compute swing (variability index) of input temperature array.
        variability index is calculated as the spectral centroid of the 'temps' array.
        temperatures are first averaged in groups of 'nr_days' days.
    """
    days = len(temps)
    if days == 0:
        return np.nan
    resh_temps = temps[: len(temps) // nr_days * nr_days].values
    resh_temps = np.mean(resh_temps.reshape((-1, nr_days)), axis=1)
    spectrum = np.abs(np.fft.rfft(resh_temps))
    freq = np.fft.rfftfreq(len(resh_temps))
    return np.average(freq, weights=spectrum)

def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)') #pylint: disable=eval-used

    y=np.convolve(w/w.sum(),s,mode='valid')
    left_off = int((window_len - 1) / 2)
    right_off = (window_len - 1) - left_off
    return y[left_off:-right_off]
