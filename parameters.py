'''
system_param.py

Setting some storage system parameters as shown below.

Inverter and battery efficiencies could be transformed into functions instead of constants

Justin Elszasz 10/2/2014

'''

def set_params():

    bat_size = 5. # kWh

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

    system_param = {
        'Inverter Cost' : 1500., # ballpark
        'Storage Cost' : 200. / 1.2, # cost per kilowatt-hour based on link above
        'Storage Size' : bat_size,  # storage size in kilowatt-hours
        'Max Charge Rate' : bat_size / 12.,
        'Max DOD' : .2, # DOD
        'Bat Depleted' : .2 * bat_size,
        'Inverter Efficiency' : inverter_efficiency,
        'Battery Efficiency' : battery_efficiency,
    }

    return system_param