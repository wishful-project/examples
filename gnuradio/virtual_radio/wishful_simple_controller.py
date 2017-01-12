#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import wishful_controller
import gevent
import wishful_upis as upis
import os
import sys
import time
import pickle
import wishful_module_gnuradio

__author__ = "Maicon Kist"
__copyright__ = "Copyright (c) 2017 Connect Centre - Trinity College Dublin" 
__version__ = "0.1.0"
__email__ = "kistm@tcd.ie"


log = logging.getLogger('wishful_controller')
log_level = logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

#Create controller
# ::TRICKY:: update IP addresses to external interface
controller = wishful_controller.Controller(dl="tcp://192.168.5.55:8990", ul="tcp://192.168.5.55:8989")

#Configure controller
controller.set_controller_info(name="WishfulController", info="WishfulControllerInfo")
# ::TRICKY:: update IP addresses to external interface
controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
                      className="PyreDiscoveryControllerModule",
                      kwargs={"iface":"ens3", "groupName":"wishful_1234", "downlink":"tcp://192.168.5.55:8990", "uplink":"tcp://192.168.5.55:8989"})


nodes = {}
the_node = None
the_variables = {}

TOTAL_NODES = 1
NODE_NAMES = ["tx", "rx1", "rx2"]

conf = {

    # list of files that will be send to agents
    'files' : {
    "tx" : 	"/home/nodeuser/gr-hydra/apps/video_benchmark_tx.py",
    "rx1" :  "/home/nodeuser/gr-hydra/apps/video_rx.py",
    "rx2" :  "/home/nodeuser/gr-hydra/apps/video_rx.py"
    },

    # What code each node will execute. Node 0 is TX, Node 1 is RX
    'nodes_to_program' : {
        "tx" : "tx",
        "rx1": "rx", 
        "rx2": "rx", 
    },

    'program_getters' : {
        "tx": ["svl_bandwidth", "svl_center_freq"],
        "rx1": ["bandwidth", "center_freq", "pkt_rcvd", "pkt_right", ],
        "rx2": ["bandwidth", "center_freq", "pkt_rcvd", "pkt_right", ],
    },

    'program_args': {
        "tx": ["",], 
        "rx1": ["",],
        "rx2": ["--vr-configuration", "2"],
    },


}


# for the svl tx
SVL_TX_BANDWIDTH = 'svl_bandwidth'
SVL_TX_CENTER_FREQ = 'svl_center_freq'
VR_TX_GAIN = 'vr{id}_gain'

# for the receivers only
RX_BANDWIDTH = 'bandwidth'
RX_CENTER_FREQ = 'center_freq'
RX_GAIN = 'gain'

SETTER_FILE = "./setter.bin"


@controller.new_node_callback()
def new_node(node):
    log.info("New node appeared: Name: %s" % (node.name, ))
    nodes[node.name] = node


    if node.name not in NODE_NAMES:
        log.info("Node '%s' is not part of this showcase. Ignoring it" % (node.name, ))
    else:
        program_name = node.name
        program_code = open(conf['files'][program_name], "r").read()
        program_args = conf['program_args'][node.name]

        controller.blocking(False).node(node).radio.iface('usrp').activate_radio_program({'program_name': program_name, 'program_code': program_code, 'program_args': program_args,'program_type': 'py'})

@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes.values():
        del nodes[node.name]
    log.info(("NodeExit : NodeID : {} Reason : {}".format(node.id, reason)))

@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    log.info("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))


@controller.add_callback(upis.radio.get_parameters)
def get_vars_response(group, node, data):
    log.info("{} get_vars_response : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

    if node.name == 'rx1':
        the_variables['rx1_pkt_rcv'] = data['pkt_rcvd'] if 'pkt_rcvd' in data else 'NA'
        the_variables['rx1_pkt_right'] = data['pkt_right'] if 'pkt_right' in data else 'NA'
        the_variables['rx1_center_freq'] = data['center_freq'] if 'center_freq' in data else 'NA'
        the_variables['rx1_bandwidth'] = data['bandwidth'] if 'bandwidth' in data else 'NA'
    elif node.name == 'rx2':
        the_variables['rx2_pkt_rcv'] = data['pkt_rcvd'] if 'pkt_rcvd' in data else 'NA'
        the_variables['rx2_pkt_right'] = data['pkt_right'] if 'pkt_right' in data else 'NA'
        the_variables['rx2_center_freq'] = data['center_freq'] if 'center_freq' in data else 'NA'
        the_variables['rx2_bandwidth'] = data['bandwidth'] if 'bandwidth' in data else 'NA'

    pickle.dump(the_variables, open("./getter.bin", "wb"))

def exec_loop():
    #Start controller
    controller.start()

    running = False
    first_time = True

    while len(nodes) < TOTAL_NODES:
    # Waiting for 2 nodes
        log.info("%d nodes connected. Waiting for %d more" % (len(nodes), TOTAL_NODES - len(nodes)))
        gevent.sleep(2)

    log.info("All nodes connected. Starting showcase...")

    #control loop
    while nodes:
            # TRICKY: gets are assynchronous. callback for get_parameters is called automatically
            for node in nodes.keys():
                log.info("Requesting data to VR %s" % (node))
                controller.blocking(False).node(nodes[node]).radio.iface('usrp').get_parameters(conf['program_getters'][node])

            # set variables
            setters = pickle.load(open(SETTER_FILE, "rb"))
            for node in setters.keys():
                if node in nodes:
                    log.info("Setting configuration of node %s" % (node, )) 
                    controller.blocking(False).node(nodes[node]).radio.iface('usrp').set_parameters(setters[node])
                else:
                    log.info("Node %s not connected. Skipping setting" % (node, )) 

            gevent.sleep(2)

    log.info("All nodes disconnected. Exiting controller")
    controller.stop()

if __name__ == '__main__':
    exec_loop()
