#!/usr/bin/python3

"""
"""

from network import Network
from edge import EdgeServer
import time
import pandas as pd
from plots import *
from funcs import find_value_index


####### Global Variables #######
NUM_VEHICLES = 100
NUM_SWITCHES = 10
DEFAULT = True

RESULTS_DIR = ""
####### SCENARIOS #######
# 100 vehicles
if DEFAULT:
    RESULTS_DIR = "new/"
else:
# 400 vehicles
    RESULTS_DIR = "results_400/"

###### Plots ######
PLOT_ALL: bool = True
SAVE_PLOTS: bool = True



if __name__ == "__main__":
    DEFAULT = True

    # create the edge server
    model = EdgeServer()

    # Network
    net = Network(NUM_VEHICLES, NUM_SWITCHES, RESULTS_DIR)

    # run the network
    net.load_dataset_for_baseline()
    net.run(model)
    net.get_packet_drops()
    time.sleep(5)
    net.end()

    if PLOT_ALL:
        ### training and test latency
        train_lat = pd.read_csv((RESULTS_DIR + "train_latency.csv"), header=None, names=["latency"])
        train_lat["Index"] = train_lat.index
        train_lat = train_lat[["Index", "latency"]]

        test_lat = pd.read_csv((RESULTS_DIR + "test_latency.csv"), header=None, names=["latency"])
        test_lat["Index"] = test_lat.index
        test_lat = test_lat[["Index", "latency"]]

        ##### PLOT TRAIN TEST #####
        plot_title = "Training and Testing Latency for 100 vehicles"
        
        if not DEFAULT:
            plot_title = "Training and Testing Latency for 400 vehicles"
        plot_train_test_latency(train=train_lat, test=test_lat, save=SAVE_PLOTS, title=plot_title, dir=RESULTS_DIR)

        # Network overhead
        overhead = pd.read_csv((RESULTS_DIR + "network_overhead.csv"), header=None)
        overhead = overhead.groupby(0)[1].mean().reset_index()

        ##### PLOT NETWORK OVERHEAD #####
        label = "Network Overhead"
        x = "Vehicle Speed (km/hr)"
        y = "Percentage Overhead"
        title = "Network Overhead with Respect to Vehicle Speed"
        dir = RESULTS_DIR + "network_overhead/overhead.png"
        plot_network_figs(overhead=overhead, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y)

        # Computational Complexity
        complex = pd.read_csv((RESULTS_DIR + "computational_complexity.csv"), header=None)
        complex = complex.groupby(0)[1].mean().reset_index()

        ##### PLOT COMPUTATIONAL COMPLEXITY #####
        label = "complexity"
        x = "Vehicle Speed (km/hr)"
        y = "Computational Complexity (%)"
        title = "Computational Complexity with Respect to Vehicle Speed"
        dir = RESULTS_DIR + "computational_complexity/complexity.png"
        plot_network_figs(overhead=complex, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y)

        # Packet drop ratio
        density = pd.read_csv((RESULTS_DIR + "packet_drop.csv"), header=None)
        density = density[::10]

        speed = pd.read_csv((RESULTS_DIR + "packet_drop_speed.csv"), header=None)
        speed = speed.groupby(0)[1].mean().reset_index()

        speed_values = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

        table_data = []
        count = 0
        for idx, row in density.iterrows():
            dens_idx = idx + 10
            dens_val = row[1]

            val = speed_values[count]
            count += 1
            id = find_value_index(speed[1], val)

            for pos, spd_row in speed.iterrows():
                if pos == id:
                    speed_val = spd_row[1]
                    table_data.append([dens_idx, dens_val, val, speed_val])
        
        col = ['Vehicles Density veh/km', 'Packet Drop Ratio', 'Vehicle Speed km/h', 'Packet Drop Ratio']
        title = "Packet Drop Ratio"
        dir = RESULTS_DIR + "packet_drop/table.png"
        plot_table(table_data, col, title, dir)

        # Routing ratio
        veh_ratio = pd.read_csv((RESULTS_DIR + "routing_vehicles.csv"), header=None)

        ##### PLOT ROUTING RATIO V VEHICLE DENSITY #####
        label = "vehicle routing distribution"
        x = "Risk Distance (m)"
        y = "Vehicles Density"
        title = "Routing Ratio V Vehicle Density (veh/km)"
        dir = RESULTS_DIR + "routing_ratio/vehicle_routing.png"
        plot_network_figs(overhead=veh_ratio, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y)

        spd_ratio = pd.read_csv((RESULTS_DIR + "routing_speed.csv"), header=None)
        spd_ratio = spd_ratio.groupby(0)[1].mean().reset_index()

        ##### PLOT ROUTING RATIO RELATIVE TO SPEED #####
        label = "speed routing distribution"
        x = "Risk Distance (m)"
        y = "Vehicle Speed (km/hr)"
        title = "Routing Ratio V Vehicle Speed"
        dir = RESULTS_DIR + "routing_ratio/speed_routing.png"
        plot_network_figs(overhead=spd_ratio, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y, y_lim=150)

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
        x = "Vehicle Speed (km/hr)"
        y = "Time (s)"
        title = "Routing Efficiency V Vehicle Speed (km/hr)"
        dir = RESULTS_DIR + "routing_efficiency/speed_efficiency.png"
        plot_network_figs_time(overhead=spd_eff, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y, y_lim=None)

        # Channel utilization
        channel_veh = pd.read_csv((RESULTS_DIR + "v21_vehicles.csv"), header=None, names=['util', 'total', 'veh'])
        channel_veh = channel_veh.groupby('veh').agg({'util': 'mean', 'total': 'mean'}).reset_index()

        ##### PLOT CHANNEL UTILIZATION #####
        dir = RESULTS_DIR + "/channel_utilization/vehicle.png"
        title = "Channel Utilization Relative to Vehicle Density"
        plot_channel_utilization(df=channel_veh, save=SAVE_PLOTS, dir=dir, title=title)

        channel_spd = pd.read_csv((RESULTS_DIR + "v21_speed.csv"), header=None, names=['util', 'total', 'spd'])
        channel_spd = channel_spd.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()

        ##### PLOT CHANNEL UTILIZATION #####
        dir = RESULTS_DIR + "/channel_utilization/speed.png"
        title = "Channel Utilization Relative to Vehicle Speed"
        plot_channel_utilization(df=channel_spd, save=SAVE_PLOTS, dir=dir, title=title)

        # Collision rate
        coll = pd.read_csv((RESULTS_DIR + "collision_rate.csv"), header=None)
        coll = coll.groupby(0)[1].mean().reset_index()

        ##### PLOT COLLISION RATE #####
        label = "collision rate"
        x = "Vehicle Speed (km/hr)"
        y = "Rate (%)"
        title = "Possible collision V Vehicle Speed (km/hr)"
        dir = RESULTS_DIR + "/collision/rate.png"
        plot_network_figs(overhead=coll, save=SAVE_PLOTS, dir=dir, title=title, label=label, x=x, y=y, y_lim=None)

        # E2E delay RD
        delay_veh = pd.read_csv((RESULTS_DIR + "e2edelayrdveh.csv"), header=None, names=['util', 'total', 'veh'])
        delay_veh = delay_veh[::10]
        delay_veh = delay_veh.groupby('util').agg({'veh': 'mean', 'total': 'mean'}).reset_index()

        ##### PLOT E2E DELAY #####
        dir = RESULTS_DIR + "/E2E/vehicle_rd.png"
        title = "E2E delay Relative to Vehicle Density"
        x = "Risk Distance (m)"
        plot_delay(df=delay_veh, save=SAVE_PLOTS, dir=dir, title=title, x=x)

        # E2E delay RD Speed
        delay_spd = pd.read_csv((RESULTS_DIR + "e2edelayrdspd.csv"), header=None, names=['util', 'total', 'spd'])
        delay_spd = delay_spd.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
        delay_spd = delay_spd.groupby('util').agg({'spd': 'mean', 'total': 'mean'}).reset_index()

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
        x = "Transmission range (mhz)"
        plot_delay(df=delay_veh_5g, save=SAVE_PLOTS, title=title, dir=dir, x=x)

        # E2E delay 5G Speed
        delay_spd_5g = pd.read_csv((RESULTS_DIR + "e2edelay5gSpeed.csv"), header=None, names=['util', 'total', 'spd'])
        delay_spd_5g = delay_spd_5g.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
        delay_spd_5g = delay_spd_5g.groupby('util').agg({'spd': 'mean', 'total': 'mean'}).reset_index()


        ##### PLOT E2E DELAY #####
        dir = RESULTS_DIR + "/E2E/speed_5g.png"
        title = "E2E delay (5g range) Relative to Vehicle Speed"
        x = "Transmission range (mhz)"
        plot_delay(df=delay_spd_5g, save=SAVE_PLOTS, dir=dir, title=title, x=x)

