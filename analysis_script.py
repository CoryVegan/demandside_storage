#import system_param
import TOU_pricing
import storage_logic
import pandas as pd
import numpy as np
import time

reload(storage_logic)


def calc_annual_var_cost(results):

    cost_peak = results['cost'] * results['grid_to_demand_peak']
    cost_offpeak = results['cost'] * (results['grid_to_demand_offpeak'] + results['grid_to_inverter'])
    annual_var_cost = round(cost_peak.sum() + cost_offpeak.sum(),2)
    return annual_var_cost

def calc_PBP(results, system_param):

    results_R = storage_logic.main(TOU_pricing.main('R', False), system_param)
    R_annual_cost = calc_annual_var_cost(results_R)

    PBP = (system_param['Inverter Cost'] + system_param['Storage Cost'] * system_param['Storage Size']) / (R_annual_cost - calc_annual_var_cost(results))

    return PBP

def calc_metrics(results, system_param):

    total_kWh_purchased = results['grid_to_demand_peak'].sum() + results['grid_to_demand_offpeak'].sum() + results['grid_to_inverter'].sum()
    total_peak_demand = results['USAGE'][results['period']=='peak'].sum()

    metrics = {

        'Total kWh Purchased' : total_kWh_purchased,
        '% Purchased During Peak' : results['grid_to_demand_peak'].sum() / total_kWh_purchased,
        '% Purchased During Off-Peak' : (results['grid_to_demand_offpeak'].sum() + results['grid_to_inverter'].sum()) / total_kWh_purchased,
        'Hours on Battery Only' : results['USAGE'][results['storage_to_inverter']>0][results['grid_to_demand_peak']==0].count(),
        '% Peak Demand Battery' : results['USAGE'][results['storage_to_inverter']>0].sum() / total_peak_demand,
        'Hours Battery Full' : results['USAGE'][results['storage_available']==results['storage_available'].max()].count(),
        'Hours Battery Depleted' : results['USAGE'][results['storage_available']==results['storage_available'].min()].count(),
        'Annual System Eff' : results['USAGE'].sum() / total_kWh_purchased,
        'Annual Var Cost' : calc_annual_var_cost(results),
        'Initial Cost' : system_param['Inverter Cost'] + system_param['Storage Cost'] * system_param['Storage Size'],
        'Peak kWh Shaved' : results['USAGE'][results['period']=='peak'].sum() - results['grid_to_demand_peak'].sum(),
        '% Peak kWh Shaved' : (results['USAGE'][results['period']=='peak'].sum() - results['grid_to_demand_peak'].sum()) / results['USAGE'][results['period']=='peak'].sum(),
        'PBP' : calc_PBP(results, system_param)
        #### ADD PBP HERE ####

        #'% Demand Served by Battery' : results['USAGE'][results['storage_to_inverter']>0].sum() / results['USAGE'].sum(), # not sure this is useful
    }

    return metrics

def storage_size():

    t0 = time.time()

    def inverter_efficiency(direction):
        if direction == 'charging':
            eff = .85
        elif direction == 'discharging':
            eff = .85
        return eff

    def battery_efficiency(direction):
        if direction == 'charging':
            eff = .85
        elif direction == 'discharging':
            eff = .85
        return eff

    battery_sizes = [1., 2., 5., 7.5, 10., 15., 20., 25., 30.]
    max_dod = .2

    for i, bat_size in enumerate(battery_sizes):

        system_param = {
            'Inverter Cost' : 1500., # ballpark
            'Storage Cost' : 200. / 1.2, # cost per kilowatt-hour based on link above
            'Storage Size' : bat_size,  # storage size in kilowatt-hours
            'Max Charge Rate' : bat_size / 8.,
            'Max DOD' : max_dod, # DOD
            'Bat Depleted' : max_dod * battery_sizes[i],
            'Inverter Efficiency' : inverter_efficiency,
            'Battery Efficiency' : battery_efficiency,
        }

        metrics = calc_metrics(storage_logic.main(TOU_pricing.main('EV',False), system_param), system_param)

        if i == 0: all_metrics = pd.DataFrame(index=battery_sizes, columns=metrics.keys()) 
            
        all_metrics['Total kWh Purchased'][bat_size] = metrics['Total kWh Purchased']
        all_metrics['% Purchased During Peak'][bat_size] = metrics['% Purchased During Peak']
        all_metrics['% Purchased During Off-Peak'][bat_size] =  metrics['% Purchased During Off-Peak']
        all_metrics['Hours on Battery Only'][bat_size] = metrics['Hours on Battery Only']
        all_metrics['% Peak Demand Battery'][bat_size] = metrics['% Peak Demand Battery']
        all_metrics['Hours Battery Full'][bat_size] = metrics['Hours Battery Full']
        all_metrics['Hours Battery Depleted'][bat_size] = metrics['Hours Battery Depleted']
        all_metrics['Annual System Eff'][bat_size] = metrics['Annual System Eff']
        all_metrics['Annual Var Cost'][bat_size] = metrics['Annual Var Cost']
        all_metrics['Initial Cost'][bat_size] = metrics['Initial Cost']
        all_metrics['Peak kWh Shaved'][bat_size] = metrics['Peak kWh Shaved']
        all_metrics['% Peak kWh Shaved'][bat_size] = metrics['% Peak kWh Shaved']
        all_metrics['PBP'][bat_size] = metrics['PBP']

    t1 = time.time()

    print 'Time for model run:',round(t1-t0,1),'s'

    all_metrics.to_csv('all_metrics_storage.csv')    
    return all_metrics

def batt_eff():

    bat_effs = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

    for i, bat_eff in enumerate(battery_sizes):

        def inverter_efficiency(direction):
            if direction == 'charging':
                eff = .85
            elif direction == 'discharging':
                eff = .85
            return eff

        def battery_efficiency(direction):
            if direction == 'charging':
                eff = bat_effs[i]
            elif direction == 'discharging':
                eff = bat_effs[i]
            return eff

        bat_size = 5.
        max_dod = .2

        system_param = {
            'Inverter Cost' : 1500., # ballpark
            'Storage Cost' : 200. / 1.2, # cost per kilowatt-hour based on link above
            'Storage Size' : bat_size,  # storage size in kilowatt-hours
            'Max Charge Rate' : bat_size / 8.,
            'Max DOD' : max_dod, # DOD
            'Bat Depleted' : max_dod * battery_sizes[i],
            'Inverter Efficiency' : inverter_efficiency,
            'Battery Efficiency' : battery_efficiency,
        }

        metrics = calc_metrics(storage_logic.main(TOU_pricing.main('EV',False), system_param), system_param)

        if i == 0: all_metrics = pd.DataFrame(index=bat_effs, columns=metrics.keys()) 
            
        all_metrics['Total kWh Purchased'][bat_eff] = metrics['Total kWh Purchased']
        all_metrics['% Purchased During Peak'][bat_eff] = metrics['% Purchased During Peak']
        all_metrics['% Purchased During Off-Peak'][bat_eff] =  metrics['% Purchased During Off-Peak']
        all_metrics['Hours on Battery Only'][bat_eff] = metrics['Hours on Battery Only']
        all_metrics['% Peak Demand Battery'][bat_eff] = metrics['% Peak Demand Battery']
        all_metrics['Hours Battery Full'][bat_eff] = metrics['Hours Battery Full']
        all_metrics['Hours Battery Depleted'][bat_eff] = metrics['Hours Battery Depleted']
        all_metrics['Annual System Eff'][bat_eff] = metrics['Annual System Eff']
        all_metrics['Annual Var Cost'][bat_eff] = metrics['Annual Var Cost']
        all_metrics['Initial Cost'][bat_eff] = metrics['Initial Cost']
        all_metrics['Peak kWh Shaved'][bat_eff] = metrics['Peak kWh Shaved']
        all_metrics['% Peak kWh Shaved'][bat_eff] = metrics['% Peak kWh Shaved']
        all_metrics['PBP'][bat_eff] = metrics['PBP']

    all_metrics.to_csv('all_metrics_battery_efficiency.csv')    
    return all_metrics
