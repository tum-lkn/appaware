#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import logging
import time
import json
import itertools as it
import numpy as np
from os.path import join as pjoin
import networkx as nx
import networkx.readwrite.json_graph as json_graph

log = logging.getLogger(__name__)

def gen_id():
    return "{}_{}".format(time.strftime('%Y%m%d_%H%M%S'),
                          str(uuid.uuid4())[:4])

from vis.topology import print_graph, plot_delay
from vis.apps import print_app_list
from vis.models import plot_model, plot_model2


def load_topology(nxf):

    log.debug("Loading topology from %s." % nxf)

    from networkx.readwrite import json_graph

    with open(nxf) as f:
        data = json.load(f)

    G = json_graph.node_link_graph(data)

    log.debug("Topology has %d nodes and %d edges." % (G.number_of_nodes(), G.number_of_edges()))

    C = np.zeros((G.number_of_nodes(), G.number_of_nodes()))

    for u, v, d in G.edges(data=True):
        edata = G.get_edge_data(u, v)
        if edata:
            C[u, v] = edata['capacity']

    return G, C

def load_applications(appf, model_dir):
    """

    :param appf: JSON file with the application configurations
    :param model_dir: Folder where to find the utility models
    """

    with open(appf) as f:
        apps = json.load(f)

    for k in apps.keys():
        apps[int(k)] = apps[k]
        del apps[k]

    for a in apps.values():
        load_model(a, model_dir, a['model'])

    return apps


def load_model(a, model_dir, model):
    """

    :param a: (Application) dict to add the loaded model and params to.
    :param model_dir: Model directory
    :param model: Name of the model
    """

    modelp = pjoin(model_dir, "%s.npy" % model)

    log.debug("Loading model: %s" % modelp)

    a['utility_npy'] = np.load(modelp)

    log.debug("Model shape: %s" % str(a['utility_npy'].shape))

    paramsp = pjoin(model_dir, "%s.json" % model)

    log.debug("Loading model params: %s" % paramsp)

    with open(paramsp) as f:
        params = json.load(f)

    assert(len(params['delays']) == a['utility_npy'].shape[0])
    assert(len(params['rates']) == a['utility_npy'].shape[1])

    a['model_params'] = params
    a['model_delays_npy'] = np.array(params['delays'])
    a['model_rates_npy'] = np.array(params['rates'])

def load_delay_approx(delayf):

    delay_approx = np.load(delayf)

    return delay_approx


if __name__ == "__main__":

    import os
    import argparse

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}
    logging.basicConfig(level=logging.DEBUG, **logconf)

    parser = argparse.ArgumentParser(description="Solve simple bottleneck scenarios.")
    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')
    parser.add_argument('--run-folders', help="Where to store the detailed run results.",
                        default="runs")
    parser.add_argument('--summary', '-s', help="Filename where to store the summary.", default="summary.json")

    args = parser.parse_args()

    output = "runs"

    # Generate a unique run_id
    cfg = {'run_id': gen_id(),
           'create_topo_plot': True,
           'create_app_list': True,
           'create_delay_plot': True,
           'create_model_plots': True}

    cfg['run_folder'] = os.path.join(output, cfg['run_id'])

    log.debug("Creating run folder: %s" % cfg['run_folder'])

    os.makedirs(cfg['run_folder'], exist_ok=True)


    topology = "samples/simple/G.json"

    G, C = load_topology(topology)

    if cfg['create_topo_plot']:
        print_graph(G, pjoin(cfg['run_folder'], "topology.png"))

    apps = load_applications("samples/simple/apps.json", "samples/simple/")

    print_app_list(apps, pjoin(cfg['run_folder'], "apps.txt"))

    delay_approx = load_delay_approx("samples/simple/delay_approx.npy")

    if cfg['create_delay_plot']:
        plot_delay(delay_approx, fn=pjoin(cfg['run_folder'], "delay_approx.pdf"))

    if cfg['create_model_plots']:
        for a in apps.values():
            plot_model2(a['utility_npy'], a['model_rates_npy'], a['model_delays_npy'],
                       fn=pjoin(cfg['run_folder'], "model_%s.pdf" % a['id']))
