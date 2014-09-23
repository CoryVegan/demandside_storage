
# Some decent colors
mint = '#66FF99'
navy = '#000066'
apple = '#009933'
redorange = '#FF3300'
purple = '#9900FF'
gold = '#CC9900'
darkgray = '#333333'
lightgray = '#B2B2B2'

def day_e_plot(results, plot_date, save):

    import matplotlib.pyplot as plt

    fig = plt.figure()

    results['USAGE'].ix[plot_date].plot(linestyle='--', linewidth=5, color=darkgray)

    results['grid_demand_peak'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color=redorange)
    results['grid_demand_offpeak'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color=purple)
    results['grid_store'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color=mint)
    results['storage_available'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color=apple)
    results['storage_send'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color=navy, grid='off')

    plt.axvspan(plot_date+' 10:00:00',plot_date+' 19:00:00', facecolor=lightgray, alpha=0.5)

    plt.legend(['Demand',
                'Peak Grid for Demand',
                'Off-Peak Grid for Demand',
                'Grid to Battery',
                'Storage Available',
                'Storage to Demand'],
               labelspacing=.2,
               prop={'size':10})

    plt.title('Demand-Side Storage Model, Hourly Energy State \n %s' %plot_date)
    plt.ylabel('Hourly Electricity State (kWh)', fontsize=14)

    if save == True:

        filename = 'Daily_Energy_State_'+plot_date+'.png'

        plt.savefig(filename)

    plt.show()

def day_purchase(results, plot_date, save):

    import matplotlib.pyplot as plt

    fig = plt.figure()

    results['USAGE'].ix[plot_date].plot(linestyle='--', linewidth=3, color='gray')

    #results['purchase_peak'].ix[plot_date].plot(marker='.', linestyle='', markersize=13, color='red')
    #results['purchase_offpeak'].ix[plot_date].plot(marker='.', linestyle='', markersize=13, color='orange', grid='off')

    results['purchase_peak'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color='red')
    results['purchase_offpeak'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color='orange', grid='off')

    plt.axvspan(plot_date+' 10:00:00',plot_date+' 19:00:00', facecolor=lightgray, alpha=0.5)

    plt.legend(['Demand','Purchased During Peak Hours', 'Purchased During Off-Peak Hours'], labelspacing=.2, prop={'size':10})
    plt.ylabel('Electricity (kWh)', fontsize=14)
    plt.title('Demand-Side Storage Model, Hourly Electricity From Grid \n %s' %plot_date)

    if save == True:

        filename = 'Daily_Energy_Purchased_'+plot_date+'.png'

        plt.savefig(filename)

    plt.show()