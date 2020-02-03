#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from utility.video import VideoUtility
from service.video import VideoService
from postprocessing.tools import plot_utility_model, utility_grid, save_model
from postprocessing.cfg import *


#%% live streaming

df = pd.read_csv("../service/data/metrics_dash_1sec.csv")
X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
y = df.mean_ql_mean

service_model = VideoService(X, y)

# Unscaled

utility_model = VideoUtility()

tp,delay,utility = utility_grid(service_model, utility_model,
                                discrete_delay_cnt=glb_discrete_delay_cnt,
                                discrete_tp_cnt=glb_discrete_tp_cnt,
                                max_delay=service_model.max_delay,
                                min_delay=service_model.min_delay,
                                min_tp=750,
                                max_tp=service_model.max_tp)

plot_utility_model(tp, delay, utility)
save_model("postprocessing/models_unscaled/", "video_live", tp, delay, utility)

# Scaled

utility_model = VideoUtility(scaled=True)

tp,delay,utility = utility_grid(service_model, utility_model,
                                discrete_delay_cnt=glb_discrete_delay_cnt,
                                discrete_tp_cnt=glb_discrete_tp_cnt,
                                max_delay=service_model.max_delay,
                                min_delay=service_model.min_delay,
                                min_tp=750,
                                max_tp=service_model.max_tp)

plot_utility_model(tp, delay, utility)
save_model("postprocessing/models/", "video_live", tp, delay, utility)
