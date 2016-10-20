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
   --measurements measurementsConfig Config file with measurement info

Example:
   python sc2_tsch_blacklisting/global_cp.py --config config/portable/global_cp_config.yaml --nodes config/portable/nodes.yaml --measurements config/portable/measurement_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import datetime
import logging
from contiki.contiki_helpers.global_node_manager import *
from contiki.contiki_helpers.taisc_manager import *
from contiki.contiki_helpers.app_manager import *
import gevent
import yaml
from measurement_logger import *
from contiki.sc2_tsch_blacklisting.wifi_interference_ap import wifi_interference_ap
from contiki.sc2_tsch_blacklisting.wifi_interference_sta import wifi_interference_sta

__author__ = "Peter Ruckebusch & Jan Bauwens"
__copyright__ = "Copyright (c) 2016, imec"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be & jan.bauwens@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')


def mapWifiOnZigbeeChannels(log, channel_mapping):
    dct = {}
    try:
        file_n = open(channel_mapping, 'rt')
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
    measurement_logger.log_measurement(event_name, event_value)


def main(args, interferer_ap, interferer_sta):
    contiki_nodes = global_node_manager.get_mac_address_list()
    print("Connected nodes", [str(node) for node in contiki_nodes])
    taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
    app_manager = AppManager(global_node_manager)

    """ Blacklist TSCH channels that overlap with Wi-Fi channel """
    wifi_to_tsch_channels_dct = mapWifiOnZigbeeChannels(log, './sc2_tsch_blacklisting/ieee80211_to_ieee802154_channels.csv')

    ret = taisc_manager.update_slotframe('./contiki_helpers/default_taisc_slotframe.csv')
    log.info(ret)
    ret = taisc_manager.update_macconfiguration({'IEEE802154e_macSlotframeSize': len(contiki_nodes)})
    log.info(ret)
    global_node_manager.start_local_monitoring_cp()
    gevent.sleep(5)
    app_manager.subscribe_events(["RIME_appPerPacket_rxstats"], event_cb, 0)
    gevent.sleep(5)

    # control loop
    while True:
        # without interference
        log.info("Activating TSCH MAC (without interference)!")
        err1 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 0})
        err2 = taisc_manager.activate_radio_program("TSCH")
        gevent.sleep(5)
        err3 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 1})
        log.info("Error: MAC {} APP {},{}".format(err2, err1, err3))
        gevent.sleep(20)

        # with interference
        global_node_manager.start_custom_local_cp(wifi_interference_ap, ap_callback, [interferer_ap])
        global_node_manager.start_custom_local_cp(wifi_interference_sta, sta_callback, [interferer_sta])
        log.info("TSCH MAC with interference!")
        gevent.sleep(20)

        # with interference + blacklisting
        # Blacklist channels
        blacklisted_channels = wifi_to_tsch_channels_dct[1]
        log.info("Blacklist TSCH channels {}".format(blacklisted_channels))
        ret = taisc_manager.blacklist_channels(blacklisted_channels)
        log.info(ret)
        log.info("Activating TSCH MAC (with interference, but blacklisted channels (err {})!".format(ret))
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

    logging.basicConfig(filename=logfile, level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

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
    global_node_manager.wait_for_agents(node_config['ip_address_list'])

    measurements_file_path = args['--measurements']
    with open(measurements_file_path, 'r') as f:
        measurement_config = yaml.load(f)
    measurement_logger = MeasurementLogger.load_config(measurement_config)

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        measurement_logger.stop_logging()
        global_node_manager.stop()
