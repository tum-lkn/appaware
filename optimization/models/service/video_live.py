#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sklearn import linear_model
from sklearn.neighbors import KNeighborsRegressor
from service.base import ServiceInterface
from service.tools import plot_service_model, plot_service_values
from service.video import VideoServiceKNN
from service.video import VideoServiceLinear

#%%

VideoService = VideoServiceKNN
#VideoService = VideoServiceLinear

#%%

if __name__ == "__main__":

    df = pd.read_csv("data/metrics_dash_1sec.csv")

    X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
    y = df.mean_ql_mean

    service_model = VideoService(X, y)

    zlabel = r"Mean quality level"

    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():19j,
                     X.iloc[:,1].min():X.iloc[:,1].max():19j]

    x1, y1 = mgrid

    #%%

    from scipy.interpolate import griddata

    z_cubic = griddata(X, y, (x1, y1), method='cubic')

    vmin = 1
    vmax = 5

    plot_service_model(x1, y1, z_cubic, zlabel, "Data (Cubic Interpolation)",
                       vmin=vmin, vmax=vmax, fn="service_data_video_live.png",
                       datapoints=X)

    z_pred = np.zeros(x1.shape)

    for i in np.ndindex(x1.shape):
        z_pred[i] = service_model.predict(x1[i], y1[i])

    plot_service_model(x1, y1, z_pred, zlabel, "Predicted (%s)" % service_model.METHOD,
                       vmin=vmin, vmax=vmax, fn="service_pred_video_live.png",
                       datapoints=X)

    #%% Raw values
    plot_service_values(X, y, zlabel, "Data (Raw)",
                        vmin=vmin, vmax=vmax, fn="service_values_video_live.png")