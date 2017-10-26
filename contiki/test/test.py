#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   python global_cp.py --config config/localhost/global_cp_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
import logging
import wishful_controller
import yaml
import gevent


__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')


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

    controller = wishful_controller.Controller()
    nodes = []

    @controller.new_node_callback()
    def new_node(node):
        nodes.append(node)
        print("New node appeared:")
        print(node)

    try:
        config_file_path = args['--config']
        config = None
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)

        controller.load_config(config)
        controller.start()

        first_time = True

        net_measurement_list = [
            "udp_stats",
            "app_stats",
            "nd6_stats",
            "icmp_stats",
            "rpl_stats",
            "global_ipv6_address",
            "link_local_ipv6_address",
            "nd6_num_neighbors"
        ]

        net_param_list = [
            "app_send_interval",
            "app_payload_length",
            "app_activate",
            "rpl_objective_function",
            "link_address",
            "rpl_dio_interval_min",
            "rpl_dio_interval_doublings",
            "rpl_dio_redundancy",
            "rpl_default_lifetime",
            "rpl_objective_function",
        ]

        radio_param_list = [
            "ContikiMAC_ChannelCheckRate",
            "ContikiMAC_PhaseOptimization",
            "IEEE802154_macExtendedAddress",
            "IEEE802154_macPANId",
            "IEEE802154_macShortAddress",
            "IEEE802154_phyCurrentChannel",
            "IEEE802154_phyTXPower",
            "IEEE802154_macMaxBE",
            "IEEE802154_macMaxCSMABackoffs",
            "IEEE802154_macMaxFrameRetries",
            "IEEE802154_macMinBE",
            "IEEE802154_backoff_algorithm",
            "IEEE802154_macCW",
        ]
        radio_measurement_list = [
            "IEEE802154_measurement_macStats"
        ]
        radio_event_list = [
            "IEEE802154_event_macStats"
        ]

        net_event_list = [
            "app_rx_event"
        ]

        udp_server_node = 0
        udp_server_iface = None

        udp_clients = []

        while True:
            gevent.sleep(5)
            print("\n")
            print("Connected nodes", [str(node.name) for node in nodes])
            if len(nodes) == 3:
                if first_time:
                    for i in range(0,len(nodes)):
                        ret = controller.blocking(True).node(nodes[i]).net.iface("lowpan0").set_parameters_net({'rpl_objective_function': 1})
                        print(ret)
                        radio_platforms = controller.blocking(True).node(nodes[i]).radio.iface("lowpan0").get_radio_platforms()
                        for rp in radio_platforms:
                            ret = controller.blocking(True).node(nodes[i]).radio.iface(rp).get_parameters(["IEEE802154_macShortAddress"])
                            print(ret)
                            if ret["IEEE802154_macShortAddress"] == 1:
                                print("found server")
                                udp_server_node = i
                                udp_server_iface = rp
                                ret = controller.blocking(True).node(nodes[udp_server_node]).net.iface(udp_server_iface).rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
                                print("Set Border Router -> ", ret)
                                ret = controller.blocking(True).node(nodes[i]).net.iface(rp).set_parameters_net({'app_activate': 1})
                                print("Set Server -> ", ret)
                            else:
                                udp_clients.append([i,rp])
                                ret = controller.blocking(True).node(nodes[i]).net.iface(rp).set_parameters_net({'app_activate': 2})
                                print("Set Client -> ", ret)
                            ret = controller.blocking(True).node(nodes[i]).net.iface(rp).get_measurements_net(['global_ipv6_address'])
                            print(ret)
                            hex_ret = ""
                            for val in ret['global_ipv6_address']:
                               hex_ret = hex_ret + " " + hex(val)
                            print(hex_ret)
                            ret = controller.blocking(True).node(nodes[i]).net.iface(rp).get_measurements_net(['link_local_ipv6_address'])
                            print(ret)
                            hex_ret = ""
                            for val in ret['link_local_ipv6_address']:
                               hex_ret = hex_ret + " " + hex(val)
                            print(hex_ret)
                    first_time = False
                else:
                    gevent.sleep(2)
                    print("Server Results")
                    val = controller.blocking(True).node(nodes[udp_server_node]).net.iface(udp_server_iface).get_measurements_net(['app_stats'])
                    print(val)
                    val = controller.blocking(True).node(nodes[udp_server_node]).net.iface(udp_server_iface).get_measurements_net(['ipv6_stats'])
                    print(val)
                    val = controller.blocking(True).node(nodes[udp_server_node]).net.iface(udp_server_iface).get_measurements_net(['icmp_stats'])
                    print(val)
                    val = controller.blocking(True).node(nodes[udp_server_node]).net.iface(udp_server_iface).get_measurements_net(['rpl_stats'])
                    print(val)
                    val = controller.blocking(True).node(nodes[udp_server_node]).radio.iface(udp_server_iface).get_measurements(['IEEE802154_measurement_macStats'])
                    print(val)
                    for udp_client in udp_clients:
                        print("Client Results")
                        val = controller.blocking(True).node(nodes[udp_client[0]]).net.iface(udp_client[1]).get_measurements_net(['app_stats'])
                        print(val)
                        val = controller.blocking(True).node(nodes[udp_client[0]]).net.iface(udp_client[1]).get_measurements_net(['ipv6_stats'])
                        print(val)
                        val = controller.blocking(True).node(nodes[udp_client[0]]).net.iface(udp_client[1]).get_measurements_net(['icmp_stats'])
                        print(val)
                        val = controller.blocking(True).node(nodes[udp_client[0]]).net.iface(udp_client[1]).get_measurements_net(['rpl_stats'])
                        print(val)
                        val = controller.blocking(True).node(nodes[udp_client[0]]).radio.iface(udp_client[1]).get_measurements(['IEEE802154_measurement_macStats'])
                        print(val)
            gevent.sleep(2)

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
