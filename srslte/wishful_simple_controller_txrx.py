#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
srsLTE Simple Example: Example tutorial of WiSHFUL (controller side)

Usage:
   wishful_simple_controller [options] [-q | -v]



Example:
   ./wishful_simple_controller_pair

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import datetime
import logging
import gevent
import os
import sys
import time
from itertools import cycle
import math


# WiSHFUL imports
import wishful_controller
import wishful_upis as upis
import wishful_module_srslte

__author__ = "Justin Tallon"
__copyright__ = "Copyright (c) 2017 Software Radio Systems Ltd."
__version__ = "0.1.0"
__email__ = "justin.tallon@softwareradiosystems.com"

"""
Setting of controller node
"""
controller_PC_IP_address = "192.168.5.64"
controller_PC_interface = "ens3"
"""
END setting of controller nodes
"""

DL_address = "tcp://" + controller_PC_IP_address + ":8990"
UL_address = "tcp://" + controller_PC_IP_address + ":8989"


""" START Define logging controller """
""" we use the python logging system module (https://docs.python.org/2/library/logging.html) """
log = logging.getLogger('wishful_controller')

#Create controller, we specify in the parameters the ip addresses and the ports used for downlink and uplink connection
#with the nodes tesbed, in this case we spcify the interface loopback and the port 8990 for the downlink and the
# interface loopback and the port 8989 for the uplink.
controller = wishful_controller.Controller(dl=DL_address, ul=UL_address)

#Configure controller, we specify in the parameters the controller name and a string information related to the
#controller
controller.set_controller_info(name="WishfulController", info="WishfulControllerInfo")

#add the discovery module, responsable for the nodes discovery procedure and nodes adding to the controllers
#we specify interface, the name of the nodes group, and the ip address and port for the downlink and uplink connection
controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
                      className="PyreDiscoveryControllerModule",
                      kwargs={"iface":controller_PC_interface, "groupName":"wishful_4321", "downlink":DL_address, "uplink":UL_address})
""" END the WiSHFUL controller setting """

# Global list with all nodes (agents) connected to this controller. We start empty and append nodes when they start.
# See new_node function below
nodes = []
TOTAL_NODES = 2 # We expect 2 nodes to connect: 'tx', and 'rx'.

@controller.new_node_callback()
def new_node(node):
    """ This function is performed when a new node has been found in the network

    :param node: finded node
    """
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
    # Safety check
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


@controller.add_callback(upis.radio.get_parameters)
def get_vars_response(group, node, data):
    """ This function implements a callback called when ANY get_* function is called in ANY of the nodes

    :param group: Experiment group name
    :param node: Node used to execute the UPI
    :param data: ::TODO::
    """
    print("{} get_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

def print_response(group, node, data):
    """ This function implements a callback to print generic UPI function calling result

    :param group: Experiment group name
    :param node: Node used to execute the UPI
    :param data: Execution time
    """
    print("\n{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))


# Entry point after globals initialization
if __name__ == '__main__':


    #Start controller
    controller.start()

    # We expect two agents (tx and rx).
    # Observation: we dont check if the agents connectict are in fact the ones that we want.
    while len(nodes) < TOTAL_NODES:
        print('-- Nodes connected: {}/{}'.format(len(nodes), TOTAL_NODES))
        gevent.sleep(2)

    print("All nodes connected. Starting Simple Experiment of wishful srs")


    running_enb = False
    #running_enb = controller.node(nodes[1]).radio.get_running_radio_program()
    if running_enb is False:

        print('\t- Starting program at TX Agent')
        controller.node(nodes[1]).radio.set_parameters({'IS_UE':False})
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_DL_FREQ': 2410000000})
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_RF_AMP': 0.8})
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_TX_GAIN': 20})
        #controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_NO_OF_FRAMES': 100000})
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_DL_BW': 25})
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_WHICH_PRBS': 0xFFFF})
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_MCS': 1})
        # set any static  parameters needed to be set here for the ENB
        controller.node(nodes[1]).radio.activate_radio_program('ENB')
    else:
        print('\t Agent TX is already running something. Please stop it first')

    gevent.sleep(10)
    running_ue = False
    running_ue = controller.node(nodes[0]).radio.get_running_radio_program()
    if running_ue is False:
        print('\t- Starting program at RX Agent')

        # set any static  parameters needed to be set here for the UE
        controller.node(nodes[0]).radio.set_parameters({'IS_UE':True})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_DL_FREQ': 2410000000})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_RX_GAIN': 30})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_N_RX_ANT': 1})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_EQUALIZER_MODE': 'mmse'})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_MAX_TURBO_ITS': 3})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_NOISE_EST_ALG': 0})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_SSS_ALGORITHM': 1})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_SNR_EMA_COEFF': 0.1})
        controller.node(nodes[0]).radio.set_parameters({'LTE_UE_CFO_TOL': 50})
        #now that our parameters are set we can start our radio, these parameters have default values so they do not HAVE to be set
        controller.node(nodes[0]).radio.activate_radio_program('UE')
    else:
        print('\t Agent RX is already running something. Please stop it first')

    gevent.sleep(20)


    # the following logic ensures the transmitter and receiver are on the same frequency
    vals = controller.node(nodes[0]).radio.get_parameters(['LTE_UE_DL_FREQ'])

    initial_cf_ue = vals['FREQ']

    vals = controller.node(nodes[1]).radio.get_parameters(['LTE_ENB_DL_FREQ'])
    initial_cf_enb = vals['FREQ']
    if initial_cf_enb != initial_cf_ue:
        controller.node(nodes[0]).radio.set_parameters({'FREQ': initial_cf_enb})

    gevent.sleep(10)



    meas = controller.node(nodes[0]).radio.get_measurements({'SNR'})
    snr = meas['SNR']
    print ('\t snr is \n', snr)
    gevent.sleep(2)
    if snr < 10:
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_TX_GAIN': 20})


    gevent.sleep(5)
    meas  =  controller.node(nodes[0]).radio.get_measurements({'PDSCH_MISS'})
    pdsch_miss = meas['PDSCH_MISS']
    print ('\t pdsch_miss is \n',pdsch_miss)
    gevent.sleep(2)
    if pdsch_miss < 5:
        param = controller.node(nodes[1]).radio.get_parameters(['LTE_ENB_MCS'])
        mcs = param['MCS']
        controller.node(nodes[1]).radio.set_parameters({'LTE_ENB_MCS': mcs + 2})

    gevent.sleep(30)

    meas = controller.node(nodes[0]).radio.get_measurements({'N_FRAMES'})
    n_frames = meas['N_FRAMES']
    print ('\t n_frames received  is \n', n_frames)

    controller.node(nodes[0]).radio.deactivate_radio_program('UE')
    controller.node(nodes[1]).radio.deactivate_radio_program('ENB')
    print('Controller Exiting')
    sys.exit()
