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

    # create a WiSHFUL global controller
    controller = wishful_controller.Controller()
    nodes = []

    # Bind new node callback in controller
    @controller.new_node_callback()
    def new_node(node):
        nodes.append(node)
        print("New node appeared:")
        print(node)

    try:
        # read the global cp config
        config_file_path = args['--config']
        config = None
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)

        # load the global cp config
        controller.load_config(config)
        # Start the WiSHFUL global controller
        controller.start()

        # First wait for nodes to appear
        while len(nodes) == 0:
            gevent.sleep(5)

        print("Connected nodes", [str(node.name) for node in nodes])

        # configure a node as RPL border router by pushing a IPv6 prefix to start the IPv6 network
        ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
        print(ret)

        # get all the radio plaforms for each node
        dict_nodes_radio_platform_lst = controller.blocking(True).nodes(nodes).radio.iface("lowpan0").get_radio_platforms()

        # Available UPI_R parameters
        radio_param_list = [
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

        # Available UPI_R measurements
        radio_measurement_list = [
            "IEEE802154_measurement_macStats"
        ]

        # Available UPI_N parameters
        net_param_list = [
            "link_address",
            "rpl_dio_interval_min",
            "rpl_dio_interval_doublings",
            "rpl_dio_redundancy",
            "rpl_default_lifetime",
            "rpl_objective_function"
        ]

        # Available UPI_N measurements
        net_measurement_list = [
            "ipv6_stats",
            "icmp_stats",
            "tcp_stats",
            "udp_stats",
            "nd6_stats",
            "rpl_stats"
        ]

        while True:
            gevent.sleep(5)
            if nodes:
                # iterate over the nodes
                for node in nodes:
                    # interate over the radio platforms
                    for radio_platform in dict_nodes_radio_platform_lst[node]:
                        # interate over the UPI_R parameters
                        for param in radio_param_list:
                            val = controller.blocking(True).node(node).radio.iface(radio_platform).get_parameters([param])
                            print("{}: {}".format(radio_platform, val))
                        # interate over the UPI_N parameters
                        for param in net_param_list:
                            val = controller.blocking(True).node(node).net.iface(radio_platform).get_parameters_net([param])
                            print("{}: {}".format(radio_platform, val))
                        # interate over the UPI_R measurements
                        for m in radio_measurement_list:
                            val = controller.blocking(True).node(node).radio.iface(radio_platform).get_measurements([m])
                            print("{}: {}".format(radio_platform, val))
                        # interate over the UPI_N measurements
                        for m in net_measurement_list:
                            val = controller.blocking(True).node(node).net.iface(radio_platform).get_measurements_net([m])
                            print("{}: {}".format(radio_platform, val))

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
