from __future__ import absolute_import
import pandas

def get_data_frame(data_file):
    df = pandas.read_csv(filepath_or_buffer=data_file,
                         delim_whitespace=True, header=None,
                         names=['STN---', 'WBAN', 'YEARMODA', 'TEMP',
                                'TEMP_CNT', 'DEWP', 'DWEP_CNT', 'SLP',
                                'SLP_CNT', 'STP', 'STP_CNT', 'VISIB',
                                'VISIB_CNT', 'WDSP', 'WDSP_CNT', 'MXSPD',
                                'GUST', 'MAX', 'MIN', 'PRCP', 'SNDP', 'FRSHTT'])
    return df

def get_t_min_max(df, years, season_pref):
    match_criterion = df['YEARMODA'].str.startswith
    tmins = [df.loc[match_criterion(season_pref[y])]['MIN'] for y in years]
    tmaxs = [df.loc[match_criterion(season_pref[y])]['MAX'] for y in years]
    return tmins, tmaxs

def get_years(df):
    start_year = int(df['YEARMODA'].values[1][:4])
    end_year = int(df['YEARMODA'].values[-1][:4])
    return start_year, end_year
