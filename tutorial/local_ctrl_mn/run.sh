#!/usr/bin/env bash

echo "Hello world with local controller in mininet"

sudo python mn_script.py

if [ "$?" != "0" ]; then
  echo "Unittest failed !!!!"
fi

echo "cleaning up ..."
sudo mn -c 2>/dev/null
