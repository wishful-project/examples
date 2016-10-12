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
   --nr-ip-address nrIP Node Red IP address
   --nr-port nrPort     Node Red port

Example:
   python global_cp.py --config config/portable/global_cp_config.yaml --nodes config/portable/nodes.yaml --nr-ip-address 172.16.16.1 --nr-port 55555

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
import jsonSocket

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')

def parse_node_red_command(json_server, nr_command, node_manager):
    if 'execute_upi_function' in nr_command:
        nr_exec_upi_func = nr_command['execute_upi_function']
        upi_type = nr_exec_upi_func['upi_type']
        upi_func = nr_exec_upi_func['upi_func']
        node_list = nr_exec_upi_func['node_list']
        upi_func_args = nr_exec_upi_func['args']
        ret_val = node_manager.execute_upi_function(upi_type, upi_func, node_list,args=upi_func_args)
        json_ret = { 'execute_upi_function' : {'upi_type': upi_type, "upi_func": upi_func, "node_list": node_list, 'ret_val' : ret_val}}
        json_server.send_obj({'payload': json_ret})

class MyFactoryThread(jsonSocket.ServerFactoryThread):
    # This is an example factory thread, which the server factory will
    # instantiate for each new connection.
    def __init__(self):
        super(MyFactoryThread, self).__init__()
        self.timeout = 2.0

    def _process_message(self, obj):
        # virtual method - Implementer must define protocol
        if obj != '' and type(obj) is dict:
            parse_node_red_command(self, obj['payload'], global_node_manager)

def main(args):
    contiki_nodes = []
    #~ jsocket_server = jsonSocket.JsonServer(args['--nr-ip-address'], int(args['--nr-port']))
    jsocket_server = jsonSocket.ServerFactory(MyFactoryThread, address=args['--nr-ip-address'], port=int(args['--nr-port']))
    jsocket_server.timeout = 2.0
    jsocket_server.start()
    while True:
        time.sleep()

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
