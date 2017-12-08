#!/bin/bash

if [ $# -lt 1 ]; then
	echo "usage $0 <user> <nodes_list> (use ',' to separate nodes in list )"
	exit
fi

set -x
user=$1
nodes=$(echo $2 | tr "," "\n")
stations=$nodes
kill_before=0

if [ 1 -eq 1 ]; then

    for sta in $stations
    do
        rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude examples/* --exclude agent_modules/*  --exclude .repo/ ../../../  -e ssh $user@$sta:~/wishful-github-manifest/
        rsync -avz  ../../../agent_modules/iperf/  -e ssh $user@$sta:~/wishful-github-manifest/agent_modules/iperf/
        rsync -avz  ../../../agent_modules/wifi_wmp/  -e ssh $user@$sta:~/wishful-github-manifest/agent_modules/wifi_wmp/
        rsync -avz  ../../../agent_modules/wifi/  -e ssh $user@$sta:~/wishful-github-manifest/agent_modules/wifi/
        rsync -avz  ../../../agent_modules/net_linux/  -e ssh $user@$sta:~/wishful-github-manifest/agent_modules/net_linux/
        #ssh $user@$sta 'mkdir ~/wishful-github-manifest/examples/wmp/'
        ssh $user@$sta 'mkdir ~/wishful-github-manifest/examples/'
        #rsync -avz  ../../../examples/wmp/  -e ssh root@$sta:~/wishful-github-manifest/examples/wmp/
        rsync -avz --exclude experiment_data/* --exclude spectral_scan/* --exclude station-conf/writing-tool/* --exclude station-conf/scapy/* ../../../examples/interference_detection/  -e ssh $user@$sta:~/wishful-github-manifest/examples/interference_detection/
    done

fi

set +x


