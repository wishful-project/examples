#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
contiki_control_program_global.py: Example Contiki global control program

Usage:
   contiki_control_program_global.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./contiki_control_program_global -v --config ./config/localhost/control_program_global.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import sys
import datetime
import logging
from contiki.contiki_helpers.global_node_manager import *
import gevent
import wishful_upis as upis
import wishful_controller
import yaml

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

control_engine = wishful_controller.Controller()
global_node_manager = GlobalNodeManager(control_engine)

@control_engine.new_node_callback()
def new_node(node):
    global_node_manager.add_node(node)
    print("New node appeared:")
    print(node)

@control_engine.node_exit_callback()
def node_exit(node, reason):
    global_node_manager.remove_node(node)
    print("NodeExit : NodeID : {} MAC_ADDR : {} Reason : {}".format(node.id,mac_address_exit_list, reason))

@control_engine.set_default_callback()
def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

@control_engine.add_callback(upis.radio.set_rxchannel)
def set_channel_reponse(group, node, data):
    print("{} set_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

@control_engine.add_callback(upis.radio.get_rxchannel)
def get_channel_reponse(group, node, data):
    print("{} get_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

def main(args):

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)
    control_engine.load_config(config)
    control_engine.start()
    contiki_nodes = []

    #control loop
    while True:
        gevent.sleep(10)
        contiki_nodes = global_node_manager.get_mac_address_list()
        print("\n")
        print("Connected nodes", [str(node) for node in contiki_nodes])
        if contiki_nodes:
            #execute UPI function blocking
            global_node_manager.execute_upi_function("radio","set_parameters",contiki_nodes,{'IEEE802154_phyCurrentChannel':12})

            #schedule non-blocking UPI function with specific callback
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            global_node_manager.schedule_upi_function("radio","set_parameters",exec_time, contiki_nodes, print_response, {'IEEE802154_phyCurrentChannel':12})

            #delayed UPI function call with default callback
            global_node_manager.delay_upi_function("radio","set_parameters",3, contiki_nodes, {'IEEE802154_phyCurrentChannel':12})

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
    log = logging.getLogger('contiki_global_control_program')

    log.debug(args)

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_node_manager.control_engine.stop()
