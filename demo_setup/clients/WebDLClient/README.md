# WebDLClient
## Dependencies
```
provision.sh
```

The version of phantomjs in the ubuntu repo has problems although it is version 2.1.1

`Error - Unable to load Atom 'execute_script' from file ':/ghostdriver/./third_party/webdriver-atoms/execute_script.js'`

https://gist.github.com/telbiyski/ec56a92d7114b8631c906c18064ce620#file-install-phantomjs-2-1-1-ubuntu

```
apt-get update
apt-get install build-essential chrpath libssl-dev libxft-dev -y
apt-get install libfreetype6 libfreetype6-dev -y # already installed as dependency
apt-get install libfontconfig1 libfontconfig1-dev -y # already installed as dependency
cd ~
export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
wget https://github.com/Medium/phantomjs/releases/download/v2.1.1/$PHANTOM_JS.tar.bz2
tar xvjf $PHANTOM_JS.tar.bz2
rm $PHANTOM_JS.tar.bz2
mv $PHANTOM_JS /usr/local/share
ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
```

Other webdrivers for Firefox and Chrome could be installed on non headless machines

Firefox has also a headless mode and is used from now on because we are able to clear the cache via a WebExtension. In order to controll firefox the geckodriver needs to be installed.

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

## Reported Metric

WebDLClient reports download time and content length for HTTP(S) downloads.
Check the [documentation](http://pages.lkn.ei.tum.de/~appaware/docs/html/content/applications/webdl.html) for details.