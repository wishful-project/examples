#!/bin/bash
export PATH=$PATH:/opt/compilers/mspgcc-4.7.3/bin
if [ $# = 3 ] && [ -e $1 ]; then
        BINARY=$1
        NODE_ID=$2
        SERIAL_DEV=$3
        echo "INFO: tos-set-symbols --objcopy msp430-objcopy --objdump msp430-objdump --target ihex $BINARY ./test_$NODE_ID.ihex node_id=$NODE_ID"
        tos-set-symbols --objcopy msp430-objcopy --objdump msp430-objdump --target ihex $BINARY ./test_$NODE_ID.ihex node_id=$NODE_ID
        echo "INFO: ibcn-f5x-tos-bsl -c $SERIAL_DEV -5 -R --invert-reset --swap-reset-test -r -e -I -p ./test_$NODE_ID.ihex &"
        ./ibcn-f5x-tos-bsl -c $SERIAL_DEV -5 -R --invert-reset --swap-reset-test -r -e -I -p ./test_$NODE_ID.ihex &      
else
        echo "Wrong arguments: $BINARY,$NODE_ID,$SERIAL_DEV or PATH $PATH"
fi
