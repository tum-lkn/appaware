#!/usr/bin/env bash

if [ $(basename $0) = "setup_client.sh" ]; then
    # We can use relative PATH
    REPO_PATH=$(dirname $0)"/../"
else
    # Called from e.g. /tmp/vagrant-shell so we assume repo can be found in /vagrant
    REPO_PATH="/vagrant/"
fi

bash ${REPO_PATH}/clients/WebClient/provision.sh
bash ${REPO_PATH}/clients/WebDLClient/provision.sh
bash ${REPO_PATH}/clients/SSHClient/provision.sh
bash ${REPO_PATH}/clients/WebRTCClient/provision.sh
bash ${REPO_PATH}/clients/DASHClient/provision.sh
bash ${REPO_PATH}/clients/VoIPClient/provision.sh
bash ${REPO_PATH}/control/Daemon/provision.sh
bash ${REPO_PATH}/control/TestController/provision.sh
bash ${REPO_PATH}/servers/WebServer/provision.sh
bash ${REPO_PATH}/servers/WebRTCServer/provision.sh
bash ${REPO_PATH}/servers/VoIPServer/provision.sh
