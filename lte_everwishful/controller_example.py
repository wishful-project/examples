#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
wmp_example_tutorial_controller: Example tutorial of WiSHFUL (agent side)
Usage:
   wmp_example_tutorial_controller [options] [-q | -v]
Options:
   --logfile name      Name of the logfile
   --config configFile Config file path
Example:
   ./wishful_example_tutorial_controller -v --config ./config.yaml
Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
import types
import sys
import time
import datetime
import logging
import gevent

sys.path.append('../../')
sys.path.append("../../agent_modules/module_lte")
sys.path.append('../../upis')
sys.path.append('../../framework')
sys.path.append('../../agent')

import wishful_controller
import wishful_upis as upis

__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

"""
Setting of experiment nodes, ip address and name
"""
#Controller (UP-Board_2)
controller_PC_ip_address = "10.30.2.149"
controller_PC_interface = "eth0" 

# EPC
epc_name = "UP-Board 1"
epc_ip = "10.30.2.56"
epc_interface = "enx503f56020469"

## RCC
#rcc_name = "Jean 2"
#rcc_ip = "10.30.2.57" 
#rcc_interface = "eth5"

# eNB/RRU
enb_name = "Wilson" 
enb_ip = "10.30.2.58"
enb_interface = "eth0"

#UE
ue_name = "Kote" #to check
ue_ip = "10.30.2.98" #to check
ue_interface = "eth0" #to check

#Nodes number
nodes_number=3

"""
END setting of experiment nodes
"""



""" START the WiSHFUL controller setting """
"""
The WiSHFUL controller module is the core module of the WiSHFUL framework and allow all the basics functions
such as the node discovery, the UPI functions execution on local and remote node, perform the messages exchange between
global control program and local control program, and all the other management functions of the framework. The different
works of the controller are  performed by different module can be added on demand in the controller
"""

#Create controller, we specify in the parameters the ip addresses and the ports used for downlink and uplink connection
#with the nodes tesbed, in this case we spcify the interface loopback and the port 8990 for the downlink and the
# interface loopback and the port 8989 for the uplink.
controller = wishful_controller.Controller(dl="tcp://"+controller_PC_ip_address+":8990", ul="tcp://"+controller_PC_ip_address+":8989")

#Configure controller, we specify in the parameters the controller name and a string information related to the
#controller
controller.set_controller_info(name="WishfulController", info="WishfulControllerInfo")

#the following rows add all the needed modules to the controller

#add the discovery module, responsable for the nodes discovery procedure and nodes adding to the controllers
#we specify interface, the name of the nodes group, and the ip address and port for the downlink and uplink connection
controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
                      className="PyreDiscoveryControllerModule", 
                      kwargs={"iface":controller_PC_interface, "groupName":group_name, "downlink":"tcp://"+controller_PC_ip_address+":8990", "uplink":"tcp://"+controller_PC_ip_address+":8989"})

""" END the WiSHFUL controller setting """

""" START Define logging controller """
""" we use the python logging system module (https://docs.python.org/2/library/logging.html) """

#set the logging name
log = logging.getLogger('wishful_controller')

""" END Define logging controller """


#experiment nodes list
nodes = []

@controller.new_node_callback()
def new_node(node):
    """ This function is performed when a new node has been found in the network
    :param node: finded node
    """
    #the found node is added to the controller nodes list
    nodes.append(node)
    print("New node appeared:")
    print(node)

@controller.node_exit_callback()
def node_exit(node, reason):
    """ This function is performed when a node, present in the controller node list, leave the experiment. During the
    experiment, the nodes send "hello packet" to the controller. If the controller do not receives hello packet from a node
    present in the node list, perform this function and the node is been removed
    :param node: node that leave the experiment
    :param reason : exit reason
    """
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


def setEPC(controller, node):
    """ This function use WiSHFUL UPI functions to perform an

    :param controller: framework controller object
    :param node:
    """
    # start epc
    pass

def setENB(controller, node):
    """ This function use WiSHFUL UPI functions to
    :param controller: framework controller object
    :param node:
    :return
    """
    # start eNB
    pass

def setUE(controller, node):
    """ This function use WiSHFUL UPI functions
    :param controller: framework controller object
    :param node:
    :return connected:
    """
    # start UE
    pass


def main(args):

    #start the controller
    controller.start()

    #list with information about platform type and radio capabilities for experiment nodes
    nodes_platform_info = None

    #control loop
    while True:
        gevent.sleep(5)

        #Print the currently connected nodes
        print("\nConnected nodes", [str(node.name) for node in nodes])

        #Check if all nodes are present in the experiment
        if len(nodes) == nodes_number:

            """
            This part of controller assigns the correct role for any experiment node finded
            """
            epc_node = None
            enb_node = None
            ue_node= None
            #Find experiment nodes role
            for ii in range(0, len(nodes)):
                if nodes[ii].ip == epc_ip:
                    epc_node = nodes[ii]
                if nodes[ii].ip == epc_ip:
                    enb_node = nodes[ii]
                if nodes[ii].ip == ue_ip:
                    ue_node = nodes[ii]
            if epc_node == None and enb_node == None and ue_node == None :
                print("Experiment nodes found, however the reported ip address do not match, please check the setting ip address, the interface and the group name")
                break

            """
            This part of the controller performs a LTE network
            """

            #execute blocking function immediately
            result = controller.node(enb_node).radio.set_parameters(parameter_enb)
            result = controller.node(ue_node).radio.set_parameters(parameter_ue)

            break


if __name__ == "__main__":
    try:
        from docopt import docopt
    except:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise

    #get program arguments
    args = docopt(__doc__, version=__version__)

    """ START Configure logging controller """
    """ we use the python logging system module (https://docs.python.org/2/library/logging.html) """

    #set the logging level
    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR
    #set the logging format
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    """ END Define logging controller """

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()