#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
upi_executor_daemon.py: Example Contiki global control program

Usage:
   upi_executor_daemon.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./upi_executor_daemon -v --config ./daemon_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import logging
import wishful_controller
import gevent
import yaml
import json

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University - iMinds - IBCN"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"


log = logging.getLogger('upi_executor_daemon')
global_control_engine = wishful_controller.Controller()
nodes = []


@global_control_engine.new_node_callback()
def new_node(node):
    nodes.append(node)
    print("New node appeared:")
    print(node)


@global_control_engine.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node)
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


def main(args):
    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    global_control_engine.load_config(config)
    global_control_engine.start()

    # control loop
    while True:
        if nodes:
            channel_no = int(raw_input())
            if channel_no >= 11 and channel_no <= 26:
                result = global_control_engine.node(nodes).radio.iface("lowpan0").set_rxchannel(channel_no)
                print json.dumps({"ERROR Code": result})
            else:
                break
        else:
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

    logging.basicConfig(filename=logfile, level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_control_engine.stop()
