import matplotlib.pyplot as plt
import pandas as pd
from funcs import find_value_index

def plot_train_test_latency(train, test, save, title, dir):
    # train curve
    #plt.plot(train["Index"], train["latency"], label="training", color="red")
    
    # test curve
    plt.plot(test["Index"], test["latency"], label="testing", color="green")

    plt.xlabel("Number of Vehicles")
    plt.ylabel("Time (s)")
    plt.title(title)

    plt.legend()
    plt.show()

    if save:
        # plt.savefig((dir + "test_lat"))\
        pass

def plot_network_figs(overhead, save, dir, title, label, x, y, y_lim=100):
    plt.plot(overhead[0], overhead[1], label=label)
    if y_lim != None:
        plt.ylim(0, y_lim)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.grid(True)
    plt.show()

    if save:
        pass
        #plt.savefig(dir)


def plot_net_figs(overhead, save, dir, title, label, x, y, y_lim=100):
    plt.plot(overhead[1], overhead[0], label=label)
    if y_lim != None:
        plt.ylim(0, y_lim)
    plt.xlabel(y)
    plt.ylabel(x)
    plt.title(title)
    plt.grid(True)
    plt.show()

    if save:
        pass
        #plt.savefig(dir)



def plot_network_figs_time(overhead, save, dir, title, label, x, y, y_lim=100):
    f = 1000 / 3600
    plt.plot(overhead[0] * f, overhead[1] * 1000, label=label)
    if y_lim != None:
        plt.ylim(0, y_lim)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.grid(True)
    plt.show()

    if save:
        pass
        #plt.savefig(dir)


def plot_inverted_figs(df, save, dir, title, label, x, y):
    plt.plot(df[1], df[0], label=label)
    plt.ylim(0,100)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.grid(True)
    plt.show()

    if save:
        pass
        #plt.savefig(dir)


def plot_table(table_data, columns, title, dir):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')

    ax.table(cellText=table_data,
            colLabels=columns,
            cellLoc='center',
            loc='center')
    plt.title(title)
    plt.tight_layout()
    plt.show()
    # plt.savefig(dir)


def plot_channel_utilization(df, save, dir, title):
    plt.plot(df['total'] * 10000, df['util'], label = "channel utilization")
    plt.xlabel("channel utilization (%) x 10^-4")
    plt.ylabel("time (s)")
    plt.title(title)
    plt.xlim(0, 4)
    plt.grid(True)
    plt.show()
    
    if save:
        pass
        # plt.savefig(dir)


def plot_delay(df, save, dir, title, x):
    
    plt.plot(df['util'], df['total'] * 1000, label = "E2E delay")
    plt.xlabel(x)
    plt.ylabel("delay (ms)")
    plt.title(title)
    plt.grid(True)
    plt.show()
    
    if save:
        pass
        # plt.savefig(dir)


RESULTS_DIR = "results_training/"
SAVE_PLOTS = True

if __name__ == "__main__":
    
    # Channel utilization
    channel_veh = pd.read_csv((RESULTS_DIR + "v21_vehicles.csv"), header=None, names=['util', 'total', 'veh'])
    channel_veh = channel_veh.groupby('veh').agg({'util': 'mean', 'total': 'mean'}).reset_index()
    
    # trim to be fixed
    lowerBound = 0.0000
    upperBound = 0.0004
    channel_veh = channel_veh[(channel_veh['total'] >= lowerBound) & (channel_veh['total'] <= upperBound)]

    ##### PLOT CHANNEL UTILIZATION #####
    dir = RESULTS_DIR + "/channel_utilization/vehicle.png"
    title = "Channel Utilization Relative to Vehicle Density"
    plot_channel_utilization(df=channel_veh, save=SAVE_PLOTS, dir=dir, title=title)

    channel_spd = pd.read_csv((RESULTS_DIR + "v21_speed.csv"), header=None, names=['util', 'total', 'spd'])
    channel_spd = channel_spd.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
    channel_spd = channel_spd.groupby('util').agg({'total': 'mean', 'spd': 'mean'}).reset_index()

    channel_spd = channel_spd[(channel_spd['total'] >= lowerBound) & (channel_spd['total'] <= upperBound)]
    
    ##### PLOT CHANNEL UTILIZATION #####
    dir = RESULTS_DIR + "/channel_utilization/speed.png"
    title = "Channel Utilization Relative to Vehicle Speed"
    plot_channel_utilization(df=channel_spd, save=SAVE_PLOTS, dir=dir, title=title)
    
    # Routing ratio
    veh_ratio = pd.read_csv((RESULTS_DIR + "routing_vehicles.csv"), header=None)

    ##### PLOT ROUTING RATIO V VEHICLE DENSITY #####
    label = "vehicle routing distribution"
    x = "Successful Routing Ratio"
    y = "Vehicles Density"
    title = "Routing Ratio V Vehicle Density (veh/km)"
    dir = RESULTS_DIR + "routing_ratio/vehicle_routing.png"
    plot_network_figs(overhead=veh_ratio, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y)

    spd_ratio = pd.read_csv((RESULTS_DIR + "routing_speed.csv"), header=None)
    spd_ratio = spd_ratio.groupby(0)[1].mean().reset_index()

    ##### PLOT ROUTING RATIO RELATIVE TO SPEED #####
    label = "speed routing distribution"
    x = "Successsful Routing Ratio"
    y = "Vehicle Speed (km/hr)"
    title = "Routing Ratio V Vehicle Speed"
    dir = RESULTS_DIR + "routing_ratio/speed_routing.png"
    plot_network_figs(overhead=spd_ratio, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y, y_lim=150)

    upp = 7
    dow = 1

    # E2E delay RD
    delay_veh = pd.read_csv((RESULTS_DIR + "e2edelayrdveh.csv"), header=None, names=['util', 'total', 'veh'])
    delay_veh = delay_veh[::10]
    delay_veh = delay_veh.groupby('util').agg({'veh': 'mean', 'total': 'mean'}).reset_index()

    delay_veh = delay_veh[(delay_veh['util'] >= dow) & (delay_veh['util'] <= upp)]

    ##### PLOT E2E DELAY #####
    dir = RESULTS_DIR + "/E2E/vehicle_rd.png"
    title = "E2E delay Relative to Vehicle Density"
    x = "Risk Distance (m)"
    plot_delay(df=delay_veh, save=SAVE_PLOTS, dir=dir, title=title, x=x)

    # E2E delay RD Speed
    delay_spd = pd.read_csv((RESULTS_DIR + "e2edelayrdspd.csv"), header=None, names=['util', 'total', 'spd'])
    delay_spd = delay_spd.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
    delay_spd = delay_spd.groupby('util').agg({'spd': 'mean', 'total': 'mean'}).reset_index()

    delay_spd = delay_spd[(delay_spd['util'] >= dow) & (delay_spd['util'] <= upp)]

    ##### PLOT E2E DELAY #####
    dir = RESULTS_DIR + "/E2E/speed_rd.png"
    title = "E2E delay Relative to Vehicle Speed"
    x = "Risk Distance (m)"
    plot_delay(df=delay_spd, save=SAVE_PLOTS, dir=dir, title=title, x=x)

    # E2E delay 5G
    delay_veh_5g = pd.read_csv((RESULTS_DIR + "e2edelay5g.csv"), header=None, names=['util', 'total', 'veh'])
    delay_veh_5g = delay_veh_5g[::10]
    delay_veh_5g = delay_veh_5g.groupby('util').agg({'veh': 'mean', 'total': 'mean'}).reset_index()

    ##### PLOT E2E DELAY #####
    dir = RESULTS_DIR + "/E2E/vehicle_5g.png"
    title = "E2E delay (5G range) Relative to Vehicle Density"
    x = "Transmission range (m)"
    plot_delay(df=delay_veh_5g, save=SAVE_PLOTS, title=title, dir=dir, x=x)

    # E2E delay 5G Speed
    delay_spd_5g = pd.read_csv((RESULTS_DIR + "e2edelay5gSpeed.csv"), header=None, names=['util', 'total', 'spd'])
    delay_spd_5g = delay_spd_5g.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
    delay_spd_5g = delay_spd_5g.groupby('util').agg({'spd': 'mean', 'total': 'mean'}).reset_index()

    ##### PLOT E2E DELAY #####
    dir = RESULTS_DIR + "/E2E/speed_5g.png"
    title = "E2E delay (5g range) Relative to Vehicle Speed"
    x = "Transmission range (m)"
    plot_delay(df=delay_spd_5g, save=SAVE_PLOTS, dir=dir, title=title, x=x)

    # Routing Efficiency
    veh_eff = pd.read_csv((RESULTS_DIR + "vehicle_efficiency.csv"), header=None)

    ##### PLOT ROUTING EFFICIENCY V VEHICLE DENSITY #####
    label = "routing efficiency"
    x = "Vehicle Density"
    y = "Time (s)"
    title = "Routing Efficiency V Vehicle Density (veh/km)"
    dir = RESULTS_DIR + "routing_efficiency/vehicle_efficiency.png"
    plot_network_figs_time(overhead=veh_eff, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y, y_lim=None)

    spd_eff = pd.read_csv((RESULTS_DIR + "speed_efficiency.csv"), header=None)
    spd_eff = spd_eff.groupby(0)[1].mean().reset_index()

    ##### PLOT ROUTING EFFICIENCY V VEHICLE DENSITY #####
    label = "routing efficiency"
    x = "Vehicle Speed (m/s)"
    y = "Time (s)"
    title = "Routing Efficiency V Vehicle Speed (m/s)"
    dir = RESULTS_DIR + "routing_efficiency/speed_efficiency.png"
    plot_network_figs_time(overhead=spd_eff, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y, y_lim=None)
