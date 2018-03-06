#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki EXPERT control program

Usage:
   controller.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   python controller.py --config config/localhost/global_cp_config.yaml

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


__author__ = "Dimitrs Katris"
__copyright__ = "Copyright (c) 2017, IMEC"
__version__ = "0.1.0"
__email__ = "dkatris@intellia.gr"

log = logging.getLogger('contiki_global_control_program')


retranmissions = 0
pdr = 0
rpl_parent = 0
rpl_dio_stats = 0

#import function from expert library
from expert import implementation_exp_algo


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

        while True:
            gevent.sleep(5)
            print("\n")
            print("Connected nodes", [str(node.name) for node in nodes])
            if nodes:
                # Network Configurations
                ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
                radio_platforms = controller.blocking(True).node(nodes[0]).radio.iface("lowpan0").get_radio_platforms()
                ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").set_parameters_net({'app_activate': 1})
                for i in range(1, len(radio_platforms)):
                    ret = controller.blocking(True).node(nodes[0]).net.iface(radio_platforms[i]).set_parameters_net({'app_activate': 2})

                gevent.sleep(2)

                #implent algo
                implementation_exp_algo(controller, nodes[0], 1)

                break

        while True:
            gevent.sleep(60) # run experiment for 60sec
            if nodes:
                for node in nodes:
                    # Calculate macStats
                    for radio_platform in radio_platforms:
                        val = controller.blocking(True).node(node).radio.iface(radio_platform).get_measurements(["IEEE802154_measurement_macStats"])
                        file.write(str(val)+ "\n")
                        noAck = int(val['IEEE802154_measurement_macStats'][7])
                        collision = int(val['IEEE802154_measurement_macStats'][8])
                        macStats = noAck + collision
                        retranmissions += macStats
                    # Calculate pdr for lowpan0
                    val = controller.blocking(True).node(node).net.iface("lowpan0").get_measurements_net(['app_stats'])
                    received = int(val['app_stats'][0])
                    lost = int(val['app_stats'][1])
                    pdr = received / (received + lost)
                    file.write(str(val)+ "\n")
                    # Calculate rpl_parent, rpl_dio_stats
                    for radio_platform in radio_platforms:
                        val = controller.blocking(True).node(node).net.iface(radio_platform).get_measurements_net( ["rpl_stats","rpl_dio_stats"])
                        rpl_parent += int(val['rpl_stats'][4])
                        file.write(str(val)+ "\n")
                        # calculate rpl_dio_stats
                        rpl_dio_stats += int(val['rpl_dio_stats'][1]) +  int(val['rpl_dio_stats'][2])

                    ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").get_parameters_net(['rpl_objective_function', 'app_send_interval', 'app_payload_length'])
                    print(ret)
                    val = controller.blocking(True).node(nodes[0]).radio.iface("lowpan0").get_parameters(['IEEE802154_phyTXPower'])
                    print(val)

                break

        print("retranmissions per Node: ", float(retranmissions/len(radio_platforms)))
        print("pdr for lowpan0: ", pdr)
        print("rpl_parent per Node: ", float(rpl_parent/len(radio_platforms)))
        print("rpl_dio_stats per Node: ", float(rpl_dio_stats/len(radio_platforms)))
        file.close()



    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
