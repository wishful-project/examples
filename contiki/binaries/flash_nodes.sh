#!/bin/bash
export PATH=$PATH:/opt/compilers/mspgcc-4.7.3/bin
echo $PATH
NODE_ID=$1
if [ $# = 2 ] && [ -e $2 ]; then
        BINARY=$2
else
        BINARY="./Wishful-application.rm090"
        echo "INFO: No binary specified, defaulting to $BINARY"
fi

N_NODES=`ls -l /dev/ttyUSB* | wc -l`
for (( i=0; i<$N_NODES; i++ ))
do
        echo "INFO: tos-set-symbols --objcopy msp430-objcopy --objdump msp430-objdump --target ihex $BINARY ./test_$[ i + NODE_ID ].ihex node_id=$[ i + NODE_ID ]"
        echo "INFO: ibcn-f5x-tos-bsl -c /dev/ttyUSB$i -5 -R --invert-reset --swap-reset-test -r -e -I -p ./test_$[ i + NODE_ID ].ihex&"
        tos-set-symbols --objcopy msp430-objcopy --objdump msp430-objdump --target ihex $BINARY ./test_$[ i + NODE_ID ].ihex node_id=$[ i + NODE_ID ]
        /groups/portable-ilabt-iminds-be/wishful/repos/contiki/tools/rm090/ibcn-f5x-tos-bsl -c /dev/ttyUSB$i -5 -R --invert-reset --swap-reset-test -r -e -I -p ./test_$[ i + NODE_ID ].ihex&
done
