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
import wishful_controller
import gevent

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

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

    def main(args):

        config_file_path = args['--config']
        global_node_manager = GlobalNodeManager(config_file_path)
        contiki_nodes = []

        @global_node_manager.control_engine.set_default_callback()
        def default_callback(group, node, cmd, data):
            print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

        @global_node_manager.control_engine.add_callback(upis.radio.set_rxchannel)
        def set_channel_reponse(group, node, data):
            print("{} set_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

        @global_node_manager.control_engine.add_callback(upis.radio.get_rxchannel)
        def get_channel_reponse(group, node, data):
            print("{} get_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))


        def print_response(group, node, data):
            print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

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

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_manager.control_engine.stop()
