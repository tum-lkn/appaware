# Clients 

## Daemon

Not finished yet

## nsjoin - Namespace Support

*nsjoin* allows to execute a client in a isolated network namespace.
At the moment only network namespaces are supported.

Example to enter a namespace named *testns* and execute the web client as user *vagrant*.

```
./nsjoin -u vagrant testns ./WebClient.py -c clients/WebClient/sample_config.json -s
```

## WebClient

config sample can be found at clients/WebClient/sample_config.json

```
$ WebClient.py --help
usage: WebClient.py [--help] [-a APP_CONTROLLER] [-c CONFIG] [-d [DEBUG_LOG]]
                    [-h HOST_ID] [-i CLIENT_ID] [-l [APP_CONTROLLER_LOG]]
                    [-m [METRIC_LOG]] [-p APP_CONTROLLER_PORT] [-s] [-v]

WebClient parameter

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

## SSHClient

config sample can be found at clients/SSHClient/sample_config.json

```
SSHClient.py --help
usage: SSHClient.py [--help] [-a APP_CONTROLLER] [-c CONFIG] [-d [DEBUG_LOG]]
                    [-h HOST_ID] [-i CLIENT_ID] [-l [APP_CONTROLLER_LOG]]
                    [-m [METRIC_LOG]] [-p APP_CONTROLLER_PORT] [-s] [-v]

SSHClient parameter

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

## WebRTCClient

config sample can be found at clients/WebRTCClient/sample_config.json

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

## WebDLClient

config sample can be found at clients/WebDLClient/sample_config.json

```
$ ./WebDLClient.py --help
usage: WebDLClient.py [--help] [-a APP_CONTROLLER] [-c CONFIG] [-d [DEBUG_LOG]]
                    [-h HOST_ID] [-i CLIENT_ID] [-l [APP_CONTROLLER_LOG]]
                    [-m [METRIC_LOG]] [-p APP_CONTROLLER_PORT] [-s] [-v]

WebDLClient parameter

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

## DASHClient

config sample can be found at clients/DASHClient/sample_config.json

```
$ ./DASHClient.py --help
usage: DASHClient.py [--help] [-a APP_CONTROLLER] [-c CONFIG] [-d [DEBUG_LOG]]
                    [-h HOST_ID] [-i CLIENT_ID] [-l [APP_CONTROLLER_LOG]]
                    [-m [METRIC_LOG]] [-p APP_CONTROLLER_PORT] [-s] [-v]

DASHClient parameter

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
