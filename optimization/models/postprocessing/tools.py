#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pylab as plt

def utility_grid(service_model, utility_model,
                 discrete_tp_cnt=20,
                 discrete_delay_cnt=100,
                 min_tp=100,
                 max_tp=8000,
                 min_delay=10,
                 max_delay=300):

    discrete_tp_cnt = complex(0, discrete_tp_cnt)
    discrete_delay_cnt = complex(0, discrete_delay_cnt)

    mgrid = np.mgrid[min_tp:max_tp:discrete_tp_cnt,
                     min_delay:max_delay:discrete_delay_cnt]

    x1, y1 = mgrid

    z1 = np.zeros(x1.shape)

    for i in np.ndindex(x1.shape):
        service_kpis = service_model.predict(x1[i], y1[i])
        z1[i] = utility_model.predict(*service_kpis)

    return x1, y1, z1


def plot_utility_model(x1, y1, z1, fn=None):

    f, ax = plt.subplots()

    cmap=plt.cm.get_cmap('RdYlGn')

    vmin=1
    vmax=5

    ims = ax.imshow(z1.T, cmap=cmap,
                    origin='lower', aspect='auto', vmin=vmin, vmax=vmax,
                    extent=[x1.min(), x1.max(), y1.min(), y1.max()])

    ax.scatter(x1.flatten(), y1.flatten(), marker="+", color='black')

    ax.set_xlabel("Throughput (kbps)")
    ax.set_ylabel("Delay(ms)")

    cb = plt.colorbar(ims)
    cb.set_label("Utility", rotation=270)


    minmax = [(z1.max()-vmin)/(vmax-vmin),
              (z1.min()-vmin)/(vmax-vmin)]
    for v in minmax:
        cb.ax.plot([0, 1], [v]*2, 'black')

    if fn:
        f.savefig(fn, dpi=200)
        plt.close()


def save_model(folder, name, tp, delay, utility):

    os.makedirs(folder, exist_ok=True)

    U_TP = tp[:,0]
    U_D = delay[0,:]
    U = utility

    np.save(os.path.join(folder, "model_%s_U.npy" % name), U)
    np.save(os.path.join(folder, "model_%s_TP.npy" % name), U_TP)
    np.save(os.path.join(folder, "model_%s_D.npy" % name), U_D)

    plot_utility_model(tp, delay, utility, os.path.join(folder, "model_%s.png" % name))


if __name__ == "__main__":

    import pandas as pd
    from utility.ssh import SSHUtility
    from service.ssh import SSHService

    df = pd.read_csv("service/data/ssh.csv")
    X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
    y = df.sshc_median

    service_model = SSHService(X, y)
    utility_model = SSHUtility()

    tp,delay,utility = utility_grid(service_model, utility_model,
                                    discrete_delay_cnt=15,
                                    discrete_tp_cnt=15,
                                    max_delay=service_model.max_delay,
                                    min_delay=service_model.min_delay,
                                    min_tp=service_model.min_tp,
                                    max_tp=service_model.max_tp)