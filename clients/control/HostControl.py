import logging
import subprocess

from .utils.bottle import Bottle, route, request, HTTPError

from .utils.iface_statistics.ip import InterfaceStatisticsIp
from .utils.iface_statistics.tc import InterfaceStatisticsTc
from .utils.iface_statistics.ss import SSStats
from .utils.iface_statistics.queue_limits import QueueLimits
from .utils.iface_statistics.exceptions import InterfaceNotFoundError


log = logging.getLogger(__name__)


class HostControl(Bottle):
    """
    The host control module provides a REST interface for external applications to send commands
    to the host where the application is running.
    Right now this is used to pace the hosts sending rate.
    Might be moved to a different repository later, as we also have to use it to control servers, not only
    the clients.
    """

    def __init__(self):
        super(HostControl, self).__init__()

        log.debug("Initializing HostControl.")

        self.put("/shaping/fq/add", callback=self.put_set_fq_rate)

        self.get("/shaping/tc_show", callback=self.get_tc_qdisc_show)

        self.get("/statistics/all", callback=self.get_all_statistics)

    def put_set_fq_rate(self):

        log.debug("put_set_fq_rate()")

        if not request.json:
            error_no_json_content(request.path)

        HostControl.set_fq(request.json['eth'], request.json['maxrate'])

    def get_tc_qdisc_show(self):

        log.debug("get_tc_qdisc_show()")

        output = subprocess.check_output("tc -s qdisc show", shell=True).decode('ASCII')

        return output

    def get_all_statistics(self) -> dict:
        log.debug("get_all_statistics()")

        if not request.json:
            error_no_json_content(request.path)

        try:
            stats_dict = {'tc': InterfaceStatisticsTc.get_interface_statistics(request.json['eth']),
                          'ip': InterfaceStatisticsIp.get_interface_statistics(request.json['eth']),
                          'ss': SSStats.get_ss_stats(),
                          'queue_limits': QueueLimits.get_queue_limits(request.json['eth'])}
            return stats_dict
        except InterfaceNotFoundError:
            error_iface_does_not_exist(request.json['eth'])

    @staticmethod
    def is_fq_set(eth):

        output = subprocess.check_output("sudo tc qdisc show", shell=True).decode('ASCII')

        for l in output.splitlines():
            if eth in l and "fq" in l:
                return True
        else:
            return False

    @staticmethod
    def set_fq(eth, maxrate):
        """
        Set's or updates the FQ scheduler on an interface.


        :param eth: The interface to add/change the shaping
        :param maxrate: tc compatible rate definiton, e.g.15mbit
        :return:
        """

        if HostControl.is_fq_set(eth):
            action = "change"
        else:
            action = "add"

        options = ['maxrate', str(maxrate)]

        cmd = ['sudo tc qdisc', action, 'dev', eth, 'root fq'] + options

        cmdstr = " ".join(cmd)

        log.debug("cmd: %s" % cmdstr)

        subprocess.check_call(cmdstr, shell=True)

def error_no_json_content(route):
    log.error("POST: {}: No JSON content received!".format(route))
    raise HTTPError(status=400, body="No JSON content received!")


def error_iface_does_not_exist(interface):
    msg = "Interface {} not found".format(interface)
    log.error(msg)
    raise HTTPError(status=400, body="msg")


if __name__ == "__main__":

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}
    logging.basicConfig(level=logging.DEBUG, **logconf)

    restapi = HostControl()

    restapi.run(host='0.0.0.0', port=8099, debug=True)
