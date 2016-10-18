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
   ./global_cp -v --config ./config/localhost/control_program_global.yaml --num-agents 10 --receiver-address 1

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
        log.info("Activate receiver {}: ERROR {}".format(receiver_addr, err1))
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
   --receiver-address rxAddress Address of receiver node

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
