"""
contiki_local_controller.py: Example implementation of local control program for Contiki

Usage:
   contiki_local_controller.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./contiki_local_controller -v --config ./config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
from contiki.contiki_helpers.local_node_manager import *
import wishful_upis as upis

import sys
import datetime
import logging
import time
import yaml
import gevent

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('wishful_agent.main')

def get_parameters(data):
    print("{} get_parameters_reponse : {}".format(datetime.datetime.now(), data))

def default_callback(cmd, data):
    print("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(
        datetime.datetime.now(), cmd, data))

def print_response(data):
    print("{} Specific callback for function call; Print response : {}".format(
        datetime.datetime.now(), data))


def main(args):
    contiki_nodes = []
    #control loop
    while True:
        contiki_nodes = local_node_manager.get_mac_address_list()
        print("\n")
        print("Connected nodes", [str(node) for node in contiki_nodes])
        if contiki_nodes:
            #execute UPI function blocking
            local_node_manager.execute_upi_function("radio","set_parameters",contiki_nodes,{'IEEE802154_phyCurrentChannel':12})

            #schedule non-blocking UPI function with specific callback
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            local_node_manager.schedule_upi_function("radio","get_parameters",exec_time, contiki_nodes, None, ['IEEE802154_phyCurrentChannel'])
            gevent.sleep(5)
            #delayed UPI function call with default callback
            local_node_manager.delay_upi_function("radio","set_parameters",3, contiki_nodes, None,{'IEEE802154_phyCurrentChannel':13})
            gevent.sleep(5)
            #schedule non-blocking UPI function with specific callback
            exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            local_node_manager.schedule_upi_function("radio","get_parameters",exec_time, contiki_nodes, print_response, ['IEEE802154_phyCurrentChannel'])
            
        gevent.sleep(10)


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

    local_node_manager = LocalNodeManager(config)
    local_node_manager.set_default_callback(default_callback)
    local_node_manager.add_callback(upis.radio.get_parameters,get_parameters)

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        local_node_manager.stop()
