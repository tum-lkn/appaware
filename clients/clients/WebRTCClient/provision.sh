#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y python3-pip firefox

cd $(dirname $0)

pip3 install -r requirements.txt

# install requirements for PrototypeClient
pip3 install -r ../PrototypeClient/requirements.txt

# install geckodriver for firefox
sudo apt-get install -y jq

INSTALL_DIR="/usr/local/bin"

json=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest)
url=$(echo "$json" | jq -r '.assets[].browser_download_url | select(contains("linux64"))')
curl -s -L "$url" | tar -xz
chmod +x geckodriver
sudo mv geckodriver "$INSTALL_DIR"
echo "installed geckodriver binary in $INSTALL_DIR"
