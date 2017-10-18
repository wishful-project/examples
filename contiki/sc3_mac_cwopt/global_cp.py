#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program for mac contention window optimization. Afterwards TDMA is activated. 

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path
   --nodes nodesFile   Config file with node info
   --measurements measurementsConfig Config file with measurement info

Example:
   python sc3_mac_cwopt/global_cp --config config/portable/global_cp_config.yaml --nodes config/portable/nodes.yaml --measurements config/portable/measurement_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import datetime
import time
import math
import logging
from contiki.contiki_helpers.global_node_manager import GlobalNodeManager
from contiki.contiki_helpers.taisc_manager import TAISCMACManager
from contiki.contiki_helpers.app_manager import AppManager
import gevent
import yaml
from measurement_logger import MeasurementLogger

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"


def calculateCWOpt(num_tx_nodes):
    # constants
    MacHdrLen = 11  # num mac hdr bytes
    MackAckLen = 6  # num ack bytes
    N_aMaxSIFSFrameSize = 18
    N_aUnitBackoffPeriod = 20  # num symbols in base backoff period
    T_Sym = 16  # duration of one symbol in microseconds
    T_Slot = N_aUnitBackoffPeriod * T_Sym
    T_Byte = 2 * T_Sym
    T_PhyPre = 4 * T_Byte
    T_PhySFD = T_Byte
    T_MacHdr = MacHdrLen * T_Byte
    T_MacAck = T_PhyPre + T_PhySFD + MackAckLen * T_Byte
    T_SIFS = 12 * T_Sym
    T_LIFS = 40 * T_Sym
    T_Turnaround = 12 * T_Sym
    CW_MIN = 7
    CW_MAX = 255

    # variables
    n_MacPayloadBytes = 106  # num app data bytes
    n_Tx_ED = num_tx_nodes

    # calculated values
    t_EIFS = T_Turnaround + T_MacAck + (T_LIFS if n_MacPayloadBytes > N_aMaxSIFSFrameSize else T_SIFS)
    t_AppData = n_MacPayloadBytes * T_Byte
    t_Packet = T_PhyPre + T_PhySFD + T_MacHdr + t_AppData
    t_Collision = t_Packet + t_EIFS
    CW_f = n_Tx_ED * math.sqrt(2 * t_Collision / T_Slot)
    CW = round(CW_f)
    CW = int(CW)
    CW = max(CW, CW_MIN)
    CW = min(CW, CW_MAX)
    return CW


log = logging.getLogger('contiki_global_cp')
prev_stats = {}
current_mac = "CSMA"


def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))


def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data))


def event_cb(mac_address, event_name, event_value):
    global prev_stats
    global current_mac
    mac_stats_event = [int(time.time()), mac_address, 107, current_mac, event_value[0]]
    for j in range(1, len(prev_stats[mac_address]) - 1):
        mac_stats_event.append(event_value[j] - prev_stats[mac_address][j])
    mac_stats_event.append(event_value[len(prev_stats[mac_address]) - 1])
    prev_stats[mac_address] = event_value
    measurement_logger.log_measurement(event_name, mac_stats_event)


def main(args):
    global prev_stats
    global current_mac
    contiki_nodes = global_node_manager.get_mac_address_list()
    contiki_nodes.sort()
    print("Connected nodes", [str(node) for node in contiki_nodes])
    for node in contiki_nodes:
        prev_stats[node] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
    app_manager = AppManager(global_node_manager)
    ret = taisc_manager.update_slotframe('./contiki_helpers/default_taisc_slotframe.csv')
    log.info(ret)
    global_node_manager.start_local_monitoring_cp()
    gevent.sleep(5)
    taisc_manager.subscribe_events(["IEEE802154_event_macStats"], event_cb, 0)
    gevent.sleep(1)
    ret = app_manager.update_configuration({"RIME_exampleUnicastMsgSize": 100})
    log.info(ret)
    ret = taisc_manager.update_macconfiguration({'IEEE802154e_macTsTimeslotLength': 8000})
    log.info(ret)
    ret = taisc_manager.update_macconfiguration({'IEEE802154e_macSlotframeSize': len(contiki_nodes)})
    log.info(ret)
    ret = app_manager.update_configuration({"RIME_exampleUnicastSendIntervalBoundaries": (32, 48)})
    log.info(ret)

    while True:
        # activate receiver
        # ret = app_manager.update_configuration({"RIME_exampleUnicastSendInterval": 10})
        err1 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 1}, [1])
        log.info("Activate receiver: ERROR {}".format(err1))
        gevent.sleep(1)
        cw = cwold = calculateCWOpt(2) * 320
        active_sender_address_list = []

        # add nodes
        for mac_address in contiki_nodes:
            if mac_address != 1:
                log.info("Adding sender {}!".format(mac_address))
                active_sender_address_list.append(mac_address)

                # update contention window
                cwold = cw
                cw = calculateCWOpt(len(active_sender_address_list) + 1) * 320
                err1 = taisc_manager.update_macconfiguration({'IEEE802154_macCW': cw}, active_sender_address_list)
                log.info("Changed CW from {} to {}: ERROR {}!".format(cwold, cw, err1))

                # activate application on mac
                err1 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 1}, [mac_address])
                log.info("Activated application on {}: ERROR {}!".format(mac_address, err1))

                gevent.sleep(10)

        log.info("Switching all nodes to TDMA!")

        err1 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 0})
        log.info("Stopping APP: ERROR {}".format(err1))
        gevent.sleep(1)

        err1 = taisc_manager.activate_radio_program("TDMA")
        current_mac = "TDMA"
        log.info("Activated TDMA: ERROR {}".format(err1))
        # send_interval = int(math.ceil(128 / (1000 / (len(contiki_nodes) * 8))))
        # ret = app_manager.update_configuration({"RIME_exampleUnicastSendInterval": send_interval})
        # log.info(ret)

        err1 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 1})
        log.info("Starting APP: ERROR {}".format(err1))

        log.info("Switching all nodes to TDMA!")
        gevent.sleep(30)

        err1 = app_manager.update_configuration({"RIME_exampleUnicastActivateApplication": 0})
        log.info("Stopping APP: ERROR {}".format(err1))
        gevent.sleep(1)

        err1 = taisc_manager.activate_radio_program("CSMA")
        current_mac = "CSMA"
        log.info("Activated CSMA: ERROR {}".format(err1))
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
