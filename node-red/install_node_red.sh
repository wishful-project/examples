#/bin/bash

curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
nodejs --help
sudo apt-get install -y build-essential
sudo npm install -g --unsafe-perm node-red

echo "start by exec: node-red"