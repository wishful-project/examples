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
            "nd6_num_neighbors",
            "rpl_rank",
            "rpl_dio_stats",
            "energest_stats",
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
            "app_server_ipv6_address",
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

        while True:
            gevent.sleep(5)
            print("\n")
            print("Connected nodes", [str(node.name) for node in nodes])
            if nodes:
                if first_time:
                    ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
                    print(ret)
                    first_time = False
                    radio_platforms = controller.blocking(True).node(nodes[0]).radio.iface("lowpan0").get_radio_platforms()
                    for rp in radio_platforms:
                        ret = controller.blocking(True).node(nodes[0]).net.iface(rp).set_parameters_net({'rpl_objective_function': 1})
                        print(ret)
                else:
                    for node in nodes:
                        for param in radio_param_list:
                            for radio_platform in radio_platforms:
                                val = controller.blocking(True).node(node).radio.iface(radio_platform).get_parameters([param])
                                print("{}: {}".format(radio_platform, val))
                            gevent.sleep(1)
                        for param in net_param_list:
                            for radio_platform in radio_platforms:
                                val = controller.blocking(True).node(node).net.iface(radio_platform).get_parameters_net([param])
                                print("{}: {}".format(radio_platform, val))
                            gevent.sleep(1)
                        for m in radio_measurement_list:
                            for radio_platform in radio_platforms:
                                val = controller.blocking(True).node(node).radio.iface(radio_platform).get_measurements([m])
                                print("{}: {}".format(radio_platform, val))
                            gevent.sleep(1)
                        for m in net_measurement_list:
                            for radio_platform in radio_platforms:
                                val = controller.blocking(True).node(node).net.iface(radio_platform).get_measurements_net([m])
                                print("{}: {}".format(radio_platform, val))
                            gevent.sleep(1)

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
