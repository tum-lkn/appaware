#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt
import pandas as pd
import numpy as np

def plot_service_model(x1, y1, z, zlabel, title, vmin=None, vmax=None, fn=None, datapoints=None):

    f, ax = _plot_service_model(x1, y1, z, zlabel, title, 
                                vmin=vmin, vmax=vmax, fn=None)

    if datapoints is not None:
        ax.scatter(datapoints.iloc[:,0], datapoints.iloc[:,1], 
                   marker="+", alpha=0.5)

    if fn:
        f.savefig(fn, dpi=200)
    
def _plot_service_model(x1, y1, z, zlabel, title, vmin=None, vmax=None, fn=None):

    f, ax = plt.subplots()
    
    plt.title(title)

    cmap=plt.cm.get_cmap('gist_heat_r')
    #plt.set_cmap()

    ims = ax.imshow(z.T, cmap=cmap,
                    origin='lower',
                    extent=[x1.min(), x1.max(), y1.min(), y1.max()],
                    aspect='auto',
                    vmin=vmin, vmax=vmax)

    ax.set_xlabel("Throughput (kbps)")
    ax.set_ylabel("Delay(ms)")

    ax.set_xlim([x1.min(), x1.max()])
    ax.set_ylim([y1.min(), y1.max()])

    cb = plt.colorbar(ims)
    cb.set_label(zlabel, rotation=270)
    cb.ax.get_yaxis().labelpad = 15    
    
    return f, ax
    
def plot_service_values(X, y, zlabel, title, vmin=None, vmax=None, fn=None):
    
    f, ax = plt.subplots()
    
    cmap = plt.cm.get_cmap('gist_heat_r')
    
    sc = plt.scatter(X.iloc[:,0], X.iloc[:,1],
                     c=y.values, vmin=vmin, vmax=vmax,
                     cmap=cmap, marker="s", s=140, 
                     linewidth=1, edgecolor='black', alpha=.8)
    
    ax.set_xlim([X.iloc[:,0].min(), X.iloc[:,0].max()])
    ax.set_ylim([X.iloc[:,1].min(), X.iloc[:,1].max()])
    
    plt.title(title)
    
    cb = plt.colorbar(sc)
    cb.set_label(zlabel, rotation=270)
    cb.ax.get_yaxis().labelpad = 15    
        
    ax.grid(True, alpha=0.2)    
    
    if fn:
        f.savefig(fn, dpi=200)

if __name__ == "__main__":
    
    df = pd.read_csv("data/webdl.csv")
    X = df[['cfg_server_maxrate_kbit', 'cfg_delay']]
    y = df.webdlc_median

    zlabel = r"Median Download Time (s)"

    mgrid = np.mgrid[X.iloc[:,0].min():X.iloc[:,0].max():30j,
                     X.iloc[:,1].min():X.iloc[:,1].max():30j]

    x1, y1 = mgrid

    #%%

    from scipy.interpolate import griddata

    z_cubic = griddata(X, y, (x1, y1), method='cubic')

    vmin = 0
    vmax = 200

    plot_service_model(x1, y1, z_cubic, zlabel, "Data (Cubic Interpolation)",
                       vmin=vmin, vmax=vmax,
                       datapoints=X)
    
    #%%
    plot_service_values(X, y, r"Median Download Time (s)", "Data", 0, 200)
    