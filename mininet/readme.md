# Wishful controller example in Mininet-WiFi

## Setup phase
### Install Mininet-Wifi

    git clone https://github.com/intrig-unicamp/mininet-wifi
    cd mininet-wifi
    sudo util/install.sh -Wnfv

Stop the network manager, i.e. 
    sudo service network-manager stop

### Install Wishful as global library ###
    cd wishful
    sudo pip3 install -U -r ./.repo/manifests/requirements_dev.txt

### Install Wishful wrapper for Python2
    cd wishful/
    sudo pip2 install -U ./mininet/

## Run the example
    cd wishful/examples/mininet
    ./run.sh

Open new terminal to see the output of the controller:

    tail -f /tmp/ctrl.log

and the two agents:
    tail -f /tmp/ap1.log
    tail -f /tmp/ap2.log

![mn_example](./mn_example.png)
