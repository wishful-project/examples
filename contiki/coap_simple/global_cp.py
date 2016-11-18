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
    logging.basicConfig(filename=logfile, level=log_level,format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')
    
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
            gevent.sleep(10)
            print("\n")
            print("Connected nodes", [str(node.name) for node in nodes])
            if nodes:
                val = controller.blocking(True).node(nodes[0]).radio.iface("lowpan0").get_parameters([1000])
                print(val)

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()
