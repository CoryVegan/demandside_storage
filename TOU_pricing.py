"""
import_funcs.py class has two functions - weather() and BGEdata()


weather() aggregates and returns a Pandas dataframe with hourly weather readings. The csv files
are hourly weather observations from weatherunderground.com using 'weather_download_observations.py'
Add additional csv's using weather.append.
params: none
returns: 'weather' - Pandas dataframe, hourly weather data

BGEdata() aggregates and returns a Pandas dataframe with hourly electricity usage from BGE.com.
params: none
returns: 'DF' - Pandas dataframe, hourly electricity usage


Justin Elszasz 2014.04.10
"""



import pandas as pd
import numpy as np

summer_months = [6,7,8,9]

# BGE Prices

BGE_R_summer = .08975
BGE_R_nonsummer = .08616

BGE_RL_summer_peak = .11395
BGE_RL_summer_offpeak = .07419
BGE_RL_summer_int = .07783
BGE_RL_nonsummer_peak = .11924
BGE_RL_nonsummer_offpeak = .06974
BGE_RL_nonsummer_int = .08468

BGE_EV_summer_peak = .15656
BGE_EV_summer_offpeak = .05556
BGE_EV_nonsummer_peak = .18266
BGE_EV_nonsummer_offpeak = .05209


# BGE RL Plan

BGE_RL_summer_peak_starttime = '10:00' 
BGE_RL_summer_peak_endtime = '19:00'

BGE_RL_summer_int1_starttime = '07:00'
BGE_RL_summer_int1_endtime = '09:00'
BGE_RL_summer_int2_starttime = '20:00'
BGE_RL_summer_int2_endtime = '22:00'

BGE_RL_nonsummer_peak1_starttime = '07:00'
BGE_RL_nonsummer_peak1_endtime = '10:00'
BGE_RL_nonsummer_peak2_starttime = '17:00'
BGE_RL_nonsummer_peak2_endtime = '20:00'

BGE_RL_nonsummer_int_starttime = '11:00' 
BGE_RL_nonsummer_int_endtime = '16:00'

# BGE EV Plan

BGE_EV_summer_peak_starttime = '10:00'
BGE_EV_summer_peak_endtime = '19:00'

BGE_EV_nonsummer_peak1_starttime = '07:00'
BGE_EV_nonsummer_peak1_endtime = '10:00'
BGE_EV_nonsummer_peak2_starttime = '17:00'
BGE_EV_nonsummer_peak2_endtime = '20:00'


#def period(df):


def BGE_elec_cost(df):

    df['BGE-R_cost_perkWh'] = np.zeros(len(df['USAGE'])) # price per kWh
    df['BGE-RL_cost_perkWh'] = np.zeros(len(df['USAGE'])) # price per kWh
	
    df['BGE-EV_cost_perkWh'] = np.zeros(len(df['USAGE'])) # price per kWh

    #df['BGE-R'] = np.zeros(len(df['USAGE'])) # price per kWh
    #df['BGE-RL'] = np.zeros(len(df['USAGE'])) # price per kWh
    #df['BGE-EV'] = np.zeros(len(df['USAGE'])) # price per kWh

	# BGE R Plan
    #df['BGE-R_cost_perkWh'][df['BGE-R'] == 'offpeak'] = BGE_R_nonsummer
    #df['BGE-R_cost_perkWh'][df['BGE-R'] == 'peak'] = BGE_R_summer
	
    df['BGE-R_cost_perkWh'] = BGE_R_nonsummer
    df['BGE-R_cost_perkWh'].ix[(df[np.in1d(df.index.month,summer_months)]).index] = BGE_R_summer

	# BGE RL Plan

	# Non-summer Off-Peak
    df['BGE-RL_cost_perkWh'] = BGE_RL_nonsummer_offpeak
    # Non-summer On-Peak
    df['BGE-RL_cost_perkWh'].ix[(df[df.index.weekday<5].between_time(BGE_RL_nonsummer_peak1_starttime,BGE_RL_nonsummer_peak1_endtime)).index] = BGE_RL_nonsummer_peak
    df['BGE-RL_cost_perkWh'].ix[(df[df.index.weekday<5].between_time(BGE_RL_nonsummer_peak2_starttime,BGE_RL_nonsummer_peak2_endtime)).index] = BGE_RL_nonsummer_peak
    # # Non-summer Intermediate
    df['BGE-RL_cost_perkWh'].ix[(df[df.index.weekday<5].between_time(BGE_RL_nonsummer_int_starttime,BGE_RL_nonsummer_int_endtime)).index] = BGE_RL_nonsummer_int

    # Summer Off-Peak
    df['BGE-RL_cost_perkWh'][(df[np.in1d(df.index.month,summer_months)]).index] = BGE_RL_summer_offpeak
    # Summer On-Peak
    df['BGE-RL_cost_perkWh'].ix[(df[(df.index.weekday<5) & (np.in1d(df.index.month,summer_months))].between_time(BGE_RL_summer_peak_starttime,BGE_RL_summer_peak_endtime)).index] = BGE_RL_summer_peak
    # Summer Intermediate
    df['BGE-RL_cost_perkWh'].ix[(df[(df.index.weekday<5) & (np.in1d(df.index.month,summer_months))].between_time(BGE_RL_summer_int1_starttime,BGE_RL_summer_int1_endtime)).index] = BGE_RL_summer_int
    df['BGE-RL_cost_perkWh'].ix[(df[(df.index.weekday<5) & (np.in1d(df.index.month,summer_months))].between_time(BGE_RL_summer_int2_starttime,BGE_RL_summer_int2_endtime)).index] = BGE_RL_summer_int

    # BGE EV Plan

    # Non-summer Off-Peak
    df['BGE-EV_cost_perkWh'] = BGE_EV_nonsummer_offpeak
    # Non-summer On-Peak
    df['BGE-EV_cost_perkWh'].ix[(df[df.index.weekday<5].between_time(BGE_EV_nonsummer_peak1_starttime,BGE_EV_nonsummer_peak1_endtime)).index] = BGE_EV_nonsummer_peak
    df['BGE-EV_cost_perkWh'].ix[(df[df.index.weekday<5].between_time(BGE_EV_nonsummer_peak2_starttime,BGE_EV_nonsummer_peak2_endtime)).index] = BGE_EV_nonsummer_peak
    
    # Summer Off-Peak
    df['BGE-EV_cost_perkWh'].ix[(df[np.in1d(df.index.month,summer_months)]).index] = BGE_EV_summer_offpeak
    # Summer On-Peak
    df['BGE-EV_cost_perkWh'].ix[(df[(df.index.weekday<5) & (np.in1d(df.index.month,summer_months))].between_time(BGE_EV_summer_peak_starttime,BGE_EV_summer_peak_endtime)).index] = BGE_EV_summer_peak

    return df

