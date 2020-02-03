#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
import random
import os
import json
import networkx as nx
import logging
from os.path import join as pjoin
from solving.tools import vf, convert, grb_ndarr_py


log = logging.getLogger(__name__)

def build_model(Gnpy, init_embG, flows, UTIL, UTIL_TP, UTIL_DELAY, C,
          DelayTable, flow_types=None, MOS_min_lb=1.0):

    from gurobipy import Model, quicksum, GRB, LinExpr

    m = Model()

    MOS_min = m.addVar(lb=MOS_min_lb, ub=5.0, vtype=GRB.SEMICONT,
                       name="MOS_min")

    m.update()

    # Flow embedding matrix
    embG = np.zeros((len(flows), *Gnpy.shape), dtype=object)

    #
    # Only add variables for physical links
    #
    for f, (from_id, to_id) in enumerate(flows):

        for i, j in np.ndindex(Gnpy.shape):
            if Gnpy[i, j] == 1:
                var = m.addVar(vtype=GRB.BINARY, name="V_%s" % vf(f, i, j))
                embG[f, i, j] = var

        m.update()

        for i, j in np.ndindex(Gnpy.shape):
            if Gnpy[i, j] == 1:
                embG[f, i, j].start = init_embG[f, i, j]

    #
    # Start and end constrains
    #
    for f, (from_id, to_id) in enumerate(flows):

        # Start outgoing
        lexp = quicksum(embG[f, from_id, :].flatten())
        m.addConstr(lexp == 1, name="START_OUT_%s" % vf(f, from_id))

        # Start incoming
        lexp = quicksum(embG[f, :, from_id].flatten())
        m.addConstr(lexp == 0, name="START_IN_%s" % vf(f, from_id))

        # End outgoing
        lexp = quicksum(embG[f, to_id, :].flatten())
        m.addConstr(lexp == 0, name="END_OUT_%s" % vf(f, to_id))

        # End incoming
        lexp = quicksum(embG[f, :, to_id].flatten())
        m.addConstr(lexp == 1, name="END_IN_%s" % vf(f, to_id))

    #
    # Flow conservation
    #
    for f, (from_id, to_id) in enumerate(flows):

        for i in range(embG.shape[1]):
            if i == from_id or i == to_id:
                continue

            outgoing = quicksum(embG[f, i, :].flatten())
            incoming = quicksum(embG[f, :, i].flatten())
            constr = (0 == outgoing - incoming)

            m.addConstr(constr, name='FC_%s' % vf(f, i))

            constr = (outgoing <= 1)
            m.addConstr(constr, name='FC_1_%s' % vf(f, i))
            constr = (incoming <= 1)
            m.addConstr(constr, name='FC_2_%s' % vf(f, i))

    # Just a bunch of helper variables
    T = []
    Td = []

    app_cnt = len(flows)

    for a in range(app_cnt):
        T.append(m.addVar(vtype=GRB.SEMICONT, name="T_a%i" % a, lb=0.0))
        Td.append(m.addVar(vtype=GRB.SEMICONT, name="Td_a%i" % a, lb=0.0))

    b_MOS_a = [None] * app_cnt

    MOS_apps = []

    for a in range(app_cnt):
        MOS_a = m.addVar(lb=1, ub=5, vtype=GRB.SEMICONT,
                         name="MOS_a%i" % a)
        MOS_apps.append(MOS_a)

    # Which delay and throughput to select for an application
    A_TP = np.zeros(UTIL_TP.shape, dtype=object)
    A_DELAY = np.zeros(UTIL_DELAY.shape, dtype=object)

    for idx in np.ndindex(A_TP.shape):
        A_TP[idx] = m.addVar(vtype=GRB.BINARY, name="A_TP_a%d_tp%d" % idx)

    for idx in np.ndindex(A_DELAY.shape):
        A_DELAY[idx] = m.addVar(vtype=GRB.BINARY, name="A_DELAY_a%d_d%d" % idx)

    m.update()

    # Per application, only one throughput & delay can be selected
    for a in range(app_cnt):
        m.addConstr(quicksum(A_TP[a,:]) == 1, name="sum_A_TP_a%d" % (a))
        m.addConstr(quicksum(A_DELAY[a,:]) == 1, name="sum_A_DELAY_a%d" % (a))

    # Helper variable to store the result of A_DELAY * A_TP
    A_UTIL = np.zeros(UTIL.shape, dtype=object)

    for a, tp, d in np.ndindex(A_UTIL.shape):
        A_UTIL[a, tp, d] = m.addVar(vtype=GRB.BINARY, name="A_UTIL_a%d_tp%d_d%d" % (a, tp, d))

    m.update()

    # Create decision A_UTIL from A_TP and A_DELAY
    # which utility to choose for which application
    for a, tp in np.ndindex((A_UTIL.shape[0], A_UTIL.shape[1])):
        m.addConstr(quicksum(A_UTIL[a, tp, :].flatten()) == A_TP[a, tp], name="A_UTIL_A_TP_a%d_tp%d" % (a, tp))
    for a, d in np.ndindex((A_UTIL.shape[0], A_UTIL.shape[2])):
        m.addConstr(quicksum(A_UTIL[a, :, d].flatten()) == A_DELAY[a, d], name="A_UTIL_A_DELAY_a%d_tp%d" % (a, d))

    m.update()

    #
    # Helper variables to store selected utility for a flow
    #
    for a in range(app_cnt):

        # Selected MOS for application a
        m.addConstr(MOS_apps[a] == quicksum((A_UTIL[a, :] * UTIL[a]).flatten()))

        # Selected Throughput & Delay
        m.addConstr(T[a] == quicksum(A_TP[a, :] * UTIL_TP[a]), name="T_a%i" % a)
        m.addConstr(Td[a] == quicksum(A_DELAY[a, :] * UTIL_DELAY[a]), name="Td_a%i" % a)

    m.update()

    #
    # If flow_types is set, make sure all flows of the same type have the same
    # utility value.
    #
    if flow_types:
        for ftype, apps in flow_types.items():
            for app_A, app_B in zip(apps[:-1], apps[1:]):
                m.addConstr(MOS_apps[app_A] == MOS_apps[app_B],
                            name="FT_%s_U_%d_eq_%d" % (ftype.upper(), app_A, app_B))
                m.addConstr(T[app_A] == T[app_B],
                            name="FT_%s_T_%d_eq_%d" % (ftype.upper(), app_A, app_B))
                m.addConstr(Td[app_A] == Td[app_B],
                            name="FT_%s_Td_%d_eq_%d" % (ftype.upper(), app_A, app_B))

    h_Traffic = np.zeros(Gnpy.shape, dtype=object)

    for i, j in np.ndindex(h_Traffic.shape):
        if Gnpy[i, j] == 1:
            #h_Traffic[i, j] = m.addVar(vtype=GRB.SEMICONT, name="TRAFFIC_i%i_j%i" % (i, j))
            h_Traffic[i, j] = LinExpr()

    #
    # Calculate Traffic Matrix
    #
    for i, j in np.ndindex(h_Traffic.shape):
        if Gnpy[i, j] == 1:
            # Source target data-rate
            expr_st = LinExpr()

            for f, _ in enumerate(flows):
                h_Traffic[i,j] += embG[f, i, j] * T[f]

    #
    # Add traffic constrains
    #
    for i, j in np.ndindex(h_Traffic.shape):
        if Gnpy[i, j] == 1:
            m.addConstr(h_Traffic[i,j] <= (C[i,j]), name="TP_i%03d_j%03d" % (i, j))

    #
    # Helper variables to get the current traffic
    #
    h_Traffic_Out = np.zeros(h_Traffic.shape, dtype=object)
    for i, j in np.ndindex(h_Traffic.shape):
        if Gnpy[i, j] == 1:
            h_Traffic_Out[i, j] = m.addVar(vtype=GRB.SEMICONT, name="TRAFFIC_OUT_i%d_j%d" % (i, j), lb=0.0)
    m.update()
    for i, j in np.ndindex(h_Traffic.shape):
        if Gnpy[i, j] == 1:
            m.addConstr(h_Traffic[i,j] == h_Traffic_Out[i,j], name="TRAFFIC_OUT_eq_i%d_j%d" % (i, j))

    Z_Table = np.zeros((embG.shape[1], embG.shape[2], DelayTable.shape[0] - 1), dtype=object)

    for i, j, s in np.ndindex(Z_Table.shape):
        if Gnpy[i, j] == 1:
            Z_Table[i, j, s] = m.addVar(name="Z_i%d_j%d_s%d" % (i,j,s), vtype=GRB.BINARY)

    Delay = np.zeros(h_Traffic.shape, dtype=object)

    for i, j in np.ndindex(Delay.shape):
        if Gnpy[i, j] == 1:
            Delay[i, j] = m.addVar(name="Delay_i%d_j%d" % (i,j), vtype=GRB.SEMICONT, lb=0.0)

    S_Table = np.zeros(Z_Table.shape, dtype=object)

    for i, j, s in np.ndindex(S_Table.shape):
        if Gnpy[i, j] == 1:
            S_Table[i, j, s] = m.addVar(lb=0.0, ub=1.0, name="S_i%d_j%d_s%d" % (i,j,s), vtype=GRB.SEMICONT)

    FlowLinkDelay = np.zeros(embG.shape, dtype=object)

    for f, i, j in np.ndindex(embG.shape):
        if Gnpy[i, j] == 1:
            FlowLinkDelay[f, i, j] = m.addVar(name="FlowLinkDelay_f%d_i%d_j%d" % (f,i,j), vtype=GRB.CONTINUOUS)

    # Current delay of a flow
    FlowDelay = np.zeros(embG.shape[0], dtype=object)
    for f in range(FlowDelay.shape[0]):
        FlowDelay[f] = m.addVar(name="FlowDelay_f%d" % (f), vtype=GRB.SEMICONT, lb=0.0)

    m.update()

    #
    # Calculate delay for a link depending on its current throughput
    #
    for i, j in np.ndindex(Z_Table.shape[:2]):
        if Gnpy[i, j] == 1:
            m.addConstr(quicksum(Z_Table[i,j].flatten()) == 1, name="sum_DelayTable_i%d_j%d" % (i, j))

    for i, j, s in np.ndindex(S_Table.shape):
        if Gnpy[i, j] == 1:
            m.addConstr(S_Table[i, j, s] <= Z_Table[i, j, s], name="S_leq_Z_i%d_j%d_s%d" % (i, j, s))

    for i, j in np.ndindex(Delay.shape):
        if Gnpy[i, j] == 1:
            expr = LinExpr()
            for z in range(DelayTable.shape[0] - 1):
                expr += (Z_Table[i,j,z] * DelayTable[z,0]) + ((DelayTable[z+1,0] - DelayTable[z,0]) * S_Table[i,j,z])
            m.addConstr(h_Traffic[i,j] == expr, name="ZS_TP_i%d_j%d" % (i,j))

    for i, j in np.ndindex(Delay.shape):
        if Gnpy[i, j] == 1:
            expr = LinExpr()
            for z in range(DelayTable.shape[0] - 1):
                expr += (Z_Table[i,j,z] * DelayTable[z,1]) + ((DelayTable[z+1,1] - DelayTable[z,1]) * S_Table[i,j,z])
            m.addConstr(Delay[i,j] == expr, name="ZS_Delay_i%d_j%d" % (i, j))

    m.update()

    max_delay = 100000

    #
    # Calculate delay per flow
    #
    for f in range(embG.shape[0]):
        d = LinExpr()
        for i in range(embG.shape[1]):
            for j in range(embG.shape[2]):
                if Gnpy[i, j] == 1:
                    # RTT delay
                    expr = (Delay[i,j] + Delay[j,i])

                    U = max_delay

                    m.addConstr(0 <= FlowLinkDelay[f,i,j])
                    m.addConstr(FlowLinkDelay[f,i,j] <= U * embG[f,i,j])
                    m.addConstr(0 <= expr - FlowLinkDelay[f,i,j])
                    m.addConstr(expr - FlowLinkDelay[f,i,j] <= U * (1 - embG[f,i,j]))

                    d += FlowLinkDelay[f,i,j]

        m.addConstr(FlowDelay[f] == d)
        m.addConstr(Td[f] >= FlowDelay[f])

    # Max-Min Fairness Constrain
    for a in range(app_cnt):
        m.addConstr(MOS_apps[a] >= MOS_min, name="MOS_a%i_geq" % a)

    m.update()

    return m, MOS_apps, MOS_min, T, Td, A_UTIL, A_TP, A_DELAY, FlowDelay, embG, Delay, h_Traffic_Out

def grb_np_save(outdir, objs, conv_func=grb_ndarr_py):

    for fname, arr in objs.items():
        np.save(pjoin(outdir, fname), conv_func(arr))

def solved_summary(m):

    solved = {'grb_numVars': m.numVars,
              'grb_objVal': m.objVal,
              'grb_NumConstrs': m.NumConstrs,
              'grb_NumSOS': m.NumSOS,
              'grb_NumQConstrs': m.NumQConstrs,
              'grb_NumIntVars': m.NumIntVars,
              'grb_NumBinVars': m.NumBinVars,
              'grb_ObjBound': m.ObjBound,
              'grb_ObjBoundC': m.ObjBoundC,
              'grb_MIPGap': m.MIPGap,
              'grb_Status': m.Status,
              'grb_IsMIP': m.IsMIP,
              'grb_IsQP': m.IsQP,
              'grb_IsQCP': m.IsQCP
              }

    return solved

def solve_stage_first(outdir, Gnpy, init_embG, flows, UTIL, UTIL_TP, UTIL_DELAY, C,
                      DelayTable, time_limit=300, no_grb_print=False,
                      flow_types=None):

    from gurobipy import GRB

    os.makedirs(outdir, exist_ok=True)

    grb_np_save(outdir, {
                'in_flows.npy': np.array(flows),
                'in_UTIL.npy': UTIL,
                'in_UTIL_DELAY.npy': UTIL_DELAY,
                'in_UTIL_TP.npy': UTIL_TP,
                'in_Gnpy.npy': Gnpy,
                'in_C.npy': C,
                'in_DelayTable.npy': DelayTable},
                conv_func=lambda x: x)

    start = time.time()

    # Build the model
    m, MOS_apps, MOS_min, T, Td, A_UTIL, \
    A_TP, A_DELAY, FlowDelay, embG, Delay, h_Traffic_Out \
        = build_model(Gnpy, init_embG, flows, UTIL, UTIL_TP, UTIL_DELAY,
                      C, DelayTable, flow_types=flow_types)

    m.update()

    """
    First Stage
    (maximize minimum utility)
    """

    mb_duration = time.time() - start

    log.debug("Building model took %.1f seconds." % mb_duration)

    m.setObjective(MOS_min, GRB.MAXIMIZE)

    m.update()

    m.write(pjoin(outdir, "model.lp"))

    if no_grb_print:
        m.setParam('OutputFlag', False)

    m.setParam('TimeLimit', float(time_limit))

    start = time.time()

    log.debug("Solving first stage (time_limit: %.1fs).." % float(time_limit))

    m.optimize()

    opt_duration = time.time() - start

    if m.status == GRB.INFEASIBLE:

        log.fatal("Failed to solve model! GRB.INFEASIBLE !!")

        try:
            log.fatal("Writing IIS to model.ilp...")
            m.computeIIS()
            m.write(pjoin(outdir, "model.ilp"))
        except:
            log.fatal("Failed to calculate IIS !!")

        raise Exception("GRB.INFEASIBLE !!")

        #return m.status

    elif m.status == GRB.TIME_LIMIT:

        log.warning("The model could not be solved optimally in the given time!")
        log.warning("The best known solution is saved.")

    elif m.status == GRB.OPTIMAL:

        log.info("Solved first stage! status = GRB.OPTIMAL")
    else:
        raise Exception("Unknown solver status %d !!" % m.status)

    m.write(pjoin(outdir, "model.sol"))

    grb_np_save(outdir,
                {'out_A_UTIL.npy': A_UTIL,
                 'out_MOS_apps.npy': MOS_apps,
                 'out_FlowDelay.npy': FlowDelay,
                 'out_embG.npy': embG,
                 'out_Delay.npy': Delay,
                 'out_h_Traffic_Out.npy': h_Traffic_Out})

    solved = solved_summary(m)

    solved.update({'model_building_duration': mb_duration,
                   'optimization_duration': opt_duration,
                   'min_utility': float(MOS_min.x),
                   'time_limit': time_limit})

    with open(pjoin(outdir, "solved.json"), "w") as f:
        json.dump(solved, f, indent=4, sort_keys=True)

    return solved


def solve_stage_second(outdir, Gnpy, init_embG, flows, UTIL, UTIL_TP, UTIL_DELAY, C,
                       DelayTable, time_limit=300, no_grb_print=False,
                       flow_types=None, MOS_min_lb=1.0):

    from gurobipy import quicksum, GRB

    log.info("Proceeding to second step with MOS_min_lb=%.1f" % MOS_min_lb)

    grb_np_save(outdir, {
                'in_flows.npy': np.array(flows),
                'in_UTIL.npy': UTIL,
                'in_UTIL_DELAY.npy': UTIL_DELAY,
                'in_UTIL_TP.npy': UTIL_TP,
                'in_Gnpy.npy': Gnpy,
                'in_C.npy': C,
                'in_DelayTable.npy': DelayTable},
                conv_func=lambda x: x)

    start = time.time()

    # Build the second-stage model
    m, MOS_apps, MOS_min, T, Td, A_UTIL, \
    A_TP, A_DELAY, FlowDelay, embG, Delay, h_Traffic_Out \
        = build_model(Gnpy, init_embG, flows, UTIL, UTIL_TP, UTIL_DELAY,
                      C, DelayTable, flow_types=flow_types,
                     MOS_min_lb=MOS_min_lb)

    mb_duration = time.time() - start

    log.debug("Building model took %.1f seconds." % mb_duration)

    m.update()

    log.debug("MOS_min: lb=%.1f, ub=%.1f"
              % (MOS_min.lb, MOS_min.ub))

    h_obj_util_sum = m.addVar(vtype=GRB.SEMICONT, name="h_obj_util_sum")

    m.update()

    m.addConstr(h_obj_util_sum == quicksum(MOS_apps), name="h_obj_util_sum_eq")

    m.update()

    m.setObjective(h_obj_util_sum + MOS_min, GRB.MAXIMIZE)

    m.update()

    m.write(pjoin(outdir, "model.lp"))

    start = time.time()

    log.debug("Solving second-stage model (time_limit: %.1fs).." % float(time_limit))

    m.optimize()

    opt_duration = time.time() - start

    if m.status == GRB.INFEASIBLE:
        raise Exception("Second stage failed!")
    elif m.status == GRB.TIME_LIMIT:
        log.warning("Time limit for second stage reached!")
    elif m.status == GRB.OPTIMAL:
        log.info("Second stage solved OPTIMAL in %.1fs!" % opt_duration)
    else:
        raise Exception("Unknown solver status %d !!" % m.status)

    m.write(pjoin(outdir, "model.sol"))

    grb_np_save(pjoin(outdir),
                {'out_A_UTIL.npy': A_UTIL,
                 'out_MOS_apps.npy': MOS_apps,
                 'out_FlowDelay.npy': FlowDelay,
                 'out_embG.npy': embG,
                 'out_Delay.npy': Delay,
                 'out_h_Traffic_Out.npy': h_Traffic_Out})

    solved = solved_summary(m)

    solved.update({'model_building_duration': mb_duration,
                   'optimization_duration': opt_duration,
                   'min_utility': float(MOS_min.x),
                   'time_limit': time_limit})

    with open(pjoin(outdir, "solved.json"), "w") as f:
        json.dump(solved, f, indent=4, sort_keys=True)

    return solved


def solve(outdir, Gnpy, init_embG, flows, UTIL, UTIL_TP, UTIL_DELAY, C,
          DelayTable, time_limit=300, no_grb_print=False,
          flow_types=None, epsilon=0.3):
    """
    Solve the model for the given input parameters.

    :param outdir:
    :param Gnpy:
    ...

    """

    start = time.time()

    log.debug("Using flow types: %s" % flow_types)

    solved = solve_stage_first(pjoin(outdir, "stage_first"), Gnpy, init_embG,
                               flows, UTIL, UTIL_TP, UTIL_DELAY, C, DelayTable,
                               time_limit=time_limit, no_grb_print=no_grb_print,
                               flow_types=flow_types)

    log.debug("Solving second stage with epsilon: %.1f." % epsilon)

    solve_stage_second(outdir, Gnpy, init_embG, flows, UTIL, UTIL_TP,
                       UTIL_DELAY, C, DelayTable, time_limit=time_limit,
                       no_grb_print=no_grb_print, flow_types=flow_types,
                       MOS_min_lb=max(1.0, solved['min_utility'] - epsilon))

    log.debug("Total solving time: %.1fs" % (time.time() - start))

    return True


if __name__ == "__main__":

    import networkx as nx
    from networkx.readwrite import json_graph

    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(1, 3)
    G.add_edge(2, 4)
    G.add_edge(3, 4)
    G.add_edge(4, 5)

    with open(pjoin("out", "G.json"), "w") as f:
        f.write(json.dumps(json_graph.node_link_data(G)))

    flows = [(0, 5), (5, 0)]
    #flows = [(0, 5)] * 2
    #flows_tp_st = [6, 6]
    #flows_tp_ts = [4, 4]

    UTIL_BASE = np.array([[3, 3, 3, 2, 1],
                         [4, 3, 3, 2, 2],
                         [4, 4, 3, 3, 3],
                         [4, 4, 3, 3, 3],
                         [5, 4, 4, 3, 3]])

    dis_cnt = UTIL.shape[0]

    app_cnt = len(flows)

    # Generic 2D utility function
    #UTIL = np.zeros((dis_cnt, dis_cnt))
    #it = np.nditer(UTIL, flags=['multi_index'])
    #while not it.finished:
    #    i, j = it.multi_index
    #    UTIL[i, j] = ((UTIL.shape[0] - i) + (UTIL.shape[0] - j)) / (UTIL.shape[0] + UTIL.shape[1] - 1) * 5
    #    it.iternext()

    # Delay and throughput vector for utility function
    UTIL_DELAY = np.linspace(5, 300, dis_cnt)
    UTIL_TP = np.linspace(10, 30, dis_cnt)

    #A_MOS_T = np.zeros((len(flows), dis_cnt, 3))

    #for a in range(A_MOS_T.shape[0]):
    #    A_MOS_T[a,:,0] = np.linspace(1, 5, dis_cnt) # MOS
    #    A_MOS_T[a,:,1] = np.linspace(1, 10, dis_cnt) # data-rate
    #    A_MOS_T[a,:,2] = [500] * dis_cnt # delay

    #delay_dis_cnt = 6
    #delay_approx = np.zeros((delay_dis_cnt, 2))
    #delay_approx[:,0] = np.linspace(0.1, 1.0, delay_dis_cnt)
    #delay_approx[:,1] = np.linspace(15, 500, delay_dis_cnt)

    delay_dis_cnt = 10
    DelayTable = np.zeros((delay_dis_cnt, 2))

    DelayTable[:,0] = np.linspace(0, 100, delay_dis_cnt) # data-rate
    DelayTable[:,1] = np.linspace(0.1, 1, delay_dis_cnt) # delay

    assert(DelayTable[:,0].max() > UTIL_TP.max())


    #TODO: Delay constrained should say which utilization at which
    # device causes how much extra delay.

    Gnpy = np.zeros((len(G.nodes()), len(G.nodes())))

    for i, j in np.ndindex(Gnpy.shape):
        if i in G[j]:
            Gnpy[i, j] = 1

    C = np.ones(Gnpy.shape) * 1000

    solve("out", Gnpy, flows, UTIL, UTIL_DELAY, UTIL_TP, C, DelayTable)
