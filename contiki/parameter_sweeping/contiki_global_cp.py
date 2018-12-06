   #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile.
   --agents-ipaddres-list AgentIPAddresses   List with the IP addresses of the agents.
   --controller-ipaddress ipaddressGlobal IP address of global WiSHFUL controller.
   --discovery-interface discoveryInterface Ethernet interface used for node discovery.

Example:
   python parameter_sweeping/contiki_global_cp.py --agents-ipaddres-list 172.16.16.1;172.16.16.2 --controller-ipaddress 127.0.0.1 --discovery-interface lo

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
import datetime
import logging
from contiki.contiki_helpers.global_node_manager import GlobalNodeManager
from contiki.contiki_helpers.taisc_manager import TAISCMACManager
from contiki.contiki_helpers.app_manager import AppManager
import gevent
import traceback
import sys

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2018, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def event_cb(mac_address, event_name, event_value):
    print("{} Node {} Event {}: {} ".format(datetime.datetime.now(), mac_address, event_name, event_value))

def main(args, log, global_node_manager, border_router_id):
    # now configure the nodes normally
    contiki_nodes = global_node_manager.get_mac_address_list()
    print("Connected nodes", [str(node) for node in contiki_nodes])
    taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
    # app_manager = AppManager(global_node_manager)

    server_node = [border_router_id]
    log.info("Set node %d as border router" % (border_router_id))
    # app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01], border_router_id)

    client_nodes = []
    for mac_address in contiki_nodes:
        if mac_address != border_router_id:
            client_nodes.append(mac_address)
    log.info("client nodes {}".format(client_nodes))

    tx_power_settings = [0xF5, 0xE5, 0xD5, 0xC5, 0xB5, 0xA5, 0x95, 0x85, 0x75, 0x65, 0x55, 0x45, 0x35, 0x25, 0x15, 0x05]
    tx_power_settings_mapping = {0xF5: 4.5, 0xE5: 2.5, 0xD5: 1, 0xC5 :-0.5, 0xB5: -1.5, 0xA5: -3, 0x95: -4, 0x85: -6, 0x75: -8, 0x65:-10, 0x55:-12, 0x45:-14, 0x35:-16, 0x25:-18, 0x15:-20, 0x05:-22}

    log.info("Activating nodes")
    # app_manager.update_configuration({"app_activate": 1}, server_node)
    taisc_manager.update_macconfiguration({"TAISC_PG_ACTIVE": 1})
    # log.info("Activating clients")
    # app_manager.update_configuration({"app_activate": 2}, client_nodes)
    # app_manager.update_configuration({"app_send_interval":128}, client_nodes)

    for tx_power_setting in tx_power_settings:
        # configuring RADIO
        log.info("Setting TX power to {} dBm".format(tx_power_settings_mapping[tx_power_setting]))
        ret = taisc_manager.update_macconfiguration({"IEEE802154_phyTXPower": tx_power_setting})
        print(ret)
        ret = taisc_manager.get_measurements(["IEEE802154_measurement_macStats"])
        print(ret)
        gevent.sleep(5)

    log.info("Stopping application")
    taisc_manager.update_macconfiguration({"TAISC_PG_ACTIVE": 0})

if __name__ == "__main__":
    try:
        from docopt import docopt
    except Exception:
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
    log = logging.getLogger('Contiki parameter_sweeping')

    log.debug(args)
    try:
        print("{}{}".format(args['--controller-ipaddress'], args['--discovery-interface']))
        global_node_manager = GlobalNodeManager(ip_address = args['--controller-ipaddress'], interface = args['--discovery-interface'], group_name = "wishful_param_sweep")
        global_node_manager.set_default_callback(default_callback)

        contiki_agents = args['--agents-ipaddres-list'].strip(";").split(";")
        global_node_manager.wait_for_agents(contiki_agents)

        main(args, log, global_node_manager, 1)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        traceback.print_exc(file=sys.stdout)
        log.debug("Exit")
        global_node_manager.stop()
