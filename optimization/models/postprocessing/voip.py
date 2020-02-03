#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from utility.voip import VoIPUtility
from service.voip import VoIPService
from postprocessing.tools import utility_grid, plot_utility_model, save_model
from postprocessing.cfg import *

if __name__ == "__main__":

    service_model = VoIPService(None, None)


    # Unscaled

    utility_model = VoIPUtility()

    tp,delay,utility = utility_grid(service_model, utility_model,
                                    discrete_delay_cnt=glb_discrete_delay_cnt,
                                    discrete_tp_cnt=glb_discrete_tp_cnt,
                                    max_delay=service_model.max_delay,
                                    min_delay=service_model.min_delay,
                                    min_tp=glb_min_tp,
                                    max_tp=service_model.max_tp)

    plot_utility_model(tp, delay, utility)
    save_model("postprocessing/models_unscaled/", "voip", tp, delay, utility)

    # Scaled

    utility_model = VoIPUtility(scaled=True)

    tp,delay,utility = utility_grid(service_model, utility_model,
                                    discrete_delay_cnt=glb_discrete_delay_cnt,
                                    discrete_tp_cnt=glb_discrete_tp_cnt,
                                    max_delay=service_model.max_delay,
                                    min_delay=service_model.min_delay,
                                    min_tp=glb_min_tp,
                                    max_tp=service_model.max_tp)

    plot_utility_model(tp, delay, utility)
    save_model("postprocessing/models/", "voip", tp, delay, utility)