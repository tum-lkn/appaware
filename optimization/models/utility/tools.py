#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pylab as plt

def mos_grid(service_model, mos_model,
             discrete_delay_cnt=100,
             discrete_tp_cnt=20,
             min_tp=100,
             max_tp=8000,
             min_delay=10,
             max_delay=300):

    discrete_delay_cnt = complex(0, discrete_delay_cnt)
    discrete_tp_cnt = complex(0, discrete_tp_cnt)

    mgrid = np.mgrid[min_delay:max_delay:discrete_delay_cnt,
                     min_tp:max_tp:discrete_tp_cnt]

    x1, y1 = mgrid

    z1 = np.zeros(x1.shape)

    for i in np.ndindex(x1.shape):
        z1[i] = mos_model.predict(service_model.predict(x1[i], y1[i]))

    return x1, y1, z1

def plot_mos_model(x1, y1, z1):

    f, ax = plt.subplots()

    cmap=plt.cm.get_cmap('RdYlGn')

    ims = ax.imshow(z1.T, cmap=cmap,
                    origin='lower', aspect='auto',
                    extent=[x1.min(), x1.max(), y1.min(), y1.max()])

    ax.set_xlabel("Delay(ms)")
    ax.set_ylabel("Throughput (kbps)")

    cb = plt.colorbar(ims)
    cb.set_label("MOS", rotation=270)


if __name__ == "__main__":

    from utility.ssh import ssh_service_model, ssh_mos_model

    x1, y1, z1 = mos_grid(ssh_service_model(), ssh_mos_model())

    plot_mos_model(x1, y1, z1)