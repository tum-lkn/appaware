#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join as pjoin
import networkx as nx
import matplotlib.pylab as plt
import numpy as np

def create_nxgraph(run_folder):

    import json
    from networkx.readwrite import json_graph

    Gnpy = np.load(pjoin(run_folder, "in_Gnpy.npy"))

    G = nx.DiGraph()

    for i, j in np.ndindex(Gnpy.shape):
        if Gnpy[i, j]:
            G.add_edge(i, j)

    C = np.load(pjoin(run_folder, "in_C.npy"))

    for s, t, data in G.edges(data=True):
        data['capacity'] = C[s,t]

    Delay = np.load(pjoin(run_folder, "out_Delay.npy"))
    h_Traffic_Out = np.load(pjoin(run_folder, "out_h_Traffic_Out.npy"))

    for s, t, data in G.edges(data=True):
        data['used'] = h_Traffic_Out[s,t]
        data['delay'] = Delay[s,t]

    return G

def plot_digraph(G, edge_labels, fn=None):

    f, ax = plt.subplots(figsize=(7,7))

    pos = nx.spring_layout(G)
    nx.draw(G, pos=pos, with_labels=True)

    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)

    if fn:
        f.savefig(fn)
        plt.close()

def plot_digraph_throughput(G, fn=None):

    edge_labels_cap = nx.get_edge_attributes(G,'capacity')
    edge_labels_used = nx.get_edge_attributes(G,'used')

    edge_labels = {}
    for i, j in edge_labels_used.keys():
        edge_labels[(i,j)]  = "%.1f / %.1f Kbps" \
                   % (edge_labels_used[(i,j)], edge_labels_cap[(i,j)])

    plot_digraph(G, edge_labels, fn=fn)

def plot_digraph_delay(G, fn=None):

    edge_labels_delay = nx.get_edge_attributes(G,'delay')

    edge_labels = {}
    for i, j in edge_labels_delay.keys():
        edge_labels[(i,j)]  = "+ %.2f ms" % \
                    (edge_labels_delay[(i,j)])

    plot_digraph(G, edge_labels, fn=fn)

def plot_digraph_utilization(G, fn=None):

    edge_labels_cap = nx.get_edge_attributes(G,'capacity')
    edge_labels_used = nx.get_edge_attributes(G,'used')
    edge_labels_delay = nx.get_edge_attributes(G,'delay')

    edge_labels = {}
    for i, j in edge_labels_used.keys():
        edge_labels[(i,j)]  = "%.1f %% (+ %.1f ms)" \
                   % (edge_labels_used[(i,j)] / edge_labels_cap[(i,j)] * 100,
                      edge_labels_delay[(i,j)])

    plot_digraph(G, edge_labels, fn=fn)


def print_graph(G, fn=None):

    f, ax = plt.subplots(figsize=(7,7))

    pos = nx.spring_layout(G)
    nx.draw(G, pos=pos, with_labels=True)

    edge_labels_C = nx.get_edge_attributes(G, 'capacity')

    edge_labels = {}
    for i, j in edge_labels_C.keys():
        edge_labels[(i,j)]  = "%.1f" % edge_labels_C[(i,j)]

    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)

    if fn:
        f.savefig(fn)
        plt.close()

def print_graph_delay(G, fn=None):

    f, ax = plt.subplots(figsize=(7,7))

    pos = nx.spring_layout(G)
    nx.draw(G, pos=pos, with_labels=True)

    edge_labels_delay = nx.get_edge_attributes(G,'delay')

    edge_labels = {}
    for i, j in edge_labels_delay.keys():
        edge_labels[(i,j)]  = "+ (%.2f ms, %.2f ms)" % \
                    (edge_labels_delay[(i,j)], edge_labels_delay[(j,i)])

    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)

    if fn:
        f.savefig(fn)
        plt.close()


def write_dotfiles(G, folder="out"):

    from networkx.drawing.nx_pydot import write_dot

    # Add label for dot file
    for s, t, data in G.edges(data=True):
        data['label'] = "%d / %d" % (data['used'], data['capacity'])

    write_dot(G, os.path.join(folder, 'G_traffic.dot'))

    for s, t, data in G.edges(data=True):
        data['label'] = "+ %.2f" % (data['delay'])

    write_dot(G, os.path.join(folder, 'G_delay.dot'))

if __name__ == "__main__":

    import json
    from networkx.readwrite import json_graph

    with open("out/G.json") as f:
        Gjson = json.load(f)

    G = json_graph.node_link_graph(Gjson)
    G = G.to_directed()

    C = np.load("out/in_C.npy")

    DelayTable = np.load("out/in_DelayTable.npy")
    plot_delay(DelayTable)

    Delay = np.load("out/out_Delay.npy")

    for s, t, data in G.edges(data=True):
        data['capacity'] = C[s,t]

    print_graph(G)

    h_Traffic_Out = np.load("out/out_h_Traffic_Out.npy")

    for s, t, data in G.edges(data=True):
        data['used'] = h_Traffic_Out[s,t]
        data['delay'] = Delay[s,t]

    print_graph_solution(G)

    print_graph_delay(G)

    write_dotfiles(G)

"""
    G = nx.DiGraph()

    edges = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
    cap = 10

    for e in edges:
        G.add_edge(e[0], e[1], capacity=cap)
        G.add_edge(e[1], e[0], capacity=cap)

    print_graph(G)
    #print_graph(G, fn="test.png")

    delay_dis_cnt = 10
    delay_approx = np.zeros((delay_dis_cnt, 2))
    delay_approx[:,0] = np.linspace(0.1, 1.0, delay_dis_cnt)
    delay_approx[:,1] = np.linspace(10, 100, delay_dis_cnt)

    plot_delay(delay_approx)
"""
