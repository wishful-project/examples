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
import time
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
    print("{} AP CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(
        datetime.datetime.now(), group, node.name, cmd, data))


def sta_callback(group, node, cmd, data):
    print("{} STA CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(
        datetime.datetime.now(), group, node.name, cmd, data))


def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(
        datetime.datetime.now(), group, node.name, cmd, data))


def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))


def event_cb(mac_address, event_name, event_value):
    measurement_logger.log_measurement(event_name, event_value)


def main(args, interferer_ap, interferer_sta):
    contiki_nodes = global_node_manager.get_mac_address_list()
    contiki_nodes.sort()
    print("Connected nodes", [str(node) for node in contiki_nodes])
    taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
    app_manager = AppManager(global_node_manager)

    """ Blacklist TSCH channels that overlap with Wi-Fi channel """
    wifi_to_tsch_channels_dct = mapWifiOnZigbeeChannels(
        log, './sc2_tsch_blacklisting/ieee80211_to_ieee802154_channels.csv')

    ret = taisc_manager.update_slotframe('./contiki_helpers/default_taisc_slotframe.csv')
    log.info(ret)
    ret = taisc_manager.update_macconfiguration({'IEEE802154e_macSlotframeSize': len(contiki_nodes)})
    log.info(ret)
    ret = taisc_manager.activate_radio_program("TSCH", contiki_nodes)
    log.info(ret)
    # global_node_manager.start_local_monitoring_cp()
    # gevent.sleep(5)
    # app_manager.subscribe_events(["RIME_appPerPacket_rxstats"], event_cb, 0)
    # gevent.sleep(5)
    ret = app_manager.update_configuration({"RIME_exampleUnicastSendInterval": 37}, contiki_nodes)
    log.info(ret)
    ap_local_cp = global_node_manager.start_custom_local_cp(wifi_interference_ap, ap_callback, [interferer_ap])
    sta_local_cp = global_node_manager.start_custom_local_cp(wifi_interference_sta, sta_callback, [interferer_sta])
    prev_stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ret = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 1}, contiki_nodes)
    log.info("Activate APP {}".format(ret))

    # control loop
    while True:
        # without interference
        log.info("TSCH MAC without interference!")
        for i in range(0, 30):
            stats = taisc_manager.get_measurements(["IEEE802154_MACSTATS"], 1)[1]["IEEE802154_MACSTATS"]
            measurement = [int(time.time()), 1, 107, "TSCH", stats[0]]
            for j in range(1, len(prev_stats)):
                measurement.append(stats[j] - prev_stats[j])
            prev_stats = stats
            measurement_logger.log_measurement("IEEE802154_MACSTATS", measurement)
            gevent.sleep(1)

        # with interference
        log.info("TSCH MAC with interference!")
        ap_local_cp.send({'command': 'start_wifi_interference'})
        sta_local_cp.send({'command': 'start_wifi_interference'})
        for i in range(0, 30):
            stats = taisc_manager.get_measurements(["IEEE802154_MACSTATS"], 1)[1]["IEEE802154_MACSTATS"]
            measurement = [int(time.time()), 1, 107, "TSCH", stats[0]]
            for j in range(1, len(prev_stats)):
                measurement.append(stats[j] - prev_stats[j])
            prev_stats = stats
            measurement_logger.log_measurement("IEEE802154_MACSTATS", measurement)
            gevent.sleep(1)

        # with interference + blacklisting
        # Blacklist channels
        log.info("TSCH MAC with interference, but blacklisted channels 15.4!")
        blacklisted_channels = wifi_to_tsch_channels_dct[6]
        ret = taisc_manager.blacklist_channels(blacklisted_channels, contiki_nodes)
        log.info("Blacklist TSCH channels {}, error {}".format(blacklisted_channels, ret))
        for i in range(0, 30):
            stats = taisc_manager.get_measurements(["IEEE802154_MACSTATS"], 1)[1]["IEEE802154_MACSTATS"]
            measurement = [int(time.time()), 1, 107, "TSCH", stats[0]]
            for j in range(1, len(prev_stats)):
                measurement.append(stats[j] - prev_stats[j])
            prev_stats = stats
            measurement_logger.log_measurement("IEEE802154_MACSTATS", measurement)
            gevent.sleep(1)

        # Resetting state for next run
        ap_local_cp.send({'command': 'stop_wifi_interference'})
        sta_local_cp.send({'command': 'stop_wifi_interference'})
        err1 = taisc_manager.update_macconfiguration({'IEEE802154e_macHoppingSequenceList': [16, 18, 17, 23, 26, 15, 25, 22, 19, 11, 12, 13, 24, 14, 20, 21]}, contiki_nodes)
        err2 = taisc_manager.update_macconfiguration({'IEEE802154e_macHoppingSequenceLength': 16}, contiki_nodes)
        log.info('resetting state for next run {} {}'.format(err1, err2))


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
    global_node_manager.wait_for_agents(node_config['ip_address_list'])

    measurements_file_path = args['--measurements']
    with open(measurements_file_path, 'r') as f:
        measurement_config = yaml.load(f)
    measurement_logger = MeasurementLogger.load_config(measurement_config)

    try:
        main(args, 1, 5)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        measurement_logger.stop_logging()
        global_node_manager.stop()
