#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from scipy import interpolate

# Download Task (10 MB)
# Egger, Sebastian, et al. "“Time is bandwidth”?
# Narrowing the gap between subjective time perception and Quality of Experience."
# Communications (ICC), 2012 IEEE International Conference on. IEEE, 2012.
class WebDLUtility(object):

    def __init__(self, scaled=False, min_mos=1, max_mos=5):

        self._scaled = scaled

        self._min_mos = min_mos
        self._max_mos = max_mos

        # Create inverse by interpolation
        x = np.linspace(0.1, 150)
        y = list(map(self.predict, x))

        self._finv = interpolate.interp1d(y, x,
                                 fill_value="extrapolate",
                                 bounds_error=False)

    def predict(self, dl):

        temp_mos = self._predict_mos(dl)

        if not (temp_mos >= self._min_mos and temp_mos <= self._max_mos):
            raise Exception("Invalid MOS %.5f (bounds: [%.5f, %.5f]!" % (temp_mos, self._min_mos, self._max_mos))

        if self._scaled:
            utility = np.interp(temp_mos, (self._min_mos, self._max_mos), (1, 5))
        else:
            utility = temp_mos

        return utility

    def _predict_mos(self, dl):
        """
        :param dl: Download Time (s)
        """
        # Restrict to range 1.0 - 5.0
        return max(1.0, min(-1.68 * np.log(dl) + 9.61, 5.0))

    def inverse(self, mos):

        assert(mos >= 1.0 and mos <= 5.0)

        r = self._finv(mos)

        return r


if __name__ == "__main__":

    model = WebDLUtility()

    print(model.predict(10))
    print(model.predict(150))

    import numpy as np
    import matplotlib.pylab as plt

    f, ax = plt.subplots()

    x = np.linspace(0.01, 180.0)
    y = list(map(model.predict, x))

    ax.step(x, y)
    ax.grid()

    ax.set_yticks(range(1, 6))

    ax.set_xlabel("Download Time 10MB dl (s)")
    ax.set_ylabel(r"$Utility_{WEBDL}(dl)$")

    # Inverse function
    f, ax = plt.subplots()

    x = np.linspace(1, 5)
    y = list(map(model.inverse, x))

    ax.step(x, y)
    ax.grid()

    ax.set_ylabel("Download Time 10MB dl (s)")
    ax.set_xlabel(r"$Utility_{WEBDL}(dl)$")

    f.savefig("utility_webdl.png", dpi=200)
