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

        radio_param_list = [
            # "ContikiMAC_ChannelCheckRate",
            # "ContikiMAC_PhaseOptimization",
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
        net_param_list = [
            "link_address",
            "rpl_dio_interval_min",
            "rpl_dio_interval_doublings",
            "rpl_dio_redundancy",
            "rpl_default_lifetime",
            "rpl_objective_function"
        ]

        net_measurement_list = [
            "ipv6_stats",
            "icmp_stats",
            "tcp_stats",
            "udp_stats",
            "nd6_stats",
            "rpl_stats"
        ]

        while True:
            gevent.sleep(10)
            print("\n")
            print("Connected nodes", [str(node.name) for node in nodes])
            if nodes:
                if first_time:
                    ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
                    print(ret)
                    first_time = False
                else:
                    for node in nodes:
                        for param in radio_param_list:
                            val = controller.blocking(True).node(node).radio.iface("lowpan0").get_parameters([param])
                            print("lowpan0: {}".format(val))
                            val = controller.blocking(True).node(node).radio.iface("lowpan1").get_parameters([param])
                            print("lowpan1: {}".format(val))
                            gevent.sleep(1)
                        for param in net_param_list:
                            val = controller.blocking(True).node(node).net.iface("lowpan0").get_parameters_net([param])
                            print("lowpan0: {}".format(val))
                            val = controller.blocking(True).node(node).net.iface("lowpan1").get_parameters_net([param])
                            print("lowpan1: {}".format(val))
                            gevent.sleep(1)
                        for m in radio_measurement_list:
                            val = controller.blocking(True).node(node).radio.iface("lowpan0").get_measurements([m])
                            print("lowpan0: {}".format(val))
                            val = controller.blocking(True).node(node).radio.iface("lowpan1").get_measurements([m])
                            print("lowpan1: {}".format(val))
                            gevent.sleep(1)
                        for m in net_measurement_list:
                            val = controller.blocking(True).node(node).net.iface("lowpan0").get_measurements_net([m])
                            print("lowpan0: {}".format(val))
                            val = controller.blocking(True).node(node).net.iface("lowpan1").get_measurements_net([m])
                            print("lowpan1: {}".format(val))
                            gevent.sleep(1)

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
