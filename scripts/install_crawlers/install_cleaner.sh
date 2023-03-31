#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -e

export DEBIAN_FRONTEND=noninteractive

apt update

apt-get install python3.6 python3-pip zip unzip libpq-dev

pip3 install -r ../../requirements.txt

rm -rf /etc/systemd/system/cleaner-worker.service

cat >> /etc/systemd/system/cleaner-worker.service <<EOT
[Unit]
Description=Data cleaner Worker
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
RemainAfterExit=no
Restart=on-failure
RestartSec=5s
User=root
Group=www-data
ExecStart=/home/ubuntu/eunimart_data_crawlers/scripts/run_crawler/run_cleaner.sh

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable cleaner-worker.service
systemctl start cleaner-worker.service