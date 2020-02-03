#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sklearn import linear_model
from sklearn.neighbors import KNeighborsRegressor
from service.base import ServiceInterface
from service.tools import plot_service_model, plot_service_values

#%%

class WebServiceLinear(ServiceInterface):

    METHOD = "Linear"

    def __init__(self, X, y):

        self.X = X
        self.y = y

        self._regr = linear_model.LinearRegression()
        self._regr.fit(X, y)

    def predict(self, tp, delay):

        x = np.array([tp, delay]).reshape(1, -1)

        return self._regr.predict(x)

class WebServiceKNN(ServiceInterface):

    METHOD = "KNN"

    def __init__(self, X, y):

        self.X = X
        self.y = y

        self._regr = KNeighborsRegressor(n_neighbors=4)
        self._regr.fit(X, y)

    def predict(self, tp, delay):

        x = np.array([tp, delay]).reshape(1, -1)

        return self._regr.predict(x)

#WebService = WebServiceLinear
WebService = WebServiceKNN

#%%

if __name__ == "__main__":


    df = pd.read_csv("data/web.csv")


    X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
    y = df.webc_median_domEnd / 1000

    service_model = WebService(X, y)

    zlabel = r"Median domEnd Time (s)"

    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():30j,
                     X.iloc[:,1].min():X.iloc[:,1].max():30j]

    x1, y1 = mgrid

    #%% Cubic

    from scipy.interpolate import griddata

    z_cubic = griddata(X, y, (x1, y1), method='cubic')

    vmin = 1
    vmax = 17

    plot_service_model(x1, y1, z_cubic, zlabel, "Data (Cubic Interpolation)",
                       vmin=vmin, vmax=vmax, fn="service_data_web.png",
                       datapoints=X)
    #%% KNN

    z_pred = np.zeros(x1.shape)

    for i in np.ndindex(x1.shape):
        z_pred[i] = service_model.predict(x1[i], y1[i])

    plot_service_model(x1, y1, z_pred, zlabel, "Predicted (%s)" % service_model.METHOD,
                       vmin=vmin, vmax=vmax, fn="service_pred_web.png",
                       datapoints=X)

    #%% Data
    plot_service_values(X, y, zlabel, "Data (Raw)",
                        vmin=vmin, vmax=vmax, fn="service_values_web.png")
