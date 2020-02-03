#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn import linear_model
from service.base import ServiceInterface
from service.tools import plot_service_model, plot_service_values


class SSHService(ServiceInterface):

    def __init__(self, X, y):

        self.X = X
        self.y = y

        self._regr = linear_model.LinearRegression()
        self._regr.fit(X, y)

    @property
    def max_tp(self):
        return 500

    @property
    def min_tp(self):
        return 100

    def predict(self, tp, delay):

        # Set tp to 2000 Kbps.
        # The model was only tested with 2000 Kbps.
        
        x = np.array([tp, delay]).reshape(1, -1)

        return self._regr.predict(x)

#%%

if __name__ == "__main__":

    df = pd.read_csv("data/ssh.csv")
    X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
    y = df.sshc_median

    service_model = SSHService(X, y)

    #%%

    zlabel = r"Response Time $rt$ (s)"

    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():50j,
                     X.iloc[:,1].min():X.iloc[:,1].max():50j]

    x1, y1 = mgrid

    #%%

    vmin = 0
    vmax = 1.5

    from scipy.interpolate import griddata

    z_cubic = griddata(X, y, (x1, y1), method='cubic')

    #plot_service_model(x1, y1, z_cubic, zlabel, "Data (Cubic Interpolation)",
     #                  vmin=vmin, vmax=vmax, fn="service_data_ssh.png",
      #                 datapoints=X)

    #%%

    z_pred = np.zeros(x1.shape)

    for i in np.ndindex(x1.shape):
        z_pred[i] = service_model.predict(x1[i], y1[i])

    #%%
    plot_service_model(x1, y1, z_pred, zlabel, "Predicted (Linear Regr.)",
                       vmin=vmin, vmax=vmax, fn="service_pred_ssh.png",
                       datapoints=X)

    #%% Data
    plot_service_values(X, y, zlabel, "Data (Raw)",
                        vmin=vmin, vmax=vmax, 
                        fn="service_values_ssh.png")