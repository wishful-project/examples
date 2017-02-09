Wishful EXAMPLE TUTORIAL
============================

For any information or issue, please contact Domenico Garlisi at domenico.garlisi@cnit.it

The goal of this experiment is to create an example tutorial for the WiSHFUL framework and the UPI functions usage.
Specifically, this experiment uses the WiSHFUL framework and the UPI functions to set-up a wireless WiFi network and
change nodes radio program and parameters. All the UPI functions used in this example tutorial are fully documented at
link https://wishful-project.github.io/wishful_upis/ and this example tutorial can be found at the link
https://github.com/wishful-project/examples

We want to demonstrate how the WISHFUL UPI can be exploited for:
i) Create a network topology with two nodes, an Access Point (AP) and a connected station (STA);
ii) Show how use the UPI functions to tune the nodes parameters;
iii) Switch from a carrier sense multiple access to a time-division access protocol;

In order to implement the experiment, we run a controller program, or WiSHFUL controller, on a PC connected through
ethernet links to all nodes, and a common agent program in any node.
The controller program permits to: (i) discovery network nodes, (ii) install the execution environment, (iii) create the
BSS infrastructure and associate stations to the access point. In additional, the WiSHFUL controller executes the logic
for controlling the experiment, where we distinguish two phases: first tuning parameters of a radio program,
second switching between CSMA radio programs (enabled by default) and TDMA radio program.

The present example tutorial has been tested on WMP platform nodes present in the w-ilab.t.

In order to better understand all the phases of the this example tutorial and the single UPI function usage, we add
inline comment to both controller and agent programs.

This example tutorial is composed of two main python programs and other 3 additional script and configuration files.
The python programs are i) wishful_example_tutorial_agent that runs the agent in the experiment nodes, and
ii) wishful_example_tutorial_controller that runs on experiment PC and performs experiment actions.

### Experiment nodes selection and interface configuration
Both, wishful_example_tutorial_controller and wishful_example_tutorial_agent contains a setting part, that must been
setted with the experiment nodes and PC information. For each node is needed reporting ip, name and interface.
An example of configuration is reported below.

"""
Setting of experiment nodes, ip address and name
"""
#PC
controller_PC_ip_address = "172.16.0.100"
controller_PC_interface = "eth4"

# AP
ap_name = "node0"
ap_ip = "172.16.0.9"
ap_wlan_interface = "wlan0"

# STA
sta_name = "node1"
sta_ip = "172.16.0.12"
sta_wlan_interface = "wlan0"

#Nodes number
nodes_number=2

# BSSID of our Network
network_bssid = "wishful_example_tutorial"
group_name = "example_tutorial"

"""
END setting of experiment nodes
"""

### WORKING WITH EMULAB
reserve all the ALIX nodes and two SERVER (SERVER3 + SERVER15)
swap in the experiment alix-wishful (https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=alix-wishful)

connect to controller PC [from ops.wilab2.ilabt.iminds.be]
SHELL 1 - CONTROLLER PC :
    ssh YOUR_USER@alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        run command to set speed alixnode network
        sudo ethtool -s eth4 speed 100 duplex full

### 2. Starting agents
Start the agent on each node to be controlled (AP and STA).
To run it, user has to execute command:

```
./wishful_example_tutorial_agent
#run with -v for debugging
```

### 3. Starting the controller
Starting the controller on a PC connected through ethernet links to all nodes.
To run it, user has to execute command:

```
./wishful_example_tutorial_controller
#run with -v for debugging
```

NB:
In order to setup the testbed and move all relevant files on nodes, the experiment contains two bash script:
1)  sync_date.sh that performs the time syncronization of the network nodes.
2)  deploy_upis.sh that performs the files syncronization


## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
