#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
unite_controller_simple.py

Usage:
   unite_controller_simple.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./unite_simple_local_controller -v --config ./config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import sys
import datetime
import logging
import random
import wishful_controller
import gevent
import yaml
import wishful_upis as upis

# import file that will be sent to node
from unite_local_control_program import my_local_control_program
from libunite.clustalgos import build_centroids, check_centroids_status

__author__ = "Kostas Kolomvatsos"
__copyright__ = "Copyright (c) 2015, Department of Informatics and Telecommunications, UoA"
__version__ = "0.1.0"
__email__ = "kostasks@di.uoa.gr"


MAIN_LOOP_SLEEP = 10
TIME_FOR_NODE_CALCULATIONS = 1


log = logging.getLogger('wishful_agent.main')
controller = wishful_controller.Controller()
nodes = []

@controller.new_node_callback()
def new_node(node):
    nodes.append(node)
    print("New node appeared:")
    print(node)


@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    print("DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(group, node.name, cmd, data))


def main(args):
    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    controller.load_config(config)
    controller.start()
    SERVER_FLAG = False
    NUMBER_OF_NODES = 1

    #main loop
    while True:
        print("\nUNITE --> Connected nodes", [str(node.name) for node in nodes])
        lcpDescriptors = []
        initial_measurements = []
        received = False
        if nodes:
            if not SERVER_FLAG:
                ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
                print("Set Border Router -> ", ret)
                ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").set_parameters_net({'app_activate': 1, "app_payload_length": 100})
                print("Server Node -> ", ret)
                SERVER_FLAG = True
            if NUMBER_OF_NODES != len(nodes):
                new_nodes = len(nodes) - NUMBER_OF_NODES
                for node in nodes[-new_nodes:]:
                    ret = controller.blocking(True).node(node).net.iface("lowpan0").set_parameters_net({'app_activate': 2, "app_payload_length": 100})
                    print("Client Node -> ", ret)
                NUMBER_OF_NODES = len(nodes)
            print("Creating & Append a lcpDescriptor")
            for node in nodes:
                lcpDescriptor = controller.node(node).hc.start_local_control_program(program=my_local_control_program)
                lcpDescriptors.append(lcpDescriptor)
                gevent.sleep(TIME_FOR_NODE_CALCULATIONS)
                msg = lcpDescriptor.recv(timeout=7)
                if msg:
                    initial_measurements.append({ "lcpDescriptor" : lcpDescriptor , "value" : msg['PoV']})

        if  len(nodes) > 1:
            centroids =  build_centroids([d['value'] for d in initial_measurements])
            affected_values = check_centroids_status(centroids, initial_measurements, 0.5)
            print("Number of affected Nodes: ", len(affected_values))
            print("Number of Clusters: ", len(centroids))
            for affected_value in affected_values:
                print("Send message to change payload")
                affected_value['lcpDescriptor'].send({"decrease_payload": 1})
            ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").get_measurements_net(['app_stats'])
            pdr = 0
            if (ret['app_stats'][0]+ret['app_stats'][1]) != 0:
                pdr = ret['app_stats'][0] / (ret['app_stats'][0]+ret['app_stats'][1])
            print("PDR -->", pdr)
        # Close descriptors
        for lcpDescriptor in lcpDescriptors:
            lcpDescriptor.close()
        print("Receive all POI from nodes, Time to Sleep")
        gevent.sleep(MAIN_LOOP_SLEEP)


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

    args = docopt(__doc__, version=__version__)

    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
