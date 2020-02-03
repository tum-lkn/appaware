#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pandas as pd
import matplotlib.pylab as plt
from os.path import join as pjoin

log = logging.getLogger(__name__)

def create_plots_from_file(csvf, folder_out):

    log.debug("Creating search result plots from %s in %s" % (csvf, folder_out))

    df = pd.read_csv(csvf)
    create_plots(df, folder_out)

def create_plots(df, folder_out):

    plots = [(plot_utility, "utility"),
             (plot_applications, "applications"),
             (plot_capacity, "capacity"),
             (plot_approx_delay, "approx_delay")]

    for func, name in plots:
        fname = pjoin(folder_out, "plot_%s.png" % name)
        func(df, fn=fname)

def plot_utility(df, fn=None):

    f, ax = plt.subplots()

    ax.scatter(df.flow_cnt, df.min_U, marker="o")
    ax.plot(df.flow_cnt, df.min_U, alpha=0.3)

    ax.set_xlabel("Number of Flows")
    ax.set_ylabel("Minimum Utility")

    ax.set_ylim([1, 5])

    ax.grid(True, alpha=.3)

    if fn:
        f.savefig(fn)
        plt.close()

def plot_applications(df, fn=None):

    f, ax = plt.subplots()

    for model in ['model_ssh', 'model_web', 'model_webdl', 'model_video']:

        y = df.loc[:,'%s_cnt' % model]# / df.loc[:,'flow_cnt']

        ax.scatter(df.flow_cnt, y, label=model)
        ax.plot(df.flow_cnt, y, alpha=.3, label="")

    ax.legend()

    ax.grid(True, alpha=.3)

    ax.set_xlabel("Number of Flows")
    ax.set_ylabel("Number of Applications")

    if fn:
        f.savefig(fn)
        plt.close()

def plot_capacity(df, fn=None):

    f, ax = plt.subplots()

    #y = df.loc[:,'%s_cnt' % model]# / df.loc[:,'flow_cnt']

    ax.scatter(df.flow_cnt, df.capacity / 1000, color="r", label="Link Capacity")
    ax.plot(df.flow_cnt, df.capacity / 1000, alpha=.3, color="r", label="")

    ax.scatter(df.flow_cnt, df.used_capacity / 1000, color="g", label="Used Capacity")
    ax.plot(df.flow_cnt, df.used_capacity / 1000, alpha=.3, color="g", label="")

    ax.legend()

    ax.grid(True, alpha=.3)

    ax.set_xlabel("Number of Flows")
    ax.set_ylabel("Capacity [Mbps]")

    if fn:
        f.savefig(fn)
        plt.close()

def plot_approx_delay(df, fn=None):

    f, ax = plt.subplots()

    #y = df.loc[:,'%s_cnt' % model]# / df.loc[:,'flow_cnt']

    ax.scatter(df.flow_cnt, df.approx_D, color="b")
    ax.plot(df.flow_cnt, df.approx_D, alpha=.3, color="b")

    ax.grid(True, alpha=.3)

    ax.set_xlabel("Number of Flows")
    ax.set_ylabel("Approx. Delay [ms]")

    if fn:
        f.savefig(fn)
        plt.close()

if __name__ == "__main__":

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}
    logging.basicConfig(level=logging.DEBUG, **logconf)

    csvfile = "../runs_searches/result_20180219_142146_64d8.csv"
    out_folder = "../runs_searches/20180219_142146_64d8/"

    create_plots_from_file(csvfile, out_folder)

    #df = pd.read_csv(csvfile)
    #plot_utility(df)
    #plot_applications(df)
    #plot_capacity(df)
    #plot_approx_delay(df)