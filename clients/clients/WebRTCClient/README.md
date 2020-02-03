# WebRTCClient
## Dependencies
```
provision.sh
```

This client uses Firefox in headless mode controlled via selenium. In order to controll firefox the geckodriver needs to be installed.

https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu/928514#928514

```
sudo apt-get install -y jq

INSTALL_DIR="/usr/local/bin"

json=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest)
url=$(echo "$json" | jq -r '.assets[].browser_download_url | select(contains("linux64"))')
curl -s -L "$url" | tar -xz
chmod +x geckodriver
sudo mv geckodriver "$INSTALL_DIR"
echo "installed geckodriver binary in $INSTALL_DIR"
```

## Usage
config sample can be found at sample_config.json

```
$ ./WebRTCClient.py --help
usage: WebRTCClient.py [--help] [-a APP_CONTROLLER] [-c CONFIG] [-d [DEBUG_LOG]]
                    [-h HOST_ID] [-i CLIENT_ID] [-l [APP_CONTROLLER_LOG]]
                    [-m [METRIC_LOG]] [-p APP_CONTROLLER_PORT] [-s] [-v]

WebRTCClient parameter

optional arguments:
  --help                show this help message and exit
  -a APP_CONTROLLER, --app-controller APP_CONTROLLER
                        IP of app controller
  -c CONFIG, --config CONFIG
                        Client config file
  -d [DEBUG_LOG], --debug-log [DEBUG_LOG]
                        Log verbose output to file
  -h HOST_ID, --host HOST_ID
                        Host identifier (e.g. IP)
  -i CLIENT_ID, --id CLIENT_ID
                        Client identifier
  -l [APP_CONTROLLER_LOG], --log [APP_CONTROLLER_LOG]
                        Log app cotroller calls to file
  -m [METRIC_LOG], --metric-log [METRIC_LOG]
                        Log app metric to file
  -p APP_CONTROLLER_PORT, --port APP_CONTROLLER_PORT
                        App controller port
  -s, --standalone      Standalone without app-controller
  -v, --verbose         Verbose
```

## Reported Metric

WebRTCClient reports RTCPeerConnectio.getStats() and also appStats with some information about the current operational state.
Check the [documentation](http://pages.lkn.ei.tum.de/~appaware/docs/html/content/applications/webrtc.html) for details.
