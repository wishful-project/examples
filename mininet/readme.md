# Wishful controller example in Mininet-WiFi

## Setup phase
### Install Mininet-Wifi

    git clone https://github.com/intrig-unicamp/mininet-wifi
    cd mininet-wifi
    sudo util/install.sh -Wnfv

Stop the network manager, i.e. 
    sudo service network-manager stop

### Install Wishful wrapper for Python2
    cd wishful/
    sudo pip2 install -U ./mininet/

## Run the example
    cd wishful/examples/mininet
    sudo python2 ./mininet_script.py

Open new terminal to see the output of the controller:

    tail -f /tmp/controller_ap1.log

![mn_example](./mn_example.png)