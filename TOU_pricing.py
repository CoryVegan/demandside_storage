"""
Imports hourly Green Button sample data and determines season, BGE time-of-use period, 
and cost of electricity at each hour.

Justin Elszasz 2014.09.12
"""

import pandas as pd
import numpy as np

def import_demand():
    """
    Reads in an Green Button sample file in xml format and returns Pandas dataframe.
    
    Returns: 
        demand_data: Timestamped Pandas dataframe containing hourly electricity usage 
            from Green Button sample file
    """

    from bs4 import BeautifulSoup as bs

    xml_file = 'raw_data/Inland_Single_Family_Jan_1_2011_to_Jan_1_2012_RetailCustomer_9.xml'
    soup = bs(open(xml_file))

    # initiate a numpy array to store values
    data_array = np.zeros((len(soup.find_all('value')),1))

    # In the Green Button schema, the IntervalReading tag designates each reading
    # Each IntervalReading has a 'time' element with start and duration children
    # 'Value' element is actual hourly usage in Watt-hours  

    for i, intervalreading in enumerate(soup.find_all('intervalreading')):
        data_array[i,0]=intervalreading.value.get_text()

    # Convert the array into a Pandas DataFrame for ease of time series use

    data_start = '1/1/2011 08:00:00'
    demand_data = pd.DataFrame(data_array*.001,columns=['USAGE'],index=pd.date_range(data_start, periods=len(soup.find_all('value')), freq='H'))

    #demand_data.to_csv('raw_data/Green_Button_Sample_Inland_SingleFamily.csv')

    return demand_data

def TOU_period(df, plan):

    """
    Determines the period (peak, off-peak, or intermediate) for each hour
    
    Args:
        df: Pandas dataframe containing timestamped data
        plan: string must be 'R' (normal residential BGE plan), 'RL' (BGE TOU plan), 
            or 'EV' (electric vehicle TOU plan)

    Returns:
        df: Pandas dataframe with periods assigned
    """

    summer_months = [6,7,8,9]
    df['season']= np.zeros_like(df['USAGE'])
    df['season'] = 'non_summer'
    df['season'].ix[(df[np.in1d(df.index.month,summer_months)]).index] = 'summer'

    if  plan == 'R':
        df['period'] = np.zeros_like(df['USAGE'])
        df['period'] = 'offpeak'
        return df

    if plan == 'RL':

        # BGE RL Plan
        RL_summer_peak_starttime = '10:00'
        RL_summer_peak_endtime = '19:00'
        RL_summer_int1_starttime = '07:00'
        RL_summer_int1_endtime = '09:00'
        RL_summer_int2_starttime = '20:00'
        RL_summer_int2_endtime = '22:00'
        RL_nonsummer_peak1_starttime = '07:00'
        RL_nonsummer_peak1_endtime = '10:00'
        RL_nonsummer_peak2_starttime = '17:00'
        RL_nonsummer_peak2_endtime = '20:00'
        RL_nonsummer_int_starttime = '11:00'
        RL_nonsummer_int_endtime = '16:00'

        df['period'] = np.zeros_like(df['USAGE'])

        # BGE RL Plan
        df['period'] = 'offpeak'
        # Non-summer
        df['period'].ix[(df[df.index.weekday<5][df['season']=='non_summer'].between_time(RL_nonsummer_peak1_starttime, RL_nonsummer_peak1_endtime)).index] = 'peak'
        df['period'].ix[(df[df.index.weekday<5][df['season']=='non_summer'].between_time(RL_nonsummer_peak2_starttime, RL_nonsummer_peak2_endtime)).index] = 'peak'
        df['period'].ix[(df[df.index.weekday<5][df['season']=='non_summer'].between_time(RL_nonsummer_int_starttime, RL_nonsummer_int_endtime)).index] = 'int'
        # Summer
        df['period'].ix[(df[df.index.weekday<5][df['season']=='summer'].between_time(RL_summer_peak_starttime, RL_summer_peak_endtime)).index] = 'peak'
        df['period'].ix[(df[df.index.weekday<5][df['season']=='summer'].between_time(RL_summer_int1_starttime, RL_summer_int1_endtime)).index] = 'int'
        df['period'].ix[(df[df.index.weekday<5][df['season']=='summer'].between_time(RL_summer_int2_starttime, RL_summer_int2_endtime)).index] = 'int'

        return df

    if plan == 'EV':

        # BGE EV Plan
        EV_summer_peak_starttime = '10:00'
        EV_summer_peak_endtime = '19:00'
        EV_nonsummer_peak1_starttime = '07:00'
        EV_nonsummer_peak1_endtime = '10:00'
        EV_nonsummer_peak2_starttime = '17:00'
        EV_nonsummer_peak2_endtime = '20:00'

        df['period'] = np.zeros_like(df['USAGE'])

        # BGE R Plan (no peak/off-peak, calling everything "offpeak")

        # BGE EV Plan
        df['period'] = 'offpeak'
        # Non-summer
        df['period'].ix[(df[df.index.weekday<5][df['season']=='non_summer'].between_time(EV_nonsummer_peak1_starttime, EV_nonsummer_peak1_endtime)).index] = 'peak'
        df['period'].ix[(df[df.index.weekday<5][df['season']=='non_summer'].between_time(EV_nonsummer_peak2_starttime, EV_nonsummer_peak2_endtime)).index] = 'peak'
        # Summer
        df['period'].ix[(df[df.index.weekday<5][df['season']=='summer'].between_time(EV_summer_peak_starttime, EV_summer_peak_endtime)).index] = 'peak'

        return df

def elec_cost(df, plan):

    """
    This function returns the costs of electricity for the BGE plans based on the season (summer/non-summer) and
    time period (peak, off-peak, intermediate).

    :param df: Pandas dataframe containing output from TOU_period(df)
    :return: df: Pandas dataframe containing cost of electricity at every hour for each of three TOU pricing schemes

    """

    if plan == 'R':

        R_summer = .08975
        R_nonsummer = .08616

        df['cost'] = np.zeros_like(df['USAGE'])

        df['cost'][df['season']=='non_summer'] = R_nonsummer
        df['cost'][df['season']=='summer'] = R_summer

        return df

    if plan == 'RL':

        RL_summer_peak = .11395
        RL_summer_offpeak = .07419
        RL_summer_int = .07783
        RL_nonsummer_peak = .11924
        RL_nonsummer_offpeak = .06974
        RL_nonsummer_int = .08468

        df['cost'] = np.zeros_like(df['USAGE'])

        df['cost'].ix[(df[df['season']=='non_summer'][df['period']=='offpeak']).index] = RL_nonsummer_offpeak
        df['cost'].ix[(df[df['season']=='non_summer'][df['period']=='peak']).index] = RL_nonsummer_peak
        df['cost'].ix[(df[df['season']=='non_summer'][df['period']=='int']).index] = RL_nonsummer_int
        df['cost'].ix[(df[df['season']=='summer'][df['period']=='offpeak']).index] = RL_summer_offpeak
        df['cost'].ix[(df[df['season']=='summer'][df['period']=='peak']).index] = RL_summer_peak
        df['cost'].ix[(df[df['season']=='summer'][df['period']=='int']).index] = RL_summer_int

        return df

    if plan == 'EV':

        EV_summer_peak = .15656
        EV_summer_offpeak = .05556
        EV_nonsummer_peak = .18266
        EV_nonsummer_offpeak = .05209

        df['cost'] = np.zeros_like(df['USAGE'])

        df['cost'].ix[(df[df['season']=='non_summer'][df['period']=='offpeak']).index] = EV_nonsummer_offpeak
        df['cost'].ix[(df[df['season']=='non_summer'][df['period']=='peak']).index] = EV_nonsummer_peak
        df['cost'].ix[(df[df['season']=='summer'][df['period']=='offpeak']).index] = EV_summer_offpeak
        df['cost'].ix[(df[df['season']=='summer'][df['period']=='peak']).index] = EV_summer_peak

        return df

def plot_all_costs(all_plan_costs):

    """
    Generate a plot showing the different BGE TOU pricing schemes.

    :param demand_cost: Timestamped data from 2011 containing the output from elec_cost(df)

    """

    import matplotlib.pyplot as plt

    #plan_cost = plan + '_cost'

    non_summer_wkday = '12-jan-2011'
    non_summer_wkend = '15-jan-2011'
    summer_wkday = '13-jul-2011'
    summer_wkend = '16-jul-2011'

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharey='row')

    ax1.plot(all_plan_costs.ix[non_summer_wkday].index,all_plan_costs['R_cost'].ix[non_summer_wkday])
    ax1.plot(all_plan_costs.ix[non_summer_wkday].index,all_plan_costs['RL_cost'].ix[non_summer_wkday])
    ax1.plot(all_plan_costs.ix[non_summer_wkday].index,all_plan_costs['EV_cost'].ix[non_summer_wkday])
    ax1.set_title('Non-Summer Weekday')

    ax2.plot(all_plan_costs.ix[summer_wkday].index,all_plan_costs['R_cost'].ix[summer_wkday])
    ax2.plot(all_plan_costs.ix[summer_wkday].index,all_plan_costs['RL_cost'].ix[summer_wkday])
    ax2.plot(all_plan_costs.ix[summer_wkday].index,all_plan_costs['EV_cost'].ix[summer_wkday])
    ax2.set_title('Summer Weekday')

    ax3.plot(all_plan_costs.ix[non_summer_wkend].index,all_plan_costs['R_cost'].ix[non_summer_wkend])
    ax3.plot(all_plan_costs.ix[non_summer_wkend].index,all_plan_costs['RL_cost'].ix[non_summer_wkend])
    ax3.plot(all_plan_costs.ix[non_summer_wkend].index,all_plan_costs['EV_cost'].ix[non_summer_wkend])
    ax3.set_title('Non-Summer Weekend')

    ax4.plot(all_plan_costs.ix[summer_wkend].index,all_plan_costs['R_cost'].ix[summer_wkend])
    ax4.plot(all_plan_costs.ix[summer_wkend].index,all_plan_costs['RL_cost'].ix[summer_wkend])
    ax4.plot(all_plan_costs.ix[summer_wkend].index,all_plan_costs['EV_cost'].ix[summer_wkend])
    ax4.set_title('Summer Weekend')

    ax4.legend(['R','RL','EV'], loc='upper right')

    fig.text(0.5, 1, 'BGE Electricity TOU Pricing Plans', ha='center', va='top', fontsize=16)
    fig.text(0.04, 0.5, 'Cost of Electricity ($/kWh)', ha='center', va='center', rotation='vertical', fontsize=16)

    plt.setp( ax1.xaxis.set_visible(False) )
    plt.setp( ax2.xaxis.set_visible(False) )
    plt.setp( ax3.xaxis.get_majorticklabels(), rotation=90 )
    plt.setp( ax4.xaxis.get_majorticklabels(), rotation=90 )

    plt.subplots_adjust(bottom=0.15)

    plt.show()

def main(plan, save):

    demand = import_demand()

    if plan == 'all':

        all_plan_costs = TOU_period(demand, 'R')
        all_plan_costs = elec_cost(all_plan_costs, 'R')
        all_plan_costs.rename(columns={'period': 'R_period', 'cost':'R_cost'}, inplace=True)

        all_plan_costs = TOU_period(all_plan_costs, 'RL')
        all_plan_costs = elec_cost(all_plan_costs, 'RL')
        all_plan_costs.rename(columns={'period': 'RL_period', 'cost':'RL_cost'}, inplace=True)

        all_plan_costs = TOU_period(all_plan_costs, 'EV')
        all_plan_costs = elec_cost(all_plan_costs, 'EV')
        all_plan_costs.rename(columns={'period': 'EV_period', 'cost':'EV_cost'}, inplace=True)        

        plot_all_costs(all_plan_costs)

        if save == True:

            all_plan_costs.to_csv('all_plan_costs.csv')

        return all_plan_costs


    else:

        demand_periods = TOU_period(demand, plan)
        demand_costs = elec_cost(demand_periods, plan)

        if save == True: demand_costs.to_csv(plan+'_demand_costs.csv')

        return demand_costs


if __name__ == "__main__":

    main()