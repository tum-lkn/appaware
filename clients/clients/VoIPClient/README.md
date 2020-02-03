# VoIPClient

## QUICKSTART

Start-up the vagrant machine:

```
vagrant up
```

First create a VoIP *client*:

```
vagrant ssh
cd /vagrant
python3 VoIPClient.py -s
```

Second create the VoIP *server*:

```
vagrant ssh
cd /vagrant
python3 VoIPServer.py
```

The statistics of the calls are stored at *client* side.

## Dependencies

```
provision.sh
```

This client uses D-ITG

http://traffic.comics.unina.it/software/ITG/manual/index.html#SECTION00051000000000000000

## Usage

config sample can be found at sample_config.json

```
$ ./VoIPClient.py --help
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


