
import pandas as pd
import numpy as np
import TOU_pricing

# Parameters
inverter_controller_cost = 500. # ballpark
storage_cost_perkWh = 200./1.2 # cost per kilowatt-hour based on link above
storage_size_kWh = 4.*1.5  # storage size in kilowatt-hours, starting point 6 hours at 1.5 kW
P_max_charge = 12 * 20 / 1000. # maximum charge rate 12 V * 20 A = .24 kW
E_min_depth = .3
E_min = E_min_depth * storage_size_kWh

initial_investment = inverter_controller_cost + storage_cost_perkWh * storage_size_kWh

def peak_battery_only(results, i):

    results['storage_send'][i] = results['USAGE'][i]
    results['storage_available'][i+1] = results['storage_available'][i] - results['USAGE'][i]
    results['grid_store'][i] = 0 # only purchased during off-peak
    results['grid_demand_peak'][i] = 0
    results['grid_demand_offpeak'][i] = 0
    results['purchase_offpeak'][i] = 0
    results['purchase_peak'][i] = 0

    return results

def peak_battery_and_grid(results, i):

    results['grid_demand_peak'][i] = results['USAGE'][i] - results['storage_available'][i] + E_min
    results['storage_available'][i+1] = E_min
    results['storage_send'][i] = results['storage_available'][i] - E_min
    results['grid_store'][i] = 0 # only purchased during off-peak
    results['grid_demand_offpeak'][i] = 0
    results['purchase_offpeak'][i] = 0
    results['purchase_peak'][i] = results['grid_demand_peak'][i]

    return results

def offpeak_store_to_cap(results, i):

    results['grid_demand_offpeak'][i] = results['USAGE'][i]
    results['grid_store'][i] = storage_size_kWh - results['storage_available'][i]
    results['storage_available'][i+1] =  storage_size_kWh
    results['storage_send'][i] = 0
    results['grid_demand_peak'][i] = 0
    results['purchase_offpeak'][i] = results['grid_demand_offpeak'][i] + results['grid_store'][i]
    results['purchase_peak'][i] = 0

    return results

def offpeak_store_partial(results, i):

    results['grid_demand_offpeak'][i] = results['USAGE'][i]
    results['grid_store'][i] = P_max_charge
    results['storage_available'][i+1] =  results['storage_available'][i] + P_max_charge
    results['storage_send'][i] = 0
    results['grid_demand_peak'][i] = 0
    results['purchase_offpeak'][i] = results['grid_demand_offpeak'][i] + results['grid_store'][i]
    results['purchase_peak'][i] = 0

    return results

def offpeak_battery_full(results, i):

    results['grid_demand_offpeak'][i] = results['USAGE'][i]
    results['grid_store'][i] = 0
    results['storage_available'][i+1] = storage_size_kWh
    results['storage_send'][i] = 0
    results['grid_demand_peak'][i] = 0
    results['purchase_offpeak'][i] = results['grid_demand_offpeak'][i]
    results['purchase_peak'][i] = 0

    return results

def energy_logic(demand_costs):

    results = demand_costs
    results['storage_available'] = np.zeros_like(results['USAGE'])
    results['storage_send'] = np.zeros_like(results['USAGE'])
    results['grid_store'] = np.zeros_like(results['USAGE'])
    results['purchase_peak'] = np.zeros_like(results['USAGE'])
    results['purchase_offpeak'] = np.zeros_like(results['USAGE'])
    results['grid_demand_peak'] = np.zeros_like(results['USAGE'])
    results['grid_demand_offpeak'] = np.zeros_like(results['USAGE'])

    results['storage_available'][0] = storage_size_kWh

    for i in range(0,len(results['USAGE'])):

        # If at the end of the time series, break out
        if i == len(results['USAGE'])-1:
            break

        # Peak hours operation
        elif results['period'][i] == 'peak' or results['period'][i] == 'int':

            # If there is enough available in the battery, use it first
            if (results['storage_available'][i] - E_min) >= results['USAGE'][i]:

                results = peak_battery_only(results, i)

            # Otherwise, use up remainder in battery and then buy from grid
            else:
                results = peak_battery_and_grid(results, i)

        # Off-peak hours operation
        else:

            # If the battery isn't full...
            if results['storage_available'][i] < storage_size_kWh:

                # ... top off the battery if it is nearly full...
                if storage_size_kWh - results['storage_available'][i] <= P_max_charge:

                    results = offpeak_store_to_cap(results, i)

                # ... otherwise, charge as much as possible in one hour.
                else:

                    results = offpeak_store_partial(results, i)

            # If the battery is full, then it isn't necessary to purchase extra.
            else:

                results = offpeak_battery_full(results, i)

    results.to_csv('results.csv')

    return results


def main():

    results = energy_logic(TOU_pricing.main('EV', False))

    return results

if __name__ == "__main__":

    main()

