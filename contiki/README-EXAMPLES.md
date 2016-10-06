# WiSHFUL Contiki Examples

This files lists all the available examples and provides instructions for configuring the contiki nodes and WiSHFUL system correctly.

## Setting up the WiSHFUL system
Make sure you have followed the instructions on http://doc.ilabt.iminds.be/ilabt-documentation/wilabfacility.html#using-the-wishful-framework for installing the framework.

On each Linux host PC activate the virtual environment, switch to the correct branches and update the virtual environment:
```
cd wishful
./repo sync
source dev/bin/activate
cd controller
git checkout dev_iminds
cd upis
git checkout dev_iminds
pip3 install -U -r ./.repo/manifests/requirements.txt
cd examples/contiki
```

## Configuring the sensors
The UPIs are currently implemented only on RM-090 sensors with a modified Contiki image.
### RM-090
Make shure the correct image is flashed on each of the RM-090. 
The `flash_nodes_<TESTBED>.sh` script is used for assigning flashing the sensor nodes and asigning the node id.
```
cd binaries/
./flash_nodes 1 <BINARY>
```
Known caveats:
 - ensure that your linux user is member of the dialout group
 - when assigning node ids check the number of nodes / linux host.

#### Zolertia Remote (rev a)
Coming soon.

