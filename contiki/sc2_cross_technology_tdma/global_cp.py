#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path
   --num-agents numAgents Number of WiSHFUL agents in experiment
   --receiver-address receiverAddress Address of receiver node.

Example:
   ./sc2_cross_technology_tdma/global_cp -v --config ./config/localhost/global_config.yaml --num-agents 10 --receiver-address 1

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""


import datetime
import logging
import wishful_controller
import gevent
import yaml
import _thread
from contiki.mac_managers.taisc_manager import *
from contiki.app_managers.app_manager import *
from local_cp import my_local_control_program

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('global_cp.main')
global_control_engine = wishful_controller.Controller()
global_taisc_manager = GlobalTAISCMACManager(global_control_engine, "CSMA")
global_app_manager = GlobalAppManager(global_control_engine, global_taisc_manager)
nodes = []


@global_control_engine.new_node_callback()
def new_node(node):
    nodes.append(node)
    print("New node appeared:")
    print(node)


@global_control_engine.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        # global_taisc_manager.remove_node(node)
        nodes.remove(node)
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


@global_control_engine.set_default_callback()
def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(
        datetime.datetime.now(), group, node.name, cmd, data))


def hc_message_handler(hc_connector):
    while True:
        msg = hc_connector.recv(block=False, timeout=1)
        while msg is not None:
            print("{} Global CP received msg {} from local CP".format(datetime.datetime.now(), msg))
            msg = hc_connector.recv(block=False, timeout=1)
        gevent.sleep(1)
    pass


def main(args):
    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    global_control_engine.load_config(config)
    global_control_engine.start()

    num_agents = int(args['--num-agents'])
    receiver_addr = int(args['--receiver-address'])

    # Wait for nodes before starting the local CP.
    while True:
        gevent.sleep(10)
        if len(nodes) == num_agents:
            log.info("All nodes are active we can start the local control programs")
            log.info("Connected nodes: %s", nodes)
            break
        else:
            log.info("Still waiting for %d nodes", num_agents - len(nodes))

    for node in nodes:
        global_taisc_manager.add_node(node)
        hc_connector = global_control_engine.node(node).hc.start_local_control_program(program=my_local_control_program)
        _thread.start_new_thread(hc_message_handler, (hc_connector,))

    mac_address_list = global_taisc_manager.get_hwaddr_list()
    active_sender_address_list = []

    gevent.sleep(1)

    # configure taisc slotframe
    ret = global_taisc_manager.update_slotframe('./mac_managers/default_taisc_slotframe.csv')
    log.info(ret)
    gevent.sleep(10)

    while True:
        # activate receiver
        parameters = {"RIME_exampleUnicastActivateApplication": 1}
        err1 = global_app_manager.update_configuration(parameters, [receiver_addr])
        log.info("Activate receiver {}: ERROR {}".format(receiver_addr,err1))
        gevent.sleep(1)
        cw = cwold = calculateCWOpt(1)

        # add nodes
        for mac_address in mac_address_list[1:]:
            log.info("Adding sender {}!".format(mac_address))
            active_sender_address_list.append(mac_address)
  
            cw = calculateCWOpt(len(active_sender_address_list))
            err1 = global_taisc_manager.update_macconfiguration({'IEEE802154_macCW': cw}, active_sender_address_list)
            log.info("Changed CW from {} to {}: ERROR {}!".format(cwold, cw, err1))
  
            parameters["RIME_exampleUnicastActivateApplication"] = 1
            err1 = global_app_manager.update_configuration(parameters, [mac_address])
            log.info("Activated application on {}: ERROR {}!".format(mac_address, err1))

            gevent.sleep(10)

        log.info("Switching all nodes to TDMA!")

        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = global_app_manager.update_configuration(parameters)
        log.info("Stopping APP: ERROR {}".format(err1))
        gevent.sleep(1)

        err1 = global_taisc_manager.activate_radio_program("TDMA")
        log.info("Activated TDMA: ERROR".format(err1))
        gevent.sleep(5)

        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err1 = global_app_manager.update_configuration(parameters)
        log.info("Starting APP: ERROR {}".format(err1))
        
        log.info("Switching all nodes to TDMA dones!")
        gevent.sleep(30)
        
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = global_app_manager.update_configuration(parameters)
        log.info("Stopping APP: ERROR {}".format(err1))
        gevent.sleep(1)
        
        err1 = global_taisc_manager.activate_radio_program("CSMA")
        log.info("Activated CSMA: ERROR".format(err1))
        gevent.sleep(5)
    
    

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
