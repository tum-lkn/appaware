import numpy as np

def vf(f, i=None, j=None):
    if i is None:
        return "f%03d" % f
    elif j is None:
        return "f%03d_i%03d" % (f, i)
    else:
        return "f%03d_i%03d_j%03d" % (f, i, j)


def to_purepy(embG, solved=False):

    if solved:
        access = lambda obj: obj.x
    else:
        access = lambda obj: obj.start

    tmp = np.copy(embG)

    it = np.nditer(tmp, flags=['multi_index', 'refs_ok'])

    while not it.finished:
        c, i, j = it.multi_index
        if not isinstance(embG[c, i, j], int):
            tmp[c, i, j] = access(embG[c, i, j])
        it.iternext()

    # Convert to float array
    tmp = tmp.astype(np.float)

    return tmp

def sp_init_embG(G, Gnpy, flows):

    import networkx as nx
    import random

    init_embG = np.zeros((len(flows), *Gnpy.shape))

    #
    # Set the path to shortest path by default
    #
    for f, (from_id, to_id) in enumerate(flows):

        path = random.choice(list(nx.shortest_paths.all_shortest_paths(G, source=from_id, target=to_id)))

        for li_idx, node in enumerate(path):

            if node == to_id:
                break

            init_embG[f, node, path[(li_idx+1)]] = 1

    return init_embG

def grb_ndarr_py(grb_ndarr):

    if type(grb_ndarr) is list:
        grb_ndarr = np.array(grb_ndarr)

    ndarr = np.zeros(grb_ndarr.shape)

    it = np.nditer(grb_ndarr, flags=['multi_index', 'refs_ok'])

    while not it.finished:
        if isinstance(grb_ndarr[it.multi_index], int) or \
           isinstance(grb_ndarr[it.multi_index], float) or \
           isinstance(grb_ndarr[it.multi_index], np.int64) or \
           isinstance(grb_ndarr[it.multi_index], np.float64):
            ndarr[it.multi_index] = grb_ndarr[it.multi_index]
        else:
            try:
                ndarr[it.multi_index] = grb_ndarr[it.multi_index].x
            except:
                ndarr[it.multi_index] = np.nan

        it.iternext()

    return ndarr.astype(np.float)


def convert(embG, b_MOS_a, FlowDelay, Delay):

    py_embG = to_purepy(embG, solved=True)

    py_FlowDelay = np.zeros(FlowDelay.shape)

    for i in range(FlowDelay.shape[0]):
        py_FlowDelay[i] = FlowDelay[i].x

    py_Delay = np.zeros(Delay.shape)

    for i in range(Delay.shape[0]):
        for j in range(Delay.shape[1]):
            try:
                py_Delay[i,j] = Delay[i,j].x
            except:
                py_Delay[i,j] = np.nan

    #py_A_UTIL = np.zeros(A_UTIL.shape)
#
#    for i in range(A_UTIL.shape[0]):
#        for j in range(A_UTIL.shape[1]):
#            try:
#                py_A_UTIL[i,j] = A_UTIL[i,j].x
#            except:
#                py_A_UTIL[i,j] = np.nan

    MOS_a = []
    for a in b_MOS_a:
        mos = [np.float(x.x) for mos_idx, x in enumerate(a)]
        mos_idx = np.argmax(mos)
        MOS_a.append(mos_idx)

    return py_embG, np.array(MOS_a), py_FlowDelay, py_Delay
