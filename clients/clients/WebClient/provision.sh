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


# phantomjs installation
apt-get install build-essential chrpath libssl-dev libxft-dev -y
apt-get install libfreetype6 libfreetype6-dev -y # already installed as dependency
apt-get install libfontconfig1 libfontconfig1-dev -y # already installed as dependency
cd ~
export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
wget -q https://github.com/Medium/phantomjs/releases/download/v2.1.1/$PHANTOM_JS.tar.bz2
tar xvjf $PHANTOM_JS.tar.bz2
rm $PHANTOM_JS.tar.bz2
mv $PHANTOM_JS /usr/local/share
ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
