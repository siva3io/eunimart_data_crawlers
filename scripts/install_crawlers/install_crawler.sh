#!/bin/bash
rm -rf /etc/systemd/system/crawler-worker.service

cat >> /etc/systemd/system/crawler-worker.service <<EOT
[Unit]
Description=Web Crawler Worker
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
RemainAfterExit=no
Restart=on-failure
RestartSec=5s
User=root
Group=www-data
ExecStart=/home/ubuntu/eunimart_data_crawlers/scripts/run_crawler/run_crawler.sh
KillMode=process

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable crawler-worker.service
systemctl start crawler-worker.service