if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -e

export DEBIAN_FRONTEND=noninteractive

apt install -y nodejs npm

npm install -g proxy-login-automator

rm -rf /etc/systemd/system/proxy-login.service

cat >> /etc/systemd/system/proxy-login.service <<EOT
[Unit]
Description=Linode Proxy Farwarder
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=200
User=root
Group=www-data
ExecStart=/usr/bin/node /usr/local/bin/proxy-login-automator.js -local_port 8081 -remote_host 66.175.208.170 -remote_port 5729 -ignore_https_cert true -usr root -pwd gu5LDMa2YoJAhUeOpIhHd4FB

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable proxy-login.service
systemctl start proxy-login.service
