import sys
import json
import requests

if __name__ == "__main__":

    ip = "10.0.8.0"
    port = 3000
    auth = ('admin', 'admin')
    dashboard = "demodashboard"
    headers = {'content-type': 'application/json'}

    url = "http://{}:{}/api/dashboards/db/{}".format(ip, port, dashboard)

    sys.stderr.write("GET: {}\n".format(url))

    r = requests.get(url, auth=auth, headers=headers)

    if r.status_code == 404:
        print("Could not found dashboard {}!".format(dashboard))
        sys.exit(1)

    body = r.json()

    body['overwrite'] = True
    body['dashboard']['id'] = None
    #body['dashboard']['uid'] = None # Only necessary if dashboard exists already.

    print(json.dumps(body, indent=4, sort_keys=True))

