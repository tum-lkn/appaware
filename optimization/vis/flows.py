#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import matplotlib.pylab as plt

def plot_path_delays(embG, a, FlowDelay, Delay, fn=None):

    f, ax = plt.subplots()

    ax.set_title("Application %d (%.2f ms)" % (a, FlowDelay[a]))

    G = nx.DiGraph()

    for i, j in np.ndindex(embG[a].shape):
        if embG[a, i, j]:
            G.add_edge(i, j)

    pos = nx.shell_layout(G)
    nx.draw(G, pos=pos, with_labels=True)

    edge_labels = {}
    for i, j in nx.edges(G):
        edge_labels[(i,j)]  = "+ %.2f ms" % Delay[i, j]

    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)

    if fn:
        f.savefig(fn)
        plt.close()


if __name__ == "__main__":

    embG = np.load("out/out_embG.npy")
    Delay = np.load("out/out_Delay.npy")
    FlowDelay = np.load("out/out_FlowDelay.npy")

    for a in range(embG.shape[0]):
        plot_path_delays(embG, a, FlowDelay, Delay)