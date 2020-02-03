#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from os.path import join as pjoin
import numpy as np
from vis.delay import plot_delayapprox
from vis.flows import plot_path_delays
from vis.utils import plot_util
from vis.topology import plot_digraph_throughput, plot_digraph_delay,\
                         plot_digraph_utilization, create_nxgraph


log = logging.getLogger(__name__)

def plot_by_cfg(cfg):

    log.info("Creating plots for run %s." % cfg['run_id'])

    if cfg['create_delay_plot']:
        log.debug("Creating delay approx. plot.")
        DelayApprox = np.load(pjoin(cfg['run_folder'], "in_DelayTable.npy"))
        plot_delayapprox(DelayApprox,
                         fn=pjoin(cfg['run_folder'], "plt_delayapprox.pdf"))

    if cfg['create_model_plots']:
            log.debug("Creating model plots.")

            A_UTIL = np.load(pjoin(cfg['run_folder'], "out_A_UTIL.npy"))
            UTIL = np.load(pjoin(cfg['run_folder'], "in_UTIL.npy"))
            UTIL_DELAY = np.load(pjoin(cfg['run_folder'], "in_UTIL_DELAY.npy"))
            UTIL_TP = np.load(pjoin(cfg['run_folder'], "in_UTIL_TP.npy"))

            for a in range(A_UTIL.shape[0]):
                fn = pjoin(cfg['run_folder'], "plt_util_a%d.pdf" % a)
                plot_util(A_UTIL, a, UTIL, UTIL_DELAY, UTIL_TP, fn=fn)

    if cfg['create_path_delay_plots']:
            log.debug("Creating path delay plots.")

            embG = np.load(pjoin(cfg['run_folder'], "out_embG.npy"))
            Delay = np.load(pjoin(cfg['run_folder'], "out_Delay.npy"))
            FlowDelay = np.load(pjoin(cfg['run_folder'], "out_FlowDelay.npy"))

            for a in range(embG.shape[0]):
                fn = pjoin(cfg['run_folder'], "plt_path_delay_a%d.pdf" % a)
                plot_path_delays(embG, a, FlowDelay, Delay, fn=fn)

    if cfg['create_topo_plot']:
            log.debug("Creating topology plot.")

            G = create_nxgraph(cfg['run_folder'])

            from networkx.readwrite import json_graph

            with open(pjoin(cfg['run_folder'], "plt_G_export.json"), "w") as f:
                jg = json_graph.node_link_data(G)
                f.write(json.dumps(jg, indent=4, sort_keys=True))

            fn = pjoin(cfg['run_folder'], "plt_topology_throughput.pdf")
            plot_digraph_throughput(G, fn=fn)
            fn = pjoin(cfg['run_folder'], "plt_topology_delay.pdf")
            plot_digraph_delay(G, fn=fn)
            fn = pjoin(cfg['run_folder'], "plt_topology_utilization.pdf")
            plot_digraph_utilization(G, fn=fn)

if __name__ == "__main__":

    cfg = {'run_id': '20180130_145528_bbc9',
           'run_folder': "runs/20180130_145528_bbc9/",
           'create_delay_plot': True,
           'create_model_plots': True,
           'create_path_delay_plots': True,
           'create_topo_plot': True}

    plot_by_cfg(cfg)