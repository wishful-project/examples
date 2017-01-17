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
                      kwargs={"iface":"enx8cae4cdf4e35", "groupName":"wishful_1234", "downlink":"tcp://192.168.5.55:8990", "uplink":"tcp://192.168.5.55:8989"})


nodes = {}
program_running = None
the_variables = {}

TOTAL_NODES = 1
NODE_NAMES = ["tx", "rx1", "rx2"]

conf = {

    # list of files that will be send to agents
    'files' : {
    	"tx" :   "/home/ctvr/wishful/gr-hydra/apps/video_benchmark_tx.py",
    	"rx1" :  "/home/ctvr/wishful/gr-hydra/apps/video_rx.py",
    	"rx2" :  "/home/ctvr/wishful/gr-hydra/apps/video_rx.py"
    },

    'program_getters' : {
        "tx":  ["svl_bandwidth", "svl_center_freq"],
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

    #if node.name not in NODE_NAMES:
    #    log.info("Node '%s' is not part of this showcase. Ignoring it" % (node.name, ))
    #else:
    if node.name == 'tx':
        program_name = node.name
        program_code = open(conf['files'][program_name], "r").read()
        program_args = conf['program_args'][node.name]

        controller.blocking(False).node(node).radio.iface('usrp').activate_radio_program({'program_name': program_name, 'program_code': program_code, 'program_args': program_args,'program_type': 'py'})

@controller.node_exit_callback()
def node_exit(node, reason):

    if node in nodes.values():
        if node.name == 'rx':
            program_running = None
        del nodes[node.name]

    log.info(("NodeExit : NodeID : {} Reason : {}".format(node.id, reason)))

@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    log.info("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))


@controller.add_callback(upis.radio.get_parameters)
def get_vars_response(group, node, data):
    log.info("{} get_vars_response : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

    #if node.name == 'rx1':
    if program_running == 'rx1':
        the_variables['rx1_pkt_rcv'] = data['pkt_rcvd'] if 'pkt_rcvd' in data else 'NA'
        the_variables['rx1_pkt_right'] = data['pkt_right'] if 'pkt_right' in data else 'NA'
        the_variables['rx1_center_freq'] = data['center_freq'] if 'center_freq' in data else 'NA'
        the_variables['rx1_bandwidth'] = data['bandwidth'] if 'bandwidth' in data else 'NA'
    elif program_running == 'rx2':
    #elif node.name == 'rx2':
        the_variables['rx2_pkt_rcv'] = data['pkt_rcvd'] if 'pkt_rcvd' in data else 'NA'
        the_variables['rx2_pkt_right'] = data['pkt_right'] if 'pkt_right' in data else 'NA'
        the_variables['rx2_center_freq'] = data['center_freq'] if 'center_freq' in data else 'NA'
        the_variables['rx2_bandwidth'] = data['bandwidth'] if 'bandwidth' in data else 'NA'

    pickle.dump(the_variables, open("./getter.bin", "wb"))

def exec_loop():
    global program_running

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
            if 'tx' in nodes:
                log.info("Requesting data to VR TX")
                controller.blocking(False).node(nodes['tx']).radio.iface('usrp').get_parameters(conf['program_getters']['tx'])

            if 'rx' in nodes and program_running != None:
                log.info("Requesting data to VR %s" % (program_running, ))
                controller.blocking(False).node(nodes['rx']).radio.iface('usrp').get_parameters(conf['program_getters'][program_running])


            # set variables
            setters = {}
            try:
                setters = pickle.load(open(SETTER_FILE, "rb"))
                pickle.dump({}, open(SETTER_FILE, "wb"))
            except Exception as e:
                log.info("Could not open setters file")
                log.info(e)

            log.info(setters)

            if 'tx' in setters.keys() and 'tx' in nodes:
                    log.info("Setting configuration of node TX") 
                    controller.blocking(False).node(nodes['tx']).radio.iface('usrp').set_parameters(setters['tx'])

            if 'rx1' in setters.keys() and program_running == 'rx1':
                    log.info("Setting configuration of node RX1") 
                    controller.blocking(False).node(nodes['rx']).radio.iface('usrp').set_parameters(setters['rx1'])
            if 'rx2' in setters.keys() and program_running == 'rx2':
                    log.info("Setting configuration of node RX2") 
                    controller.blocking(False).node(nodes['rx']).radio.iface('usrp').set_parameters(setters['rx2'])

            if 'vr' in setters.keys() and program_running != setters['vr'] and 'rx' in nodes:
                    if program_running != None:
                        controller.blocking(False).node(nodes['rx']).radio.iface('usrp').deactivate_radio_program(program_name)

                    program_name = setters['vr']
                    program_code = open(conf['files'][program_name], "r").read()
                    program_args = conf['program_args'][program_name]
                    controller.blocking(False).node(nodes['rx']).radio.iface('usrp').activate_radio_program({'program_name': program_name, 'program_code': program_code, 'program_args': program_args,'program_type': 'py'})


                    program_running = program_name

            gevent.sleep(2)

    log.info("All nodes disconnected. Exiting controller")
    controller.stop()

if __name__ == '__main__':
    exec_loop()
