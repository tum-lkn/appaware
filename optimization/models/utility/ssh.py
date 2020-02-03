#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scipy import interpolate
import pickle
import numpy as np


class SSHUtility(object):

    def __init__(self, scaled=False, min_mos=1.0, max_mos=4.3):

        self._scaled = scaled

        self._min_mos = min_mos
        self._max_mos = max_mos

        self._f = None
        self._finv = None
        self._X = None
        self._y = None

        # Based on
        # Quality of Experience in Remote Virtual Desktop Services
        # Pedro Casas, Michael Seufert, SebastianEgger, and Raimund Schatz
        # Fig 5a
        self._X = np.array([0, 50, 150, 200, 350, 500]) / 1000
        self._y = [4.3, 4.22, 3.65, 3.6, 2.95, 2.6]

        self._f = interpolate.interp1d(self._X, self._y,
                                       fill_value="extrapolate",
                                       #fill_value=(y[0], y[-1]),
                                       bounds_error=False)

        self._finv = interpolate.interp1d(self._y, self._X,
                                         fill_value="extrapolate",
                                         #fill_value=(y[0], y[-1]),
                                         bounds_error=False)

    def predict(self, rt):

        temp_mos = self._predict_mos(rt)

        if not (temp_mos >= self._min_mos and temp_mos <= self._max_mos):
            raise Exception("Invalid MOS %.5f (bounds: [%.5f, %.5f]!" % (temp_mos, self._min_mos, self._max_mos))

        if self._scaled:
            utility = np.interp(temp_mos, (self._min_mos, self._max_mos), (1, 5))
        else:
            utility = temp_mos

        return utility

    def _predict_mos(self, rt):

        r = self._f(rt)

        v = max(min(r, self._y[0]), 1)

        return v

    def inverse(self, utility):

        assert(utility >= 1.0 and utility <= 5.0)

        r = self._finv(utility)

        return max(r, 0)

    def save(self, fn):
        """"
        Save the current model to a file.
        """
        data = [self._X, self._y]

        with open(fn, "wb") as f:
            pickle.dump(data, f)

    def load(self, fn):
        """
        Load a previously saved model.
        """

        with open(fn, 'rb') as f:
            data = pickle.load(f)

        self.fit(data[0], data[1])


if __name__ == "__main__":

    ssh_mos = SSHUtility(scaled=True)

    # Based on
    # Quality of Experience in Remote Virtual Desktop Services
    # Pedro Casas, Michael Seufert, SebastianEgger, and Raimund Schatz
    # Fig 5a
    # paper_x = np.array([0, 50, 150, 200, 350, 500]) / 1000
    # paper_y = [4.3, 4.22, 3.65, 3.6, 2.95, 2.6]
    # ssh_mos.fit(paper_x, paper_y)

    #ssh_mos.load('sshutility.pickle')

    print(ssh_mos.predict(0.1))
    print(ssh_mos.predict(0.05))

    import numpy as np
    import matplotlib.pylab as plt

    f, ax = plt.subplots()

    x = np.linspace(0.0, 1.5)
    y = list(map(ssh_mos.predict, x))

    ax.step(x, y)
    ax.grid()

    for x, y in zip(ssh_mos._X, ssh_mos._y):
        ax.axhline(y, color="r", alpha=0.3)

    ax.set_yticks(range(1, 6))

    ax.set_xlabel("Response Time rt (s)")
    ax.set_ylabel(r"$Utility_{SSH}(rt)$")

    #plt.savefig("mos_ssh.pdf")

    # Inverse
    f, ax = plt.subplots()

    x = np.linspace(1, 5)
    y = list(map(ssh_mos.inverse, x))

    ax.step(x, y)
    ax.grid()

    #for x, y in zip(paper_x, paper_y):
    #    ax.axhline(y, color="r", alpha=0.3)

    #ax.set_yticks(range(1, 6))

    ax.set_ylabel("Response Time rt (s)")
    ax.set_xlabel(r"$Utility_{SSH}(rt)$")

    #f.savefig("utility_ssh.png", dpi=200)