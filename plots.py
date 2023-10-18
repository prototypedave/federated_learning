import matplotlib.pyplot as plt
import pandas as pd
from funcs import find_value_index

def plot_train_test_latency(train, test, save, title, dir):
    # train curve
    plt.plot(train["Index"], train["latency"], label="training", color="red")
    
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
    plt.plot(df['util'], df['total'], label = "channel utilization")
    plt.xlabel("time (s)")
    plt.ylabel("channel utilization (%)")
    plt.title(title)
    plt.show()
    
    if save:
        pass
        # plt.savefig(dir)


def plot_delay(df, save, dir, title, x):
    plt.plot(df['util'], df['total'], label = "E2E delay")
    plt.xlabel(x)
    plt.ylabel("delay (s)")
    plt.title(title)
    plt.show()
    
    if save:
        pass
        # plt.savefig(dir)


RESULTS_DIR = "results_1/"
SAVE_PLOTS = True

if __name__ == "__main__":
    #channel_spd = pd.read_csv((RESULTS_DIR + "v21_speed.csv"), header=None, names=['util', 'total', 'spd'])
    #channel_spd = channel_spd.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
    #print(channel_spd)

    ##### PLOT CHANNEL UTILIZATION #####
    #dir = RESULTS_DIR + "/channel_utilization/speed.png"
    #title = "Channel Utilization Relative to Vehicle Speed"
    #plot_channel_utilization(df=channel_spd, save=SAVE_PLOTS, title=title, dir=dir)

    # E2E delay 5G Speed
    delay_spd_5g = pd.read_csv((RESULTS_DIR + "e2edelay5gSpeed.csv"), header=None, names=['util', 'total', 'spd'])
    delay_spd_5g = delay_spd_5g.groupby('spd').agg({'util': 'mean', 'total': 'mean'}).reset_index()
    delay_spd_5g = delay_spd_5g.groupby('util').agg({'spd': 'mean', 'total': 'mean'}).reset_index()


    ##### PLOT E2E DELAY #####
    dir = RESULTS_DIR + "/E2E/speed_5g.png"
    title = "E2E delay (5g range) Relative to Vehicle Speed"
    x = "Transmission range (mhz)"
    plot_delay(df=delay_spd_5g, save=SAVE_PLOTS, dir=dir, title=title, x=x)
