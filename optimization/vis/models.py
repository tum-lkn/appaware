#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt

def plot_model2(UTIL, UTIL_DELAY, UTIL_TP, fn=None):

    f, ax = plt.subplots()

    ax.set_title("Application Model")

    ax.set_xlabel("Throughput")
    ax.set_ylabel("Delay")

    cmap=plt.cm.get_cmap('RdYlGn')

    xmin, xmax = UTIL_TP.min(), UTIL_TP.max()
    ymin, ymax = UTIL_DELAY.min(), UTIL_DELAY.max()

    ims = ax.imshow(UTIL, cmap=cmap,
                    origin='lower', aspect='auto',
                    extent=[xmin, xmax, ymin, ymax])

    ax.set_xlim(xmin - 0.5, xmax + 0.5)
    ax.set_ylim(ymin - 0.5, ymax + 0.5)

    cb = plt.colorbar(ims)
    cb.set_label("Utility", rotation=270)

    if fn:
        f.savefig(fn)
        plt.close()

def plot_model(rate, delay, utility, fn=None):

    f, ax = plt.subplots()

    ax.set_xlabel("Data-rate (?)")
    ax.set_ylabel("RTT (ms)")

    cmap=plt.cm.get_cmap('RdYlGn')

    ims = ax.imshow(utility.T, cmap=cmap,
                    origin='lower', aspect='auto',
                    extent=[delay.min(), delay.max(),
                            rate.min(), rate.max()])

    ax.set_xlabel("Delay (ms)")
    ax.set_ylabel("Throughput (Kilobits/s)")

    cb = plt.colorbar(ims)
    cb.set_label("Utility", rotation=270)

    #ax.grid(True)

    if fn:
        f.savefig(fn)
        plt.close()

if __name__ == "__main__":

    pass