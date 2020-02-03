#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from utility.web import WebUtility
from service.web import WebService
from postprocessing.tools import plot_utility_model, utility_grid, save_model
from postprocessing.cfg import *

#%%


df = pd.read_csv("service/data/web.csv")

X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
y = df.webc_mean_respEnd / 1000

service_model = WebService(X, y)

# Unscaled

utility_model = WebUtility()

tp,delay,utility = utility_grid(service_model, utility_model,
                                discrete_delay_cnt=glb_discrete_delay_cnt,
                                discrete_tp_cnt=glb_discrete_tp_cnt,
                                max_delay=service_model.max_delay,
                                min_delay=service_model.min_delay,
                                min_tp=glb_min_tp,
                                max_tp=service_model.max_tp)

plot_utility_model(tp, delay, utility)
save_model("postprocessing/models_unscaled/", "web", tp, delay, utility)

# Scaled

utility_model = WebUtility(scaled=True)

tp,delay,utility = utility_grid(service_model, utility_model,
                                discrete_delay_cnt=glb_discrete_delay_cnt,
                                discrete_tp_cnt=glb_discrete_tp_cnt,
                                max_delay=service_model.max_delay,
                                min_delay=service_model.min_delay,
                                min_tp=glb_min_tp,
                                max_tp=service_model.max_tp)

plot_utility_model(tp, delay, utility)
save_model("postprocessing/models/", "web", tp, delay, utility)
