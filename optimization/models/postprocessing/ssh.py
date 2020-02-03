#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from utility.ssh import SSHUtility
from service.ssh import SSHService
from postprocessing.tools import utility_grid, plot_utility_model, save_model
from postprocessing.cfg import *

if __name__ == "__main__":

    df = pd.read_csv("service/data/ssh.csv")
    X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
    y = df.sshc_median

    service_model = SSHService(X, y)

    # Unscaled

    utility_model = SSHUtility()

    tp,delay,utility = utility_grid(service_model, utility_model,
                                    discrete_delay_cnt=glb_discrete_delay_cnt,
                                    discrete_tp_cnt=glb_discrete_tp_cnt,
                                    max_delay=service_model.max_delay,
                                    min_delay=0.0,
                                    min_tp=glb_min_tp,
                                    max_tp=service_model.max_tp)

    plot_utility_model(tp, delay, utility)
    save_model("postprocessing/models_unscaled/", "ssh", tp, delay, utility)

    # Scaled

    utility_model = SSHUtility(scaled=True)

    tp,delay,utility = utility_grid(service_model, utility_model,
                                    discrete_delay_cnt=glb_discrete_delay_cnt,
                                    discrete_tp_cnt=glb_discrete_tp_cnt,
                                    max_delay=service_model.max_delay,
                                    min_delay=0.0,
                                    min_tp=glb_min_tp,
                                    max_tp=service_model.max_tp)

    plot_utility_model(tp, delay, utility)
    save_model("postprocessing/models/", "ssh", tp, delay, utility)

