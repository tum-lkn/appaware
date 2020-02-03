#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import networkx as nx
import networkx.readwrite.json_graph as json_graph

if __name__ == "__main__":

    G = nx.DiGraph()

    edges = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
    cap = 10

    for e in edges:
        G.add_edge(e[0], e[1], capacity=cap)
        G.add_edge(e[1], e[0], capacity=cap)

    with open("G.json", "w") as f:
        d = json_graph.node_link_data(G)
        json.dump(d, f, indent=4, sort_keys=True)

    applications = {0: {'src': 0, 'dst': 5, 'model': 'model_generic'}}

    with open("apps.json", "w") as f:
        json.dump(applications, f, indent=4, sort_keys=True)

    dis_cnt = 40

    app_cnt = len(flows)

    A_MOS_T = np.zeros((len(flows), dis_cnt, 4))

    # Generic service model
    data_rates = np.linspace(1, 10, dis_cnt)
    delays = np.linspace(500, 10, dis_cnt)

    xx, yy = np.meshgrid(data_rates, delays, sparse=True)

    model_generic = np.zeros((2, xx.size, yy.size))

    model_generic[0] = 5 - (xx + yy) / (10 + 500) * 5
    model_generic[1] =  5 - (xx + yy) / (10 + 500) * 5

    np.save("data_rates.npy", data_rates)
    np.save("delays.npy", delays)

    np.save("model_generic.npy", model_generic)