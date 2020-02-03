#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def print_app_list(apps, fn=None):

    if fn:
        file = open(fn, "w")
    else:
        file = sys.stdout

    for idx, app in apps.items():
        print("%03d: %03d -> %03d - %s" % (idx, app['src'], app['dst'], app['model']),
              file=file)

    if fn:
        file.close()

if __name__ == "__main__":

    apps = {0: {'src': 0, 'dst': 5, 'model': 'model_generic'}}

    print_app_list(apps, "apps.txt")