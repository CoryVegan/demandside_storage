'''
The main() function below contains the actual logic.  Functions are called by the logic
to calculate the actual state for each hour. 


Justin Elszasz, 10/3/2014
Update 10/30/2014
'''

import numpy as np


def peak_battery_only(results, system_param, i):

    results['inverter_to_demand'][i] = results['USAGE'][i] / system_param['Inverter Efficiency']('discharging')
    results['storage_to_inverter'][i] = results['inverter_to_demand'][i] / system_param['Battery Efficiency']('discharging')
    results['storage_available'][i+1] = results['storage_available'][i] - results['storage_to_inverter'][i]
    results['inverter_to_storage'][i] = 0 # elec for storage only purchased during off-peak
    results['grid_to_inverter'][i] = 0 # elec for storage only purchased during off-peak
    results['grid_to_demand_peak'][i] = 0
    results['grid_to_demand_offpeak'][i] = 0

    return results

def peak_battery_and_grid(results, system_param, i):

    results['storage_to_inverter'][i] = (results['storage_available'][i] - system_param['Bat Depleted']) * system_param['Battery Efficiency']('discharging')
    results['inverter_to_demand'][i] = results['storage_to_inverter'][i] * system_param['Inverter Efficiency']('discharging')
    results['storage_available'][i+1] = system_param['Bat Depleted']
    results['grid_to_demand_peak'][i] = results['USAGE'][i] - results['inverter_to_demand'][i] # grid makes up the difference
    results['inverter_to_storage'][i] = 0
    results['grid_to_inverter'][i] = 0 # elec for storage only purchased during off-peak
    results['grid_to_demand_offpeak'][i] = 0

    return results

def offpeak_store_to_cap(results, system_param, i):

    results['grid_to_demand_offpeak'][i] = results['USAGE'][i]
    results['inverter_to_storage'][i] = (system_param['Storage Size'] - results['storage_available'][i]) / system_param['Battery Efficiency']('charging')
    results['grid_to_inverter'][i] =  results['inverter_to_storage'][i] / system_param['Inverter Efficiency']('charging')
    results['storage_available'][i+1] =  system_param['Storage Size']
    results['storage_to_inverter'][i] = 0 # not using elec from storage during off-peak
    results['inverter_to_demand'][i] = 0 # not using elec from storage during off-peak
    results['grid_to_demand_peak'][i] = 0

    return results

def offpeak_store_partial(results, system_param, i):

    results['grid_to_demand_offpeak'][i] = results['USAGE'][i]
    results['storage_available'][i+1] =  results['storage_available'][i] + system_param['Max Charge Rate']
    results['inverter_to_storage'][i] = system_param['Max Charge Rate'] / system_param['Battery Efficiency']('charging')
    results['grid_to_inverter'][i] = results['inverter_to_storage'][i] / system_param['Inverter Efficiency']('charging')
    results['storage_to_inverter'][i] = 0 # not using elec from storage during off-peak
    results['inverter_to_demand'][i] = 0 # not using elec from storage during off-peak
    results['grid_to_demand_peak'][i] = 0

    return results

def offpeak_battery_full(results, system_param, i):

    results['grid_to_demand_offpeak'][i] = results['USAGE'][i]
    results['grid_to_inverter'][i] = 0
    results['inverter_to_storage'][i] = 0
    results['storage_available'][i+1] = system_param['Storage Size']
    results['storage_to_inverter'][i] = 0 # not using elec from storage during off-peak
    results['inverter_to_demand'][i] = 0 # not using elec from storage during off-peak
    results['grid_to_demand_peak'][i] = 0

    return results

def main(demand_costs, system_param):
    '''
    Calculates all energy flows and battery state for each hour in a year.
    
    Args: 
        demand_costs: Pandas dataframe output from TOU_pricing.main() containing hourly time-of-use periods,
            seasons, and associated price of electricity
    
    Returns:
        results: Pandas dataframe with energy flows and battery state at each hour over course of year

    '''

    # initialize storage state and flows
    results = demand_costs
    results['storage_available'] = np.zeros_like(results['USAGE'])
    results['inverter_to_storage'] = np.zeros_like(results['USAGE'])
    results['storage_to_inverter'] = np.zeros_like(results['USAGE'])
    results['inverter_to_demand'] = np.zeros_like(results['USAGE'])
    results['grid_to_inverter'] = np.zeros_like(results['USAGE'])
    results['grid_to_demand_peak'] = np.zeros_like(results['USAGE'])
    results['grid_to_demand_offpeak'] = np.zeros_like(results['USAGE'])

    # battery starts fully charged at first time step
    results['storage_available'][0] = system_param['Storage Size']

    for i in range(0,len(results['USAGE'])):

        # If at the end of the time series, break out
        if i == len(results['USAGE'])-1:
            break

        # Peak hours operation
        elif results['period'][i] == 'peak' or results['period'][i] == 'int':

            # If there is enough available in the battery, use it first
            if (results['storage_available'][i] - system_param['Bat Depleted']) * system_param['Battery Efficiency']('discharging') * system_param['Inverter Efficiency']('discharging') >= results['USAGE'][i]:
                results = peak_battery_only(results, system_param, i)

            # Otherwise, use up remainder in battery and then buy from grid
            else:
                results = peak_battery_and_grid(results, system_param, i)

        # Off-peak hours operation
        else:

            # If the battery isn't full...
            if results['storage_available'][i] < system_param['Storage Size']:

                # ... top off the battery if it is nearly full...
                if system_param['Storage Size'] - results['storage_available'][i] <= system_param['Inverter Efficiency']('charging') * system_param['Max Charge Rate']:
                    results = offpeak_store_to_cap(results, system_param, i)

                # ... otherwise, charge as much as possible in one hour.
                else:
                    results = offpeak_store_partial(results, system_param, i)

            # If the battery is full, then it isn't necessary to purchase extra.
            else:
                results = offpeak_battery_full(results, system_param, i)

    #results.to_csv('results.csv')
    return results

if __name__ == "__main__":
    main()

