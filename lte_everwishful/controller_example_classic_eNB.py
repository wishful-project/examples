#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import types
import sys
import time
import datetime
import logging
import gevent
import threading
from multiprocessing import Process 

sys.path.append('../../')
sys.path.append("../../agent_modules/module_lte")
sys.path.append('../../upis')
sys.path.append('../../framework')
sys.path.append('../../agent')

import wishful_controller
import wishful_upis as upis
import wishful_upis.lte.meta_radio as radio
import wishful_upis.lte.meta_net as net

__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

"""
Setting of experiment nodes, ip address and name
"""
#Controller (UP-Board_2)
controller_PC_ip_address = "10.30.2.59"
controller_PC_interface = "eth1"

# EPC
epc_name = "UP-Board 1"
epc_ip = "10.30.2.56"
epc_interface = "enx00909e9f9f46"

# eNB/RRU
enb_name = "Wilson" 
enb_ip = "10.30.2.58"
enb_interface = "eth4"

#UE
ue_name = "Kote"
ue_ip = "10.30.2.98"
ue_interface = "eth0"

#Nodes number
nodes_number=3
group_name = "lte_example"


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
#set the logging name
log = logging.getLogger('wishful_controller')
logLevel = logging.INFO
logging.basicConfig(level=logLevel, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

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

def setHSS(controller, node):
    """ This function use WiSHFUL UPI functions to perform an
    :param controller: framework controller object
    :param node:
    """
    #This UPI function stops the HSS
    controller.blocking(False).node(node).net.HSS_deactivation()
    gevent.sleep(5)
    #This UPI function starts the HSS
    controller.delay(3).node(node).net.HSS_activation()
    gevent.sleep(5)

def setMME(controller, node):
    """ This function use WiSHFUL UPI functions to perform an
    :param controller: framework controller object
    :param node:
    """
    #This UPI function stops the MME
    controller.blocking(False).node(node).net.MME_deactivation()
    gevent.sleep(5)
    #This UPI function starts the MME
    controller.delay(13).node(node).net.MME_activation()
    gevent.sleep(5)

def setSPGW(controller, node):
    """ This function use WiSHFUL UPI functions to perform an
    :param controller: framework controller object
    :param node:
    """
    #This UPI function stops the SPGW
    controller.blocking(False).node(node).net.SPGW_deactivation()
    gevent.sleep(5)
    #This UPI function starts the SPGW
    controller.delay(23).node(node).net.SPGW_activation()
    gevent.sleep(5)

def setENB(controller, node):
    """ This function use WiSHFUL UPI functions to
    :param controller: framework controller object
    :param node:
    :return
    """
    #This UPI function stops the eNB
    controller.blocking(False).node(node).net.eNB_deactivation()
    gevent.sleep(5)
    #This UPI function starts the eNB
    controller.delay(33).node(node).net.eNB_activation()
    gevent.sleep(5)

def setUE(controller, node):
    """ This function use WiSHFUL UPI functions
    :param controller: framework controller object
    :param node:
    :return connected:
    """
    #This UPI function stops the UE
    controller.blocking(False).node(node).net.UE_deactivation()
    gevent.sleep(5)
    #This UPI function starts the eNB
    controller.delay(43).node(node).net.UE_activation()
    gevent.sleep(5)

def RUNping(controller, ip_address):
    """ This function use WiSHFUL UPI functions to
    :param controller: framework controller object
    :param node:
    :return
    """

    #This UPI function stops the eNB, if present on node#
    #rvalue = controller.nodes(node).net.ping_test()
    pass

def main():

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

            print('nodes %s' % str(nodes))
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
                if nodes[ii].ip == enb_ip:
                    enb_node = nodes[ii]
                if nodes[ii].ip == ue_ip:
                    ue_node = nodes[ii]
            if epc_node == None and enb_node == None and ue_node == None :
                print("Experiment nodes found, however the reported ip address do not match, please check the setting ip address, the interface and the group name")
                break

            """
            This part of the controller performs a LTE network
            """
            #UPIargs_EPC = {net.MME_REALM.key: 'prova'}
            #result = controller.node(epc_node).radio.set_parameters(UPIargs_EPC)

			#UPIargs_eNB = {radio.TX_GAIN_enb.key: 10, radio.RX_GAIN_enb.key: 15}
            #result = controller.node(enb_node).radio.set_parameters(UPIargs_eNB)

            setHSS(controller,epc_node)
            setMME(controller,epc_node)
            setSPGW(controller,epc_node)
            time.sleep(10)
            setENB(controller,enb_node)
            time.sleep(10)
            setUE(controller,ue_node)
            do_run = True            
            EXPERIMENT_DURATION = 200
            dt = 0
            while do_run:
                log.warning('waiting for ... (%d sec / %d)' % (dt, EXPERIMENT_DURATION) )
                dt += 1
                gevent.sleep(1) 
            break

try:
    main()
except KeyboardInterrupt:
    log.debug("Controller exits")
finally:
    log.debug("Exit")
    controller.stop()
