import os
import time
import logging
import json
import subprocess
from .utils.bottle import Bottle, route, request, HTTPError


log = logging.getLogger(__name__)


class DummyAppController(Bottle):
    """
    A dummy application controller which can just receive and save status messages from applications.
    """

    def __init__(self, statusldir="."):
        super(DummyAppController, self).__init__()

        log.debug("Initializing DummyAppController.")

        self.put("/application/<id>/status", callback=self.put_application_status)

        self.post("/applications", callback=self.post_applications)

        # Status log directory
        self._statusldir = statusldir

        os.makedirs(self._statusldir, exist_ok=True)

        # File handlers for status logs of applications
        self._apps_statusf = {}

    def put_application_status(self, id):

        log.debug("put_application_status(%s)" % id)

        if not request.json:
            error_no_json_content(request.path)

        status = request.json

        status['timestamp'] = time.time()

        if id not in self._apps_statusf:
            self._apps_statusf[id] = open(os.path.join(self._statusldir, "%s.json.csv" % id), "a")

        self._apps_statusf[id].write(json.dumps(status) + "\n")
        self._apps_statusf[id].flush()

        return {'success': "Application status updated!"}

    def post_applications(self):

        log.debug("post_applications()")

        # We are not doing anything here

        return {'success': "Application registered."}


def error_no_json_content(route):
    log.error("POST: {}: No JSON content received!".format(route))
    raise HTTPError(status=400, body="No JSON content received!")


if __name__ == "__main__":

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}
    logging.basicConfig(level=logging.DEBUG, **logconf)

    import argparse

    parser = argparse.ArgumentParser(description="SDN Controller Interface.")
    parser.add_argument('-l', '--log', help="Folder where to store the application status logs.", default='.')
    parser.add_argument('-b', '--bind', help="REST API bind IP.", default="0.0.0.0")
    parser.add_argument('-p', '--port', help="REST API Port.", default=8080)
    args = parser.parse_args()

    restapi = DummyAppController(statusldir=args.log)

    restapi.run(host=args.bind, port=args.port, debug=True)
