#!/bin/sh
process="./dvb_tx_iris_wishful_controller"
timer=10
while true; do
      number=`ps ax | grep $process | grep -v grep| wc -l`
      if [ $number -eq 0 ]; then
                ./dvb_tx_iris_wishful_controller --config ./controller_config.yaml
       fi
        sleep $timer
done

