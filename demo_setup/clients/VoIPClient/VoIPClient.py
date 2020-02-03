#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import time
import subprocess

from clients.PrototypeClient import PrototypeClient
from servers.utils.ITG import ITG


class VoIPClient(PrototypeClient.PrototypeClient):
    def __init__(self, **kwargs):
        super(VoIPClient, self).__init__(**kwargs)
        self._logger.debug("VoIPClient.__init__()")

        self._default_config.update({
        })

        self._itgrecv = None

    def prepare(self):
        self._logger.debug("VoIPClient.prepare()")
        self.register_application()

    def run(self):
        self._logger.debug("VoIPClient.run()")
        self._running = True

        prev_call_logs = set([d for d in os.listdir(".") if d.startswith("call_")])

        self._itgrecv = ITG("ITGRecv")
        self._itgrecv.start()

        while self._running:
            self._logger.debug("Sleeping")
            time.sleep(1)
            self._logger.debug("finished Sleeping")

            call_logs = set([d for d in os.listdir(".") if d.startswith("call_") and d.endswith(".bin")])

            new_logs = [l for l in call_logs if l not in prev_call_logs]

            prev_call_logs = call_logs

            for logf in new_logs:

                while not self._is_finished_writing(logf):
                    time.sleep(1)

                self._logger.debug("CALL: %s" % logf)

                metric = self._parse_log(logf)

                self._create_metric(metric=metric)
                self._report_metric()

    def _parse_log(self, logf):

        # Summary Statistics
        cmd = "ITGDec %s -c 1000000 %s.txt" % (logf, logf)

        self._logger.debug("CMD: %s " % cmd)

        subprocess.check_call(cmd, shell=True)

        with open("%s.txt" % logf) as f:
            stats = f.readlines()

        # It should be only one line..
        assert (len(stats) == 1)

        m = ["time", "bitrate", "delay", "jitter", "packets_lost"]

        sp = stats[0].split()
        stats = {m: float(sp[i]) for i, m in enumerate(m)}

        # Print metrics summary for debugging
        cmd = "ITGDec %s > %s.summary.txt" % (logf, logf)

        self._logger.debug("CMD: %s " % cmd)

        subprocess.check_call(cmd, shell=True)

        # Packet count and sizes
        cmd = "ITGDec %s -P > %s.sizes.txt" % (logf, logf)

        self._logger.debug("CMD: %s " % cmd)

        subprocess.check_call(cmd, shell=True)

        with open("%s.sizes.txt" % logf) as f:
            sizes = f.readlines()

        pkt_count = len(sizes) - 2

        avg_pkt_size = int(sum([int(p) for p in sizes[2:]]) / pkt_count)

        stats.update({'call': logf,
                      'rcvd_pkt_count': pkt_count,
                      'rcvd_avg_pkt_size': avg_pkt_size,
                      'packet_loss': stats['packets_lost'] / (pkt_count + stats['packets_lost']),
                      'raw_application_metric': stats['packets_lost'] / (pkt_count + stats['packets_lost'])})

        return stats

    def _is_finished_writing(self, logf):
        """
        Checks if ITG finished writing the logfile.

        :param logf:
        :return:
        """

        cmd = "lsof -t %s" % logf

        #self._logger.debug("CMD: %s" % cmd)

        try:
            out = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            # Exception means no process has the file open right now
            return True

        return False

    def clean_up(self):
        self._logger.debug("VoIPClient.clean_up()")

        self._itgrecv.stop()

        self.unregister_application()

    def _apply_config(self):
        self._logger.debug("VoIPClient._apply_config()")


if __name__ == '__main__':

    from clients.StandaloneClient import StandaloneClient

    # start client
    client = StandaloneClient.StandaloneClient(client_class=VoIPClient)
    client.run()


