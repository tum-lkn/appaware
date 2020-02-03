#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

class VideoUtility(object):

    def __init__(self, min_quality=0.0, max_quality=5.0,
                 scaled=False, min_mos=1.0, max_mos=5.0):

        self._scaled = scaled

        self._min_mos = min_mos
        self._max_mos = max_mos

        self._min_quality = min_quality
        self._max_quality = max_quality

    def predict(self, meanql):

        temp_mos = self._predict_mos(meanql)

        if not (temp_mos >= self._min_mos and temp_mos <= self._max_mos):
            raise Exception("Invalid MOS %.5f (bounds: [%.5f, %.5f]!" % (temp_mos, self._min_mos, self._max_mos))

        if self._scaled:
            utility = np.interp(temp_mos, (self._min_mos, self._max_mos), (1, 5))
        else:
            utility = temp_mos

        return utility

    def _predict_mos(self, meanql):
        """
        Predict the utility for a mean quality level.

        At the moment just scales the input mean quality
        to the range of 1 - 5.
        """

        if meanql > self._max_quality or\
           meanql < self._min_quality:
            raise Exception("NOT: %.2f < %.2f < %.2f" % (self._min_quality, meanql,
                                                         self._max_quality))

        norm_meanql = (meanql - self._min_quality) / \
                      (self._max_quality - self._min_quality)

        return norm_meanql * 4 + 1

    def predict_segs(self, seg_qualities):
        """
        :param seg_qualities: Choosen quality levels so far
        """

        np_seg_qualities = np.array(seg_qualities)

        assert(np.sum([np_seg_qualities > self._max_quality]) == 0)
        assert(np.sum([np_seg_qualities < self._min_quality]) == 0)

        meanql = np.mean(np_seg_qualities)

        norm_meanql = (meanql - self._min_quality) / \
                      (self._max_quality - self._min_quality)

        return norm_meanql * 4 + 1

    def inverse(self, utility):
        return -1

if __name__ == "__main__":

    #seg_qualities = [2, 5, 4, 1, 4, 2, 3,1]

    video = VideoUtility(scaled=True)

    print(video.predict(0.3))

#
#class VideoMOS(object):
#
#    @staticmethod
#    def predict(thl):
#        """
#        :param thl: Time on highest layer (thl) 0 <= thl <= 1
#        """
#
#        alpha = 0.003
#        beta = 0.064
#        gamma = 2.498
#
#        return (alpha * np.exp(beta * thl) + gamma)

def mos_webdl(thl):
    return VideoMOS.predict(thl)

def webdl_mos_model():
    return VideoMOS()

def iqx_paper(thl):
    alpha = 0.003
    beta = 0.064
    gamma = 2.498
    thl = thl * 100
    return (alpha * np.exp(beta * thl) + gamma)

def iqx(x, thl):
    alpha = x[0]
    beta = x[1]
    gamma = x[2]
    return (alpha * np.exp(beta * thl) + gamma)

def scale_iqx(lower_layer_mos = 1, higher_layer_mos = 5):

    from scipy.optimize import least_squares

    def residual_iqx(x, thl, y):
        r = [iqx(x,i) - y[idx] for idx,i in enumerate(thl)]
        return np.array(r)

    min_y = iqx_paper(0)
    max_y = iqx_paper(1)

    train_x = np.linspace(1, 0)
    train_y = [(iqx_paper(x) - min_y) * ((higher_layer_mos - lower_layer_mos) / (max_y-min_y)) + lower_layer_mos for x in train_x]

    x_start = [0.003, 0.064, 1]

    res_lsq = least_squares(residual_iqx, x_start,
                            args=(train_x, train_y))

    return res_lsq


class VideoMOS(object):

    def predict(self, thl):
        """
        :param thl: Vector of Time on highest layer (thl) 0 <= thl <= 1
        """

        r = []
        for idx, tl in enumerate(thl[:-1]):
            r.append(iqx(self._mos_parameters[idx], tl))

        r_wmean = np.average(r, weights=thl[:-1])

        return r_wmean

    def predict_ql(self, qidx, tl):
        return iqx(self._mos_parameters[qidx], tl)

    def __init__(self, mos_values = np.array([5,4,3,2,1])):

        self._mos_values = mos_values
        self._mos_parameters = [0] * (mos_values.size - 1)

        for idx, (hl_mos, ll_mos) in enumerate(zip(mos_values[:-1], mos_values[1:])):
            res_lsq = scale_iqx(lower_layer_mos=ll_mos, higher_layer_mos=hl_mos)
            self._mos_parameters[idx] = res_lsq.x

def plot_example(mos_values, thl):

    vmos = VideoMOS(mos_values=mos_values)

    x = np.linspace(1, 0, 80)

    y_all = [0] * (mos_values.size - 1)

    for hl_mos_idx in range(mos_values.size - 1):
        y_all[hl_mos_idx] = [vmos.predict_ql(hl_mos_idx, i) for i in x]

    f, ax = plt.subplots()

    ax.grid()
    cmap = plt.get_cmap('copper')
    colors = iter(cmap(np.linspace(0,1,len(mos_values))))

    for hl_mos_idx, tl in zip(range(mos_values.size - 1), thl[:-1]):
        c = next(colors)
        ax.step(x, y_all[hl_mos_idx], color=c)
        mos = vmos.predict_ql(hl_mos_idx, tl)
        ax.scatter(tl, mos, color=c)

    for i, mos in enumerate(mos_values):
        ax.axhline(mos, xmin=0.08, alpha=.4, color="r")
        ax.text(x=-0.08, y=mos-0.05, s="Q%d" % (mos_values.size - i))

    ax.set_xlim([-0.1, 1])
    ax.set_ylim([1, 5.3])

    wmean_mos = vmos.predict(thl)

    ax.scatter(-0.09, wmean_mos)

    ax.set_xlabel("Time on Quality (%)")
    ax.set_ylabel("MOS per Quality")

    return y_all

#if __name__ == "__main__":
#
    #import numpy as np
    #import matplotlib.pylab as plt

    #layer_time = np.array([0.7,0.2,0.1,0,0])
    #mos_values = np.array([4.9, 4.1, 2.9, 2.1, 1.8])

    #y_all = plot_example(mos_values, layer_time)

    #plt.savefig("mos_dash.pdf")
