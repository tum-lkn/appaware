#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from utility.webdl import WebDLUtility
from service.webdl import WebDLService
from postprocessing.tools import plot_utility_model, utility_grid, save_model
from postprocessing.cfg import *

#%%

df = pd.read_csv("service/data/webdl.csv")
X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
y = df.webdlc_median

service_model = WebDLService(X, y)

# Unscaled

utility_model = WebDLUtility()

tp,delay,utility = utility_grid(service_model, utility_model,
                                discrete_delay_cnt=glb_discrete_delay_cnt,
                                discrete_tp_cnt=glb_discrete_tp_cnt,
                                max_delay=service_model.max_delay,
                                min_delay=service_model.min_delay,
                                min_tp=glb_min_tp,
                                max_tp=service_model.max_tp)

plot_utility_model(tp, delay, utility)
save_model("postprocessing/models_unscaled/", "webdl", tp, delay, utility)

# Scaled

utility_model = WebDLUtility(scaled=True)

tp,delay,utility = utility_grid(service_model, utility_model,
                                discrete_delay_cnt=glb_discrete_delay_cnt,
                                discrete_tp_cnt=glb_discrete_tp_cnt,
                                max_delay=service_model.max_delay,
                                min_delay=service_model.min_delay,
                                min_tp=glb_min_tp,
                                max_tp=service_model.max_tp)

plot_utility_model(tp, delay, utility)
save_model("postprocessing/models/", "webdl", tp, delay, utility)
