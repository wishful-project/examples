#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name Name of the logfile
   --config configFile Config file path
   --nodes nodesFile   Config file with node info
   --experiment_name Name of the experiment
   --experiment_group Name of the experiment group
   --abs_log_dir Absolute path of the logging directory

Example:
   python global_cp.py --config config/localhost/global_cp_config.yaml 
   
Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
import logging
import yaml
import gevent
import datetime
import numpy   
import wishful_upis as upis
import signal
import threading
from measurement_logger import *
from stdout_measurement_logger import *
from file_measurement_logger import *
from gnuplot_measurement_logger import *
from mysql_measurement_logger import *
from contiki.contiki_helpers.global_node_manager import *
from contiki.contiki_helpers.taisc_manager import *
from contiki.contiki_helpers.app_manager import *


__author__ = "Peter Ruckebusch & Jan Bauwens"
__copyright__ = "Copyright (c) 2016, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')

coexistence_logger  = None

packet_statistics_total = 0
packet_statistics = { 0:0, 1:0, 2:0, 3:0}

def default_callback(group, node, cmd, data, interface = ""):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}, interface: {}".format(datetime.datetime.now(), group, node.name, cmd, data, interface))

def event_cb(mac_address, event_name, event_value):
    print(str(event_name) + " : " + str(event_value) + " (" + str(mac_address) + ")")
    coexistence_logger.log_measurement(event_name, event_value)

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
    
    experiment_name = None
    if '--experiment_name' in args:
        experiment_name = args['--experiment_name']
    else:
        experiment_name = "experiment"
        
    experiment_group = None
    if '--experiment_group' in args:
        experiment_group = args['--experiment_group']
    else:
        experiment_group = "global_cp_taisc"
        
    log_dir = None
    if '--abs_log_dir' in args:
        log_dir = args['--abs_log_dir']
    else:
        import os
        log_dir = os.getcwd()

    nodes = []
    counter = 0  
    time = 0

    config_file_path = args['--config']
    config = None
    
    coexistence_logger  = MySQLMeasurementLogger(experiment_name, {"coexistence_stats":"channel part_a part_b", "tdma_stats":"channel tx rx"}, "localhost")
    coexistence_logger.start_logging()
    
    try:
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
            
        global_node_manager = GlobalNodeManager(config)
        app_manager = AppManager(global_node_manager)
        taisc_manager = TAISCMACManager(global_node_manager, "TDMA")
        
        global_node_manager.set_default_callback(default_callback)

        nodes_file_path = args['--nodes']
        with open(nodes_file_path, 'r') as f:
            node_config = yaml.load(f)
        global_node_manager.wait_for_agents(node_config['ip_address_list'])
        
        
        border_router_id = 1
        print("Set node %d as border router"%(border_router_id))
        app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],border_router_id)
        
        global_node_manager.start_local_monitoring_cp()

        superframe_size=3
        transmission_power=5

        #Superframe allocation:
        #Superframe size:
        err1 = taisc_manager.update_macconfiguration({"IEEE802154e_macSlotframeSize": superframe_size})
        print("Setting superframe size to %s (%s)"%(superframe_size,err1)) 
        gevent.sleep(2)
        #Hopping sequence:
        #Transmission power:
        err1 = taisc_manager.update_macconfiguration({"IEEE802154_phyTXPower": transmission_power})
        print("Setting transmission power to %s (%s)"%(transmission_power,err1)) 
        gevent.sleep(1)

        gevent.sleep(2)
        #~ ret = taisc_manager.update_slotframe('./coexistence/default_taisc_slotframe.csv')
        #~ print("Update slot frame " + str(ret))
        #ret_events = taisc_manager.subscribe_events(["coexistence_stats"], event_cb, 0)
        #print("Suscribe event returns %s"%(ret_events))    
        #ret_events = taisc_manager.subscribe_events(["tdma_stats"], event_cb, 0)
        #print("Suscribe event returns %s"%(ret_events))        
        
        while True:
            gevent.sleep(20)
    except KeyboardInterrupt:
        log.debug("Exit")
        global_node_manager.stop()
        log.debug("Controller exits")
        import sys
        sys.exit(0)
