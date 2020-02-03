#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright (c) Vito Caldaralo <vito.caldaralo@gmail.com>

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE" in the source distribution for more information.
import os, sys
from twisted.python import usage, log

class Options(usage.Options):
    optParameters = [
        ('controller', 'a', 'conventional', 'Adaptive Algorithm [conventional|tobasco|max]'),
        ('url', 'u', 'http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8', 'The playlist url. It determines the parser for the playlist'),
        ('log_sub_dir', 'l', None, 'Log sub-directory'),
        ('log_dir', 'l', None, 'Log directory'),
        ('stress_test', 's', False, 'Enable stress test. Switch level for each segment, cyclically.'),
        ('max_buffer_time', 'm', 60, 'Max time to buffer.'),
    ]
options = Options()
try:
    options.parseOptions()
except Exception as e:
    print('%s: %s' % (sys.argv[0], e))
    print('%s: Try --help for usage details.' % (sys.argv[0]))
    sys.exit(1)

def select_player():
    log.startLogging(sys.stdout)

    persistent_conn = True
    check_warning_buffering=True

    #MediaEngine
    from Tapas.media_engines.FakeMediaEngine import FakeMediaEngine
    media_engine = FakeMediaEngine()

    #Controller
    if options['controller'] == 'conventional':
        from Tapas.controllers.ConventionalController import ConventionalController
        controller = ConventionalController(max_buffer_time=int(options['max_buffer_time']))
    elif options['controller'] == 'tobasco':
        from Tapas.controllers.TOBASCOController import TOBASCOController
        controller = TOBASCOController()
    elif options['controller'] == 'max':
        check_warning_buffering=False
        from Tapas.controllers.MaxQualityController import MaxQualityController
        controller = MaxQualityController()
    else:
        print('Error. Unknown Control Algorithm')
        sys.exit()

    #Parser
    url_playlist = options['url']
    if ".mpd" in url_playlist:
        from Tapas.parsers.DASH_mp4Parser import DASH_mp4Parser
        parser = DASH_mp4Parser(url_playlist)
    elif ".m3u8" in url_playlist:
        from Tapas.parsers.HLS_mpegtsParser import HLS_mpegtsParser
        parser = HLS_mpegtsParser(url_playlist)
    else:
        print('Error. Unknown Parser')
        sys.exit()

    print("Max buffer time: ", options['max_buffer_time'], "type ", type(options['max_buffer_time']))

    #StartPlayer
    from Tapas.TapasPlayer import TapasPlayer
    player = TapasPlayer(controller=controller, parser=parser, media_engine=media_engine,
        log_dir=options['log_dir'],
        log_sub_dir="tapas",
        max_buffer_time=int(options['max_buffer_time']),
        log_period=1,
        inactive_cycle=1, initial_level=0,
        use_persistent_connection=persistent_conn,
        check_warning_buffering=check_warning_buffering,
        stress_test=options['stress_test'],
        metric_log_interval=1)
    #print 'Ready to play'

    player.start()

    import time
    import signal

    def signal_handler(signum, frame):
        print("CTRL+C")
        player.stop()

    signal.signal(signal.SIGINT, signal_handler)

    # wait for reactor to start
    while not player.is_running():
        print("wait start")
        time.sleep(1)

    t_next = time.time() + 5
    while player.is_running():
        if time.time() > t_next:
            t_next += 5
            print()
            print()
            print("metric_logs")
            print(player.get_metric_logs())
            print()
            print()
        time.sleep(1)
        print("waiting")

    player.cleanup()

if __name__ == '__main__':
    select_player()
