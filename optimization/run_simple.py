#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import logging
import time
import json
import numpy as np
import networkx as nx
from os.path import join as pjoin

log = logging.getLogger(__name__)

def gen_id():
    return "{}_{}".format(time.strftime('%Y%m%d_%H%M%S'),
                          str(uuid.uuid4())[:4])

def load_model(a, model_dir, model):
    """

    :param a: (Application) dict to add the loaded model and params to.
    :param model_dir: Model directory
    :param model: Name of the model
    """

    model_U = pjoin(model_dir, "%s_U.npy" % model)

    log.debug("Loading model U: %s" % model_U)

    a['U'] = np.load(model_U)

    log.debug("Model shape: %s" % str(a['U'].shape))

    model_D = pjoin(model_dir, "%s_D.npy" % model)
    model_TP = pjoin(model_dir, "%s_TP.npy" % model)

    log.debug("Loading D and TP: %s and %s" % (model_D, model_TP))

    a['TP'] = np.load(model_TP)
    a['D'] = np.load(model_D)

    assert(a['TP'].shape[0] == a['U'].shape[0])
    assert(a['D'].shape[0] == a['U'].shape[1])


def run_simple(cfg, summary, no_grb_print=False):

    log.debug("Creating run folder: %s" % cfg['run_folder'])

    # Overwritting run_folder for testing
    # cfg['run_folder'] = "out"
    os.makedirs(cfg['run_folder'], exist_ok=True)

    with open(pjoin(cfg['run_folder'], "run_simple_cfg.json"), "w") as f:
        json.dump(cfg, f, sort_keys=True, indent=4)

    scenario = cfg['scenario']

    #
    # Generate topology
    #

    G = nx.DiGraph()
    # Bottleneck: 0 -> 1 -> 2
    G.add_edge(0, 1)
    G.add_edge(1, 2)

    Gnpy = np.zeros((G.number_of_nodes(), G.number_of_nodes()))

    for u, v in G.edges():
        Gnpy[u, v] = 1
        # Gnpy[v,u] = 1

    # Capacity
    C = np.zeros(Gnpy.shape)

    for u, v in G.edges():
        C[u, v] = scenario['capacity']
        C[v, u] = scenario['capacity']

    #
    # Delay Approximation
    DelayApprox = np.load(cfg['delay_approx'])

    DelayApprox.T[:, 0] = DelayApprox.T[:, 0] * scenario['capacity']

    # Delay Approximations are stored as seconds, convert here to
    # milliseconds.
    DelayApprox.T[:, 1] = DelayApprox.T[:, 1] * 1000

    #
    # Load application models
    #

    # Preload first model to get the shapes
    a = {}
    load_model(a, cfg['model_dir'], scenario['flows']['0']['model'])

    Ua = np.zeros((len(scenario['flows']), *a['U'].shape))
    TPa = np.zeros((len(scenario['flows']), *a['TP'].shape))
    Da = np.zeros((len(scenario['flows']), *a['D'].shape))

    applications = {}
    for a_idx, flow in scenario['flows'].items():
        applications[a_idx] = {'src': 0, 'dst': 2, 'model': flow['model']}

        a = {}
        load_model(a, cfg['model_dir'], flow['model'])
        Ua[int(a_idx)] = a['U']
        TPa[int(a_idx)] = a['TP']
        Da[int(a_idx)] = a['D']

    with open(pjoin(cfg['run_folder'], "applications.json"), "w") as f:
        json.dump(applications, f, sort_keys=True, indent=4)

    flows = []
    for app in sorted(applications.keys()):
        flows += [(0, 2)]

    #
    # Same utility per application type
    #
    flow_types = None

    if not cfg.get('no_flow_types', False):

        flow_types = {}
        for a_idx, flow in scenario['flows'].items():
            if flow['model'] not in flow_types:
                flow_types[flow['model']] = []
            flow_types[flow['model']].append(int(a_idx))

        log.debug("Using flow types: %s" % flow_types)

    #
    # Solve the scenario
    #
    from solving.tools import sp_init_embG
    from solving.solve import solve

    init_embG = sp_init_embG(G, Gnpy, flows)

    solve(cfg['run_folder'], Gnpy, init_embG, flows, Ua, TPa, Da, C, DelayApprox.T,
          time_limit=cfg['time_limit'], no_grb_print=no_grb_print,
          flow_types=flow_types)

    #
    # Post-process
    # Create the output files
    from tools.postprocessing import create_summary

    # First stage
    run_folder_fs = pjoin(cfg['run_folder'], "stage_first")

    for run_folder in [cfg['run_folder'], run_folder_fs]:
        with open(pjoin(run_folder, "cfg.json"), "w") as f:
            json.dump(cfg, f, sort_keys=True, indent=4)

    sumdict_fs = create_summary(run_folder_fs,
                                save=[pjoin(run_folder_fs, "summary.json")])

    # Second stage
    sumdict = create_summary(cfg['run_folder'],
                             save=[pjoin(cfg['run_folder'], "summary.json"),
                                   summary],
                             stage_first=sumdict_fs)

    solved = sumdict['solved']

    log.info(
        "Solved in %.2fs with a minimum utility of %.1f (first stage: %.1f)."
        % (solved['optimization_duration'], solved['min_utility'], sumdict_fs['solved']['min_utility']))

    if cfg['plotting']:
        from vis.tools import plot_by_cfg
        plot_by_cfg(cfg)

    return sumdict


if __name__ == "__main__":

    import argparse

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}
    logging.basicConfig(level=logging.DEBUG, **logconf)

    parser = argparse.ArgumentParser(description="Solve simple bottleneck scenarios.")
    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')
    parser.add_argument('--run-folders',
                        help="Where to store the detailed run results. (default: %(default)s)",
                        default="runs")
    parser.add_argument('--summary', '-s',
                        help="Filename where to store the summary. (default: %(default)s)",
                        default="summary.json")
    parser.add_argument('--model_dir', '-m',
                        help="Where the application models are stored. (default: %(default)s)",
                        default="models/postprocessing/models/")
    parser.add_argument('--scenario',
                        help="Bottleneck scenario file. (default: %(default)s)",
                        default="samples/simple/2ssh.json")
    parser.add_argument('--delay-approx',
                        help="Which delay approx. to use. (default: %(default)s)",
                        default="samples/simple/max80perc.npy")
    parser.add_argument('--no-flow-types',
                        help="Deactivate same MOS per application type.",
                        action="store_true",
                        default=False)
    parser.add_argument('--time-limit',
                        help="Time limit for solving the scenario in seconds. (default: %(default)s)",
                        default=100)
    parser.add_argument('--plotting',
                        help="Activate plotting of results. (default: %(default)s)",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    log.info("Loading scenario file %s." % args.scenario)

    with open(args.scenario) as f:
        scenario = json.load(f)

    # Generate a unique run_id
    cfg = {'run_id': gen_id(),
           'plotting': args.plotting,  # Overwrites all the other plotting settings
           'create_topo_plot': True, # plot flags un-used at the moment
           'create_app_list': True,
           'create_path_delay_plots': True,
           'create_delay_plot': True,
           'create_model_plots': True,
           'model_dir': args.model_dir,
           'scenario': scenario,
           'delay_approx': args.delay_approx,
           'time_limit': args.time_limit,
           'no_flow_types': args.no_flow_types}

    cfg['run_folder'] = os.path.join(args.run_folders, cfg['run_id'])

    run_simple(cfg, args.summary)
