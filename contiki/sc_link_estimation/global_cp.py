#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path
   --measurements measurements --measurements config/portable/measurement_config.yaml Config Config file with measurement info

Example:
   python sc_link_estimation/global_cp.py --config config/localhost/global_cp_config.yaml --measurements config/portable/measurement_config.yaml
   
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
from measurement_logger import MeasurementLogger
import time

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2017, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('SC Link Estimation')


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

    measurements_file_path = args['--measurements']
    with open(measurements_file_path, 'r') as f:
        measurement_config = yaml.load(f)
    measurement_logger = MeasurementLogger.load_config(measurement_config)

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

        radio_measurement_list = [
            "IEEE802154_measurement_macStats"
        ]

        net_measurement_list = [
            "ipv6_stats",
            "icmp_stats",
            # "tcp_stats",
            "udp_stats",
            # "nd6_stats",
            "rpl_stats"
        ]

        radio_platforms = []

        control_msg_rx_overhead = {}
        control_msg_tx_overhead = {}

        upd_num_rx = {}
        upd_num_tx = {}

        while True:
            gevent.sleep(1)
            print("Connected nodes", [str(node.name) for node in nodes])
            if nodes:
                radio_platforms = controller.blocking(True).node(nodes[0]).radio.iface("lowpan0").get_radio_platforms()
                print(radio_platforms)
                for rp in radio_platforms:
                    control_msg_rx_overhead[rp] = 0
                    control_msg_tx_overhead[rp] = 0
                for rp in radio_platforms:
                    ret = controller.blocking(True).node(nodes[0]).net.iface(rp).set_parameters_net({'rpl_objective_function': 1})
                    control_msg_rx_overhead[rp] += 2
                    control_msg_tx_overhead[rp] += 2
                    print(ret)
                ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
                control_msg_rx_overhead["lowpan0"] += 2
                control_msg_tx_overhead["lowpan0"] += 2
                print(ret)
                break

        gevent.sleep(20)

        ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").set_parameters_net({'app_activate': 1})
        control_msg_rx_overhead["lowpan0"] += 2
        control_msg_tx_overhead["lowpan0"] += 2

        prev_val = (0, 0)

        for i in range(1, len(radio_platforms)):
            ret = controller.blocking(True).node(nodes[0]).net.iface(radio_platforms[i]).set_parameters_net({'app_activate': 2})
            control_msg_rx_overhead[radio_platforms[i]] += 2
            control_msg_tx_overhead[radio_platforms[i]] += 2
            print(ret)
            gevent.sleep(5)
            val = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").get_measurements_net(['app_stats'])
            rx = val['app_stats'][0] - prev_val[0]
            rx_loss = val['app_stats'][1] - prev_val[1]
            if rx + rx_loss > 0:
                pdr = rx / (rx + rx_loss)
            else:
                pdr = 0
            measurement_logger.log_measurement("UDP_rxstats", [time.time(), rx, rx + rx_loss, rx_loss, pdr])
            # print("rx = {}, rx_loss {}, PDR {}".format(rx, rx_loss, pdr))
            prev_val = val['app_stats']

        for rp in radio_platforms:
            ret = controller.blocking(True).node(nodes[0]).net.iface(rp).set_parameters_net({'app_activate': 0})
            control_msg_rx_overhead[rp] += 2
            control_msg_tx_overhead[rp] += 2
            print(ret)
        # for rp in radio_platforms:
        #     val = controller.blocking(True).node(nodes[0]).net.iface(rp).get_measurements_net(['rpl_stats'])
        #     control_msg_rx_overhead[rp] += 2
        #     control_msg_tx_overhead[rp] += 2
        #     print(val)
        #     val = controller.blocking(True).node(nodes[0]).net.iface(rp).get_measurements_net(['udp_stats'])
        #     control_msg_rx_overhead[rp] += 2
        #     control_msg_tx_overhead[rp] += 2
        #     print(val)

        for rp in radio_platforms:
            ret = controller.blocking(True).node(nodes[0]).net.iface(rp).set_parameters_net({'rpl_objective_function': 0})
            control_msg_rx_overhead[rp] += 2
            control_msg_tx_overhead[rp] += 2
            print(ret)

        ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").set_parameters_net({'app_activate': 1})
        control_msg_rx_overhead["lowpan0"] += 2
        control_msg_tx_overhead["lowpan0"] += 2

        prev_val = (0, 0)

        for i in range(1, len(radio_platforms)):
            ret = controller.blocking(True).node(nodes[0]).net.iface(radio_platforms[i]).set_parameters_net({'app_activate': 2})
            control_msg_rx_overhead[radio_platforms[i]] += 2
            control_msg_tx_overhead[radio_platforms[i]] += 2
            print(ret)
            gevent.sleep(5)
            val = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").get_measurements_net(['app_stats'])
            rx = val['app_stats'][0] - prev_val[0]
            rx_loss = val['app_stats'][1] - prev_val[1]
            if rx + rx_loss > 0:
                pdr = rx / (rx + rx_loss)
            else:
                pdr = 0
            measurement_logger.log_measurement("UDP_rxstats", [time.time(), rx, rx + rx_loss, rx_loss, pdr])
            # print("rx = {}, rx_loss {}, PDR {}".format(rx, rx_loss, pdr))
            prev_val = val['app_stats']

        for rp in radio_platforms:
            ret = controller.blocking(True).node(nodes[0]).net.iface(rp).set_parameters_net({'app_activate': 0})
            control_msg_rx_overhead[rp] += 2
            control_msg_tx_overhead[rp] += 2
            print(ret)

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
