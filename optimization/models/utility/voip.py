#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy import interpolate

class VoIPUtility(object):

    #from Lingfen Sun: Voice Quality Prediction Models and Their Application in VoIP Networks

    def __init__(self, scaled=False, min_mos=1.0, max_mos=3.65):

        self._scaled = scaled

        self._min_mos = min_mos
        self._max_mos = max_mos

        x0 = np.linspace(0, 600,100)  # jitter
        x1 = np.linspace(0, 600,100)  # delay
        x2 = np.linspace(0,0,len(x1)) # packet_loss
        y = list(map(self.predict, x0, x1, x2))

        self._finv = interpolate.interp1d(y, x1,
                                 fill_value="extrapolate",
                                 bounds_error=False)

    def predict(self, jitter, delay, packet_loss):
        """
        Estimates the utility of a VoIP call.

        :param jitter
        :param delay
        :param packet_loss
        """

        temp_mos = self._predict_mos(jitter, delay, packet_loss)

        if not (temp_mos >= self._min_mos and temp_mos <= self._max_mos):
            raise Exception("Invalid MOS %.5f (bounds: [%.5f, %.5f]!" % (temp_mos, self._min_mos, self._max_mos))

        if self._scaled:
            utility = np.interp(temp_mos, (self._min_mos, self._max_mos), (1, 5))
        else:
            utility = temp_mos

        return utility

    def _predict_mos(self, jitter, delay, packet_loss):
        codec = 'G729'
        if codec == 'G729':
            a = 3.61
            b = -0.13
            c = 1.22*10**-3
            d = 3.76*10**-3
            e = -2.29*10**-5
            f = 4.71*10**-6
            g = -5.16*10**-5
            h = 2.54*10**-8
            i = 1.28*10**-7
            j = -4.43*10**-8

        #if delay>177.3:
        #    H_x = 1
        #else:
        #    H_x = 0
        #I_d = 0.024*delay+0.11(delay-177.3)*H_x
        #I_e = 16.68*np.log(1+0.3011*packet_loss) + 14.96
        #I_e = a*np.log(1+b*packet_loss)+c
        temp_mos = a+b*packet_loss+c*delay+d*np.power(packet_loss,2)+e*np.power(delay,2)+f*packet_loss*delay+g*np.power(packet_loss,3)+h*np.power(delay,3)+i*packet_loss*np.power(delay,2)+j*np.power(packet_loss,2)*delay



        return temp_mos
        #return max(1.0, min(temp_mos,5.0))

    def inverse(self, utility):

        assert(utility >= 1.0 and utility <= 5.0)

        r = self._finv(utility)

        return max(r,0)

if __name__ == "__main__":
    voip_mos = VoIPUtility(scaled=True)

    import numpy as np
    import matplotlib.pylab as plt

    f, ax = plt.subplots()

    x0 = np.linspace(0, 600,100)
    x1 = np.linspace(0, 600,100)
    x2 = np.linspace(0,0,len(x1))
    y1 = list(map(voip_mos.predict, x0, x1, x2))

    ax.step(x1, y1)
    ax.grid()

    ax.set_yticks(range(1, 6))

    ax.set_xlabel("Delay (ms)")
    ax.set_ylabel(r"$Utility_{VOIP}(delay)$")

    f.savefig("utility_voip1.png", dpi=200)
    # Inverse
    f, ax = plt.subplots()

    x = np.linspace(1.471, 3.468)
    y = list(map(voip_mos.inverse, x))

    ax.step(x, y)
    ax.grid()

    ax.set_ylabel("Delay (ms)")
    ax.set_xlabel(r"$Utility_{VOIP}(delay)$")

    f.savefig("utility_voip2.png", dpi=200)

#    result = []
#
#    for d in range(0,len(delays)-1):
#        result.append([])
#        for p in range(0,len(packet_losses)-1):
#            result[d].append(voip_mos.predict(delays[d],packet_losses[p]))
#
#    X, Y = np.meshgrid(delays, packet_losses)
#    Z = voip_mos.predict(X,Y)
#
#    import numpy as np
#    import matplotlib.pylab as plt
#
#    fig = plt.figure()
#    ax = fig.gca(projection='3d')
#
#    surf = ax.plot_surface(Y, X, Z, cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)
#
#    plt.gca().invert_yaxis()
#    ax.set_zlim(1, 4)
#
#    ax.set_xlabel('Delay [ms]')
#    ax.set_ylabel('Packet loss [%]')
#    ax.set_zlabel('MOS')
#
#    plt.show()

