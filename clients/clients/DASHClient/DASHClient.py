#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import random
import time
import pandas as pd
from clients.PrototypeClient import PrototypeClient
from os.path import join as pjoin
import signal
import subprocess
import os

class DASHClient(PrototypeClient.PrototypeClient):
    def __init__(self, **kwargs):
        super(DASHClient, self).__init__(**kwargs)
        self._logger.debug("DASHClient.__init__()")

        self._default_config.update({
            "url": "http://127.0.0.1/bbb_60s/bbb_SDNAPPAWARE.m3u8",
            "buffer_size": 60,
            "controller": "conventional"
        })

        self._next_call = time.time()

        self._view = 0

    def prepare(self):
        self._logger.debug("DASHClient.prepare()")
        self.register_application()

    def run(self):
        self._logger.debug("DASHClient.run()")
        self._running = True

        if not self._config:
            self._logger.info("No config applied yet - using default config")
            self.set_config(config={})

        self._random_wait_start()

        while self._running:

            if not self._do_request():
                time.sleep(0.1)
                continue

            self._logger.info("++ View %d ++" % self._view)

            self._config['log_dir'] = pjoin(self._log_dir, "view_%d" % self._view)

            self._config['wdir'] = os.path.dirname(os.path.abspath(__file__))

            cmd = "cd {wdir}; python3 -m Tapas.play --controller={controller} --url={url} --log_dir={log_dir} -m {buffer_size}"\
                  .format(**self._config)

            self._logger.debug(cmd)

            os.makedirs(self._config['log_dir'], exist_ok=True)

            with open(pjoin(self._config['log_dir'], "popen_stdout.log"), "wt") as fout, \
                 open(pjoin(self._config['log_dir'], "popen_stderr.log"), "wt") as ferr:

                tapas = subprocess.Popen(cmd, shell=True, stdout=fout, stderr=ferr, preexec_fn=os.setsid)

                self._logger.debug("DASHClient running")

                # Wait for tapas player to stop
                while True:
                    try:
                        self._logger.info("Waiting for player to exit")
                        tapas.wait(timeout=5)
                        # wait exited normally - breaking
                        break
                    except subprocess.TimeoutExpired:
                        if self._running:
                            self._logger.debug("Waiting timed out but client still running")
                            # client still running - everything ok wait again
                            pass
                        else:
                            # client stopped but TAPAS running - killing it
                            self._logger.debug("Waiting timed out but client stopped - killing process %s" % (tapas.pid))
                            os.kill(-tapas.pid, signal.SIGTERM)
                            # wait another 2 seconds for tapas to exit then kill hard in case sigint was$
                            time.sleep(2)
                            os.kill(-tapas.pid, signal.SIGKILL)
                            break

                self._logger.info("Player stopped.")

            metric = self._parse_logs(self._log_dir, self._view)

            self._create_metric(metric=metric)
            self._report_metric()

            self._request_finished()

            self._view += 1

        self._running = False

    def _parse_logs(self, log_dir, view):

        viewd = pjoin(log_dir, "view_%d" % view, "tapas")

        logs = os.listdir(viewd)

        segmentsf = [l for l in logs if l.endswith("segments.csv")][0]
        stallingsf = [l for l in logs if l.endswith("stallings.csv")][0]
        logf = [l for l in logs if l.endswith(".log")][0]

        df_segs = pd.read_csv(pjoin(viewd, segmentsf))
        df_stallings = pd.read_csv(pjoin(viewd, stallingsf))

        mean_ql = df_segs.iloc[1:-1].ql.mean()
        stalling = (df_stallings.t_playing - df_stallings.t_paused).sum()
        switches = (df_segs.iloc[1:-1].ql.diff() > 0).sum()
        segments = df_segs.iloc[1:-1].ql.count()

        dflog = pd.read_csv(pjoin(viewd, logf), sep=" ", skiprows=2, header=None)

        return {'mean_ql': float(mean_ql), 'stalling': float(stalling),
                'switches': int(switches), 'segments': int(segments),
                'stalling_cnt': int(df_stallings.t_playing.count()),
                'view': "view_%d" % view,
                'duration': float(dflog.iloc[:,0].max() - dflog.iloc[:,0].min())}

    def clean_up(self):
        self._logger.debug("DASHClient.clean_up()")
        self.unregister_application()

    def _apply_config(self):
        self._logger.debug("DASHClient._apply_config()")


if __name__ == '__main__':

    from clients.StandaloneClient import StandaloneClient

    # start client
    client = StandaloneClient.StandaloneClient(client_class=DASHClient)
    client.run()
