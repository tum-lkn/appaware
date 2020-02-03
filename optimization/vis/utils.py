#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import matplotlib.pylab as plt
import numpy as np
from itertools import product

log = logging.getLogger(__name__)

def plot_util(A_UTIL, a, UTIL, UTIL_DELAY, UTIL_TP, fn=None):

    f, ax = plt.subplots()

    ax.set_xlabel("Throughput [Kbps]")
    ax.set_ylabel("Delay [ms]")

    i = np.max(np.argmax((A_UTIL[a]), axis=0))
    j = np.max(np.argmax((A_UTIL[a]), axis=1))

    cmap=plt.cm.get_cmap('RdYlGn')

    xmin, xmax = UTIL_TP[a].min(), UTIL_TP[a].max()
    ymin, ymax = UTIL_DELAY[a].min(), UTIL_DELAY[a].max()

    ims = ax.imshow(UTIL[a].T, cmap=cmap,
                    origin='bottom', aspect='auto',
                    extent=[xmin, xmax, ymin, ymax])

    ax.set_xlim(xmin - 0.5, xmax + 0.5)
    ax.set_ylim(ymin - 0.5, ymax + 0.5)

    ax.scatter(UTIL_TP[a][i], UTIL_DELAY[a][j], s=300, color="black", marker="o")

    gridpoints = list(product(UTIL_TP[a], UTIL_DELAY[a]))
    x1 = [x for x, y in gridpoints]
    ax.scatter([x for x, y in gridpoints], [y for x, y in gridpoints],
               marker="+", color='black', s=50)

    #ax.grid(True)

    cb = plt.colorbar(ims)
    cb.set_label("Utility", rotation=270)

    ax.set_title("Application %d (Utility: %.1f)" % (a, UTIL[a][i, j]))

    log.debug("Application %d: Throughput [%d]: %.1f , Delay [%d]: %.1f, Utility [%d,%d]: %.1f" %
          (a, i, UTIL_TP[a][i], j, UTIL_DELAY[a][j], i, j, UTIL[a][i, j]))

    if fn:
        f.savefig(fn)
        plt.close()

if __name__ == "__main__":

    A_UTIL = np.load("out/out_A_UTIL.npy")
    UTIL = np.load("out/in_UTIL.npy")
    UTIL_DELAY = np.load("out/in_UTIL_DELAY.npy")
    UTIL_TP = np.load("out/in_UTIL_TP.npy")

    for a in range(A_UTIL.shape[0]):
        plot_util(A_UTIL, a, UTIL, UTIL_DELAY, UTIL_TP)

