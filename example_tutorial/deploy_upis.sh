#!/bin/bash

if [ $# -lt 1 ]; then
	echo "usage $0 nodes_list     (use ',' to separate nodes in list )"
	exit
fi

set -x
nodes=$(echo $1 | tr "," "\n")


if [ 1 -eq 1 ]; then

    for node in $nodes
    do
        rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude examples/* --exclude agent_modules/*  --exclude .repo/ ../../  -e ssh root@$node:~/wishful-github-manifest/
        rsync -avz  ../../agent_modules/iperf/  -e ssh root@$node:~/wishful-github-manifest/agent_modules/iperf/
        rsync -avz  ../../agent_modules/wifi_wmp/  -e ssh root@$node:~/wishful-github-manifest/agent_modules/wifi_wmp/
        rsync -avz  ../../agent_modules/wifi/  -e ssh root@$node:~/wishful-github-manifest/agent_modules/wifi/
        rsync -avz  ../../examples/example_tutorial/  -e ssh root@$node:~/wishful-github-manifest/examples/example_tutorial/
    done

fi

set +x


