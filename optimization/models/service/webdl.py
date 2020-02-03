#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.neighbors import KNeighborsRegressor
from service.base import ServiceInterface
from service.tools import plot_service_model, plot_service_values

#%%

class WebDLServiceLinear(ServiceInterface):

    METHOD = "KNN"

    def __init__(self, X, y):

        self.X = X
        self.y = y

        self._regr = linear_model.LinearRegression()
        self._regr.fit(X, y)

    def predict(self, tp, delay):

        x = np.array([tp, delay]).reshape(1, -1)

        return self._regr.predict(x)

class WebDLServiceKNN(ServiceInterface):

    METHOD = "KNN"

    def __init__(self, X, y):

        self.X = X
        self.y = y

        self._regr = KNeighborsRegressor(n_neighbors=10)
        self._regr.fit(X, y)

    def predict(self, tp, delay):

        x = np.array([tp, delay]).reshape(1, -1)

        return self._regr.predict(x)

#WebService = WebDLServiceLinear
WebDLService = WebDLServiceKNN

#%%

if __name__ == "__main__":

    df = pd.read_csv("data/webdl.csv")
    X = df[['cfg_server_maxrate_kbit', 'cfg_delay']]
    y = df.webdlc_median

    zlabel = r"Median Download Time (s)"

    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():20j,
                     X.iloc[:,1].min():X.iloc[:,1].max():20j]

    x1, y1 = mgrid

    #%%

    from scipy.interpolate import griddata

    z_cubic = griddata(X, y, (x1, y1), method='cubic')

    vmin = 0
    vmax = 200

    plot_service_model(x1, y1, z_cubic, zlabel, "Data (Cubic Interpolation)",
                       vmin=vmin, vmax=vmax, fn="service_data_webdl.png",
                       datapoints=X)

    #%%

    service_model = WebDLService(X, y)

    z_pred = np.zeros(x1.shape)

    for i in np.ndindex(x1.shape):
        z_pred[i] = service_model.predict(x1[i], y1[i])

    plot_service_model(x1, y1, z_pred, zlabel, "Predicted (%s)" % service_model.METHOD,
                       vmin=vmin, vmax=vmax, fn="service_pred_webdl.png",
                       datapoints=X)

    #%% Data
    plot_service_values(X, y, zlabel, "Data (Raw)",
                        vmin=vmin, vmax=vmax, fn="service_values_webdl.png")