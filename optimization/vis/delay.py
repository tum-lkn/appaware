#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join as pjoin
import matplotlib.pylab as plt
import numpy as np


def plot_delayapprox(DelayTable, fn=None):

    f, ax = plt.subplots()

    E = DelayTable.T

    #ax.set_xlim([0, 100])
    #ax.set_ylim([0, 10])
    ax.scatter(E[0], E[1], marker="o", s=4, color="black")

    for i in range(E.shape[1] - 1):
        ax.plot([E[0, i], E[0, i+1]], [E[1, i], E[1, i+1]], alpha=0.6, color="grey")

    ax.set_ylabel("Delay [ms]")
    ax.set_xlabel("Throughput [??]")
    ax.grid(True, alpha=0.3)

    ax.text(0.05, 0.9, "min: %.1f ms @ %.1f ?" % (E[1,0], E[0,0]), transform=ax.transAxes)
    ax.text(0.05, 0.82, "max: %.1f ms @ %.1f ?" % (E[1,-1], E[0,-1]), transform=ax.transAxes)

    if fn:
        f.savefig(fn)
        plt.close()

if __name__ == "__main__":

    run = "runs/20180130_145528_bbc9/"

    DelayTable = np.load(pjoin(run, "in_DelayTable.npy"))

    plot_delayapprox(DelayTable)

    plot_delayapprox(DelayTable, fn=pjoin(run, "plt_delayapprox.pdf"))