#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn import linear_model
from service.base import ServiceInterface
from service.tools import plot_service_model, plot_service_values


class VoIPService(ServiceInterface):

    def __init__(self, X, y):
        pass
#FIXME: y has three features (jitter, delay, packet_loss).
#       Linear regression will not work here.
# - jitter: Unknown, this we should predict probably
# - delay: Known, we set it, and the tool estimates it
# - packet_loss: Should be always zero

    @property
    def max_tp(self):
        return 500

    @property
    def min_tp(self):
        return 100

    @property
    def max_delay(self):
        return 500

    @property
    def min_delay(self):
        return 0

    def predict(self, tp, delay):

        #x = np.array([tp, delay]).reshape(1, -1)
        #print(x)

        # jitter, delay, packet_loss
        return 0, delay, 0.0

#%%

if __name__ == "__main__":

    #df = pd.read_csv("data/voip.csv")
    #X = df[['cfg_client_maxrate_kbit', 'cfg_delay']]
    #y = [['jitter', 'delay', 'packet_loss']]

    result = []

    delays = np.linspace(0, 600,40)
    rates = np.linspace(250,5000,20)
    packet_losses = np.linspace(0,0,1)

    d = {'cfg_client_maxrate_kbit' : [],'cfg_delay': []}
    temp = {'mos': []}
    df = pd.DataFrame(data=d)
    y = pd.DataFrame(data=temp)

    for d in range(0,len(delays)-1):
        for r in range(0,len(rates)-1):
            df = df.append({'cfg_client_maxrate_kbit': rates[r], 'cfg_delay': delays[d]}, ignore_index=True)
            result.append(voip_mos.predict(delays[d],0))
            y=y.append({'mos': voip_mos.predict(delays[d],0)}, ignore_index=True)


    vmin = 1
    vmax = 5


    service_model = VoIPService(X, y)

    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():19j,
                     X.iloc[:,1].min():X.iloc[:,1].max():19j]

    y=y.mos
    x1, y1 = mgrid

    zlabel='MOS'
    plot_service_values(X, y, zlabel, "Data (Raw)",
                        vmin=vmin, vmax=vmax, fn="service_values_voip.png")





    #plot_service_model()

#    #%%
#
#    zlabel = r"Response Time $rt$ (s)"
#
#    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():50j,
#                     X.iloc[:,1].min():X.iloc[:,1].max():50j]
#
#    x1, y1 = mgrid
#
#    #%%
#
#    vmin = 0
#    vmax = 1.5
#
#    from scipy.interpolate import griddata
#
#    z_cubic = griddata(X, y, (x1, y1), method='cubic')
#
#    #plot_service_model(x1, y1, z_cubic, zlabel, "Data (Cubic Interpolation)",
#     #                  vmin=vmin, vmax=vmax, fn="service_data_ssh.png",
#      #                 datapoints=X)
#
#    #%%
#
#    z_pred = np.zeros(x1.shape)
#
#    for i in np.ndindex(x1.shape):
#        z_pred[i] = service_model.predict(x1[i], y1[i])
#
#    #%%
#    plot_service_model(x1, y1, z_pred, zlabel, "Predicted (Linear Regr.)",
#                       vmin=vmin, vmax=vmax, fn="service_pred_ssh.png",
#                       datapoints=X)
#
#    #%% Data
#    plot_service_values(X, y, zlabel, "Data (Raw)",
#                        vmin=vmin, vmax=vmax,
#                        fn="service_values_ssh.png")