#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

if __name__ == "__main__":

    from clients.StandaloneClient import StandaloneClient
    from clients.WebRTCClient.WebRTCClient import WebRTCClient

    # start client
    client = StandaloneClient(client_class=WebRTCClient)
    client.run()
