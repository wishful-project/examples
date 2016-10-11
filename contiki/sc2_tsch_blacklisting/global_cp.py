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
   python sc2_tsch_blacklisting/global_cp.py --config config/portable/global_cp_config.yaml --nodes config/portable/nodes.yaml

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
from contiki.sc2_tsch_blacklisting.wifi_interference_ap import wifi_interference_ap
from contiki.sc2_tsch_blacklisting.wifi_interference_sta import wifi_interference_sta

__author__ = "Peter Ruckebusch & Jan Bauwens"
__copyright__ = "Copyright (c) 2016, imec"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be & jan.bauwens@intec.ugent.be"

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
            
def mapWifiOnZigbeeChannels(log,channel_mapping):
	dct = {}
	try:
		file_n = open(channel_mapping,'rt')
		import csv
		reader = csv.DictReader(file_n)
		for row in reader:
			dct[int(row["ieee80211"])] = []
			for x in row["ieee802154"].split('-'):
				dct[int(row["ieee80211"])].append(int(x))
	except Exception as e:
		log.fatal("An error occurred while reading nodes: %s" % e)
	finally:
		file_n.close()
	return dct

def ap_callback(group, node, cmd, data):
    print("{} AP CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def sta_callback(group, node, cmd, data):
    print("{} STA CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))

def event_cb(mac_address, event_name, event_value):
    measurement_logger.log_measurement(event_name,event_value)

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
    #without interference
    log.info("Activating TSCH MAC (without interference)!")
    parameters["RIME_exampleUnicastActivateApplication"] = 0
    err1 = app_manager.update_configuration(parameters)
    err2 = taisc_manager.activate_radio_program("TSCH")
    gevent.sleep(5)
    parameters["RIME_exampleUnicastActivateApplication"] = 1
    err3 = app_manager.update_configuration(parameters)
    log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
    gevent.sleep(20)
    
    #with interference
    global_node_manager.start_custom_local_cp(wifi_interference_ap, ap_callback, [contiki_nodes[0]] )
    global_node_manager.start_custom_local_cp(wifi_interference_sta, sta_callback, [contiki_nodes[1]] )

    log.info("Activating TSCH MAC (with interference)!")
    parameters["RIME_exampleUnicastActivateApplication"] = 0
    err1 = app_manager.update_configuration(parameters)
    err2 = taisc_manager.activate_radio_program("TSCH")
    gevent.sleep(5)
    parameters["RIME_exampleUnicastActivateApplication"] = 1
    err3 = app_manager.update_configuration(parameters)
    log.info("Error: MAC {} APP {},{}".format(err2,err1,err3))
    gevent.sleep(20)
    
    #Blacklist channels
    log.info("Start blacklisting!")
    ret = taisc_manager.blacklist_channels(blacklisted_channels)
    log.info(ret)
    
    #with interference + blacklisting
    log.info("Activating TSCH MAC (with interference, but blacklisted channels!")
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

    nodes_file_path = args['--nodes']
    with open(nodes_file_path, 'r') as f:
        node_config = yaml.load(f)
    configure_measurement_logger(config)
    global_node_manager.wait_for_agents(node_config['ip_address_list'])
    log.info("MAC Addresses: " + str(global_node_manager.mac_address_list))
    
    """ Blacklist TSCH channels that overlap with Wi-Fi channel """
    wifi_to_tsch_channels_dct = mapWifiOnZigbeeChannels(log,'./sc2_tsch_blacklisting/ieee80211_to_ieee802154_channels.csv')
    blacklisted_channels = wifi_to_tsch_channels_dct[1]
    log.info("TSCH channels to be blacklisted %s",blacklisted_channels)

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        global_node_manager.stop()
