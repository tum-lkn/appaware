#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import numpy as np
from os.path import join as pjoin

log = logging.getLogger(__name__)

def flow_summary(a, A_UTIL, U, U_TP, U_D, FlowDelay):

    s = {}

    tp = np.max(np.argmax(A_UTIL[a], axis=0))
    d = np.max(np.argmax(A_UTIL[a], axis=1))

    s['a_idx'] = a
    s['tp_idx'] = tp
    s['d_idx'] = d

    s['TP'] = U_TP[a,tp]
    s['D'] = U_D[a,d]

    s['approx_D'] = FlowDelay[a]

    s['U'] = U[a, tp, d]

    for k, v in s.items():
        if type(v) is np.float64:
            s[k] = float(v)
        if type(v) is np.int64:
            s[k] = int(v)

    return s

def summary(run_folder):

    A_UTIL = np.load(pjoin(run_folder, "out_A_UTIL.npy"))
    UTIL = np.load(pjoin(run_folder, "in_UTIL.npy"))
    UTIL_DELAY = np.load(pjoin(run_folder, "in_UTIL_DELAY.npy"))
    UTIL_TP = np.load(pjoin(run_folder, "in_UTIL_TP.npy"))

    FlowDelay = np.load(pjoin(run_folder, "out_FlowDelay.npy"))

    sumdict = {}

    for a in range(A_UTIL.shape[0]):
        sumdict[a] = flow_summary(a, A_UTIL, UTIL, UTIL_TP, UTIL_DELAY, FlowDelay)

    return sumdict

def create_summary(run_folder, save=[], stage_first=None):

    log.debug("Creating summary of run %s." % run_folder)

    with open(pjoin(run_folder, "cfg.json")) as f:
        cfg = json.load(f)

    with open(pjoin(cfg['run_folder'], "applications.json")) as f:
        applications = json.load(f)

    with open(pjoin(run_folder, "solved.json")) as f:
        solved  = json.load(f)

    sumdict = {'cfg': cfg, 'solved': solved}

    if stage_first:
        sumdict['stage_first'] = stage_first

    sumdict['flows'] = summary(cfg['run_folder'])

    for a, v in applications.items():
        sumdict['flows'][int(a)]['model'] = v['model']
        sumdict['flows'][int(a)]['src'] = v['src']
        sumdict['flows'][int(a)]['dst'] = v['dst']

    for s in [s for s in save if s]:
        log.debug("Saving summary to %s." % s)
        with open(s, "w") as f:
            json.dump(sumdict, f, sort_keys=True, indent=4)

    return sumdict


def print_flow_summary(s):

    print("Application {a_idx}: Throughput [{tp_idx}]: {TP:.1f} , Delay [{d_idx}]: {approx_D:.1f}/{D:.1f} ms, Utility [{tp_idx},{d_idx}]: {U}".format(
          **s))

if __name__ == "__main__":

    run_folder = "out"

    A_UTIL = np.load(pjoin(run_folder, "out_A_UTIL.npy"))
    UTIL = np.load(pjoin(run_folder, "in_UTIL.npy"))
    UTIL_DELAY = np.load(pjoin(run_folder, "in_UTIL_DELAY.npy"))
    UTIL_TP = np.load(pjoin(run_folder, "in_UTIL_TP.npy"))

    FlowDelay = np.load(pjoin(run_folder, "out_FlowDelay.npy"))

    for a in range(A_UTIL.shape[0]):
        s = flow_summary(a, A_UTIL, UTIL, UTIL_TP, UTIL_DELAY, FlowDelay)

        print_flow_summary(s)