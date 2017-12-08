#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path
   --nodes nodesFile   Config file with node info

Example:
   python global_cp.py --config config/portable/global_cp_config.yaml --nodes config/portable/nodes.yaml

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
import yaml

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')

def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

def main(args):
    contiki_nodes = []
    #control loop
    while True:
        contiki_nodes = global_node_manager.get_mac_address_list()
        print("\n")
        print("Connected nodes", [str(node) for node in contiki_nodes])
        if contiki_nodes:
            #execute UPI function blocking
            ret = global_node_manager.execute_upi_function("radio","set_parameters",contiki_nodes,{'IEEE802154_phyCurrentChannel':12})
            print("{}".format(ret))
            #schedule non-blocking UPI function with specific callback
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            global_node_manager.schedule_upi_function("radio","get_parameters",exec_time, contiki_nodes, None, ['IEEE802154_phyCurrentChannel'])
            gevent.sleep(5)
            #delayed UPI function call with default callback
            global_node_manager.delay_upi_function("radio","set_parameters",3, contiki_nodes, None,{'IEEE802154_phyCurrentChannel':13})
            gevent.sleep(5)
            #schedule non-blocking UPI function with specific callback
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            global_node_manager.schedule_upi_function("radio","get_parameters",exec_time, contiki_nodes, print_response, ['IEEE802154_phyCurrentChannel'])
            
        gevent.sleep(10)

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

    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    global_node_manager = GlobalNodeManager(config)
    global_node_manager.set_default_callback(default_callback)
    global_node_manager.add_callback(upis.radio.get_parameters,print_response)

    nodes_file_path = args['--nodes']
    with open(nodes_file_path, 'r') as f:
        node_config = yaml.load(f)
    global_node_manager.wait_for_agents(node_config['ip_address_list'])

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_node_manager.stop()
