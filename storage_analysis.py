

def day_e_plot(results, plot_date):

    import matplotlib.pyplot as plt

    fig = plt.figure()

    results['USAGE'].ix[plot_date].plot(linestyle='-', linewidth=5, color='gray')

    results['grid_demand_peak'].ix[plot_date].plot(marker='o')
    results['grid_demand_offpeak'].ix[plot_date].plot(marker='o')
    results['grid_store'].ix[plot_date].plot(marker='o')
    results['storage_available'].ix[plot_date].plot(marker='')
    results['storage_send'].ix[plot_date].plot(marker='o')

    plt.legend(['Demand',
                'Peak Grid for Demand',
                'Off-Peak Grid for Demand',
                'Grid to Battery',
                'Storage Available',
                'Storage to Demand'])

    plt.show()

def day_purchase(results, plot_date):

    import matplotlib.pyplot as plt

    fig = plt.figure()

    results['USAGE'].ix[plot_date].plot(linestyle='--', linewidth=3, color='gray')

    #results['purchase_peak'].ix[plot_date].plot(marker='.', linestyle='', markersize=13, color='red')
    #results['purchase_offpeak'].ix[plot_date].plot(marker='.', linestyle='', markersize=13, color='orange', grid='off')

    results['purchase_peak'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color='red')
    results['purchase_offpeak'].ix[plot_date].plot(marker='', linestyle='-', linewidth=2, color='orange', grid='off')

    plt.legend(['Demand','Purchased During Peak Hours', 'Purchased During Off-Peak Hours'])

    plt.show()