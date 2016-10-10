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
from contiki.contiki_helpers.taisc_manager import *
from contiki.contiki_helpers.app_manager import *
import gevent
import wishful_upis as upis
import wishful_controller
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

def event_cb(mac_address, event_name, event_value):
    print("{} Node {} Event {}: {} ".format(datetime.datetime.now(), mac_address, event_name, event_value))

def main(args):
    contiki_nodes = global_node_manager.get_mac_address_list()
    print("Connected nodes", [str(node) for node in contiki_nodes])
    taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
    app_manager = AppManager(global_node_manager)
    ret = taisc_manager.update_slotframe('./contiki_helpers/default_taisc_slotframe.csv')
    log.info(ret)
    global_node_manager.start_local_monitoring_cp()
    gevent.sleep(5)
    app_manager.subscribe_events(["RIME_appPerPacket_rxstats"],event_cb, 0)
    gevent.sleep(5)
    parameters = {"RIME_exampleUnicastActivateApplication": 1}
    #control loop
    while True:
        log.info("Activating CSMA MAC!")
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = app_manager.update_configuration(parameters)
        err2 = taisc_manager.activate_radio_program("CSMA")
        gevent.sleep(5)
        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err3 = app_manager.update_configuration(parameters)
        log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
        gevent.sleep(20)
        log.info("Activating TDMA MAC!")
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = app_manager.update_configuration(parameters)
        err2 = taisc_manager.activate_radio_program("TDMA")
        gevent.sleep(5)
        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err3 = app_manager.update_configuration(parameters)
        log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
        gevent.sleep(20)
        log.info("Activating TSCH MAC!")
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = app_manager.update_configuration(parameters)
        err2 = taisc_manager.activate_radio_program("TSCH")
        gevent.sleep(5)
        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err3 = app_manager.update_configuration(parameters)
        log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
        gevent.sleep(20)

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
    global_node_manager.wait_for_agents(["172.16.16.1"])

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_node_manager.control_engine.stop()
