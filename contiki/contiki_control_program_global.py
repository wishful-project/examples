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
import yaml
import wishful_upis as upis

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"


log = logging.getLogger('contiki_global_control_program')
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
        nodes.remove(node);
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


@global_control_engine.set_default_callback()
def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))


@global_control_engine.add_callback(upis.radio.set_rxchannel)
def set_channel_reponse(group, node, data):
    print("{} set_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))


@global_control_engine.add_callback(upis.radio.get_rxchannel)
def get_channel_reponse(group, node, data):
    print("{} get_channel_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))


def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data)) 


def main(args):
    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    global_control_engine.load_config(config)
    global_control_engine.start()
   
    #control loop
    while True:
        gevent.sleep(10)
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])
        if nodes:
            #execute non-blocking function immediately
            global_control_engine.blocking(False).node(nodes[0]).radio.iface("lowpan0").set_rxchannel(12)

            #execute non-blocking function immediately, with specific callback
            global_control_engine.callback(print_response).node(nodes[0]).radio.iface("lowpan0").get_rxchannel()

            #schedule non-blocking function delay
            global_control_engine.delay(3).node(nodes[0]).radio.iface("lowpan0").set_rxchannel(12)

            #schedule non-blocking function exec time
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            global_control_engine.exec_time(exec_time).node(nodes[0]).radio.iface("lowpan0").get_rxchannel()

            #execute blocking function immediately
            result = global_control_engine.node(nodes[0]).radio.iface("lowpan0").get_rxchannel()
            print("{} Channel is: {}".format(datetime.datetime.now(), result))

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
        global_control_engine.stop()
