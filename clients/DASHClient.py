#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

if __name__ == "__main__":

    from clients.StandaloneClient import StandaloneClient
    from clients.DASHClient.DASHClient import DASHClient

    # start client
    client = StandaloneClient(client_class=DASHClient)
    client.run()

