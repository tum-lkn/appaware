#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class ServiceInterface(object):

    @property
    def max_tp(self):
        return self.X.iloc[:,0].max()

    @property
    def min_tp(self):
        return self.X.iloc[:,0].min()

    @property
    def max_delay(self):
        return self.X.iloc[:,1].max()

    @property
    def min_delay(self):
        return self.X.iloc[:,1].min()