#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

# Maximum Delay (in s)
max_D = 10

if __name__ == "__main__":

    # Utilization limits in percent.
    # Every utilization higher is
    # set to max_D.
    limits  = [99, 95, 90, 85, 80]

    util = np.linspace(0, 1, 20)

    delay = np.zeros(util.shape)

    for l in limits:
        delay[util>(l/100)] = max_D
        np.save("max%dperc.npy" % l, np.array((util, delay)))

    # Static delay of 2ms
    delay[:] = 0.002

    np.save("2ms.npy", np.array((util, delay)))