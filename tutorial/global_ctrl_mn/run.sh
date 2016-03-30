#!/usr/bin/env bash

echo "Hello world with global WiSHFUL controller and remote WiSHFUL agents in Mininet-WiFi"

sudo python mn_script.py

if [ "$?" != "0" ]; then
  echo "Unittest failed !!!!"
fi

echo "cleaning up ..."
sudo mn -c 2>/dev/null
