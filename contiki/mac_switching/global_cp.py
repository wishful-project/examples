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
   python mac_switching/global_cp.py --config config/portable/global_cp_config.yaml --nodes config/portable/nodes.yaml

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
from measurement_logger.stdout.std_measurement_logger import *
from measurement_logger.file.file_measurement_logger import *
from measurement_logger.MySQL.mysql_measurement_logger import *
from measurement_logger.OML.oml_measurement_logger import *

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, imec"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')

measurement_logger = None

def configure_measurement_logger(config):
    global measurement_logger
    ml_config = config["measurement_logger"]
    if "stdout" in ml_config["type"]:
        measurement_logger = STDOUTMeasurementLogger("Facility", "Global_cp", "group_name")
    elif "file" in ml_config["type"]:
        measurement_logger = FileMeasurementLogger("Facility", "Global_cp", "group_name", ml_config["filename"] )
    elif "mysql" in ml_config["type"]:
        measurement_logger = MySQLMeasurementLogger("Facility", "Global_cp", "group_name", ml_config["db_host"],\
            ml_config["db_name"], ml_config["db_username"], ml_config["db_password"], ml_config["measurement_defs"])

def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

def event_cb(mac_address, event_name, event_value):
    measurement_logger.log_measurement(event_name,event_value)
    #~ print("{} Node {} Event {}: {} ".format(datetime.datetime.now(), mac_address, event_name, event_value))

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
    # control loop
    while True:
        log.info("Activating CSMA MAC!")
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = app_manager.update_configuration(parameters)
        err2 = taisc_manager.activate_radio_program("CSMA")
        gevent.sleep(5)
        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err3 = app_manager.update_configuration(parameters)
        log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
        gevent.sleep(10)
        log.info("Activating TDMA MAC!")
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = app_manager.update_configuration(parameters)
        err2 = taisc_manager.activate_radio_program("TDMA")
        gevent.sleep(5)
        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err3 = app_manager.update_configuration(parameters)
        log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
        gevent.sleep(10)
        log.info("Activating TSCH MAC!")
        parameters["RIME_exampleUnicastActivateApplication"] = 0
        err1 = app_manager.update_configuration(parameters)
        err2 = taisc_manager.activate_radio_program("TSCH")
        gevent.sleep(5)
        parameters["RIME_exampleUnicastActivateApplication"] = 1
        err3 = app_manager.update_configuration(parameters)
        log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
        gevent.sleep(10)
    measurement_logger.stop_logging()
       

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

    nodes_file_path = args['--nodes']
    with open(nodes_file_path, 'r') as f:
        node_config = yaml.load(f)
    configure_measurement_logger(config)
    global_node_manager.wait_for_agents(node_config['ip_address_list'])

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_node_manager.stop()
