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

import threading

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

TOTAL_NODES = 2
NODE_NAMES = ["tx", "rx1", "rx2"]

# list of files that will be send to agents
files = {
    "tx" : 	"/home/nodeuser/gr-hydra/apps/video_benchmark_tx.py",
    "rx" :  "/home/nodeuser/gr-hydra/apps/video_rx.py"
}

# What code each node will execute. Node 0 is TX, Node 1 is RX
nodes_to_program = {
    "tx" : "tx",
    "rx1": "rx", 
    "rx2": "rx", 
}

program_getters = {
    "tx": ["svl_bandwidth", "svl_center_freq"],
    "rx": ["bandwidth", "center_freq", "pkt_rcvd", "pkt_right", ],
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
    log.info("New node appeared:")
    log.info(node)
    nodes[node.name] = node

@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes.values():
        del nodes[nodes.name]

    log.info(("NodeExit : NodeID : {} Reason : {}".format(node.id, reason)))

@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    log.info("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))


@controller.add_callback(upis.radio.get_parameters)
def get_vars_response(group, node, data):
    log.info("{} get_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

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


    pickle.dump(the_variables, open('controller_data.bin', 'wb'))

def exec_loop():
    # open files, read content, keep it in codes dict
    program = {}
    for _k, _v in files.items():
        with open(_v, "r") as fid:
            program[_k] = fid.read()

    #Start controller
    controller.start()

    running = False
    first_time = True

    while len(nodes) < TOTAL_NODES:
    # Waiting for 2 nodes
        log.info("%d nodes connected. Waiting for %d more" % (len(nodes), TOTAL_NODES - len(nodes)))
        gevent.sleep(2)

    log.info("All nodes connected. Starting showcase...")

    for node in nodes.values():
        if node.name not in NODE_NAMES:
            log.info("Node '%s' is not part of this showcase. Ignoring it" % (node.name, ))

        else:
            program_name = nodes_to_program[node.name]
            program_code = program[program_name] 

            controller.blocking(False).node(node).radio.iface('usrp').activate_radio_program({'program_name': program_name, 'program_code': program_code, 'program_type': 'py'})

    #control loop
    while nodes:
            # TRICKY: gets are assynchronous. callback for get_parameters is called automatically

            if 'rx1' in nodes:
                log.info("Requesting values to VR 1 RX")
                controller.blocking(False).node(nodes['rx1']).radio.iface('usrp').get_parameters(program_getters['rx'])

            if 'rx2' in nodes:
                log.info("Requesting values to VR 2 RX")
                controller.blocking(False).node(nodes['rx2']).radio.iface('usrp').get_parameters(program_getters['rx'])

            try:
                setters = pickle.load(open(SETTER_FILE, "rb"))

                if 'tx' in setters:
                    log.info("Setting values to SVL")
                    controller.blocking(False).node(nodes['tx']).radio.iface('usrp').set_parameters(setters['tx'])
                if 'rx1' in setters:
                    log.info("Setting values to VR 1 RX")
                    controller.blocking(False).node(nodes['rx1']).radio.iface('usrp').set_parameters(setters['rx1'])
                if 'rx2' in setters:
                    log.info("Setting values to VR 1 RX")
                    controller.blocking(False).node(nodes['rx2']).radio.iface('usrp').set_parameters(setters['rx2'])

            except Exception as e:
                log.info("setters file for vr1 not found. Nothing to change" )
                log.info(e)

            """
            if running:
                print("Deactivating program %s" % (program_name, ))
                #controller.blocking(False).node(nodes[0]).radio.iface('usrp').deactivate_radio_program({'program_name': program_name})
                running = False
            else:
                print("Activating program %s" % (program_name, ))
                #controller.blocking(False).node(nodes[0]).radio.iface('usrp').activate_radio_program({'program_name': program_name})
                running = True
            """
            gevent.sleep(2)

    log.info("All nodes disconnected. Exiting controller")
    controller.stop()

if __name__ == '__main__':
    exec_loop()
