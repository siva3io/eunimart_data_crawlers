#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -e

export DEBIAN_FRONTEND=noninteractive

rm -rf /etc/apt/sources.list.d/google-chrome.list

rm -rf /etc/systemd/system/crawler-worker.service

cat >> /etc/apt/sources.list.d/google-chrome.list <<EOT
deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main
EOT

wget https://dl.google.com/linux/linux_signing_key.pub

apt-key add linux_signing_key.pub

apt update

apt-get install google-chrome-stable python3.6 python3-pip zip unzip libpq-dev

wget https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_linux64.zip

unzip chromedriver_linux64.zip

mv chromedriver /usr/bin/chromedriver

chown root:root /usr/bin/chromedriver

chmod +x /usr/bin/chromedriver

pip3 install -r ../requirements.txt