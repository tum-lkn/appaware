#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

if __name__ == "__main__":

    from servers.StandaloneServer import StandaloneServer
    from servers.VoIPServer.VoIPServer import VoIPServer

    # start server
    server = StandaloneServer(server_class=VoIPServer)
    server.run()