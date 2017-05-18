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
   --application_name Name of the contiki application (udp/ping)
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
import _thread
import csv
import os
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

def print_event(mac_address, event_name, event_value):
    print(str(event_name) + " : " + str(event_value) + " (" + str(mac_address) + ")")

def event_cb(mac_address, event_name, event_value):
    _thread.start_new_thread(print_event, (mac_address, event_name, event_value))
    #~ coexistence_logger.log_measurement(event_name, event_value)

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
        taisc_manager = TAISCMACManager(global_node_manager, "TSCH")
        
        global_node_manager.set_default_callback(default_callback)

        nodes_file_path = args['--nodes']
        with open(nodes_file_path, 'r') as f:
            node_config = yaml.load(f)
        global_node_manager.wait_for_agents(node_config['ip_address_list'])
        
        
        border_router_id = 1
        print("Set node %d as border router"%(border_router_id))
        app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],border_router_id)
        
        global_node_manager.start_local_monitoring_cp()

        example             = args['--application_name']

        #Superframe allocation:
        err = taisc_manager.update_slotframe('./contiki_helpers/default_taisc_slotframe.csv','TSCH')
        print("Setting superframe allocation to %s (%s)"%('./contiki_helpers/default_taisc_slotframe.csv',err)) 
        
        err = taisc_manager.update_hopping_sequence('./contiki_helpers/default_tsch_hopping_sequence.csv','TSCH')
        print("Setting hopping sequence to %s (%s)"%('./contiki_helpers/default_taisc_slotframe.csv',err)) 
        
        with open(os.path.dirname(os.path.realpath(__file__))+'/tsch_settings.csv', 'r') as csvfile:
            tsch_settings = csv.reader(csvfile, delimiter=',')
            for tsch_setting_it in tsch_settings:
                tsch_setting = list(tsch_setting_it)
                if tsch_setting[0] == "mac":
                    err = taisc_manager.update_macconfiguration({tsch_setting[1]: int(tsch_setting[2])})
                elif tsch_setting[0] == "app":
                    err = app_manager.update_configuration({tsch_setting[1]: int(tsch_setting[2])})
                print("Setting %s to %s (%s)"%(tsch_setting[1],tsch_setting[2],err)) 
        #Application:
        #~ 0 APPLICATION_NONE,
        #~ 1 APPLICATION_UDP_SERVER,
        #~ 2 APPLICATION_UDP_CLIENT,
        #~ 3 APPLICATION_TCP_SERVER,
        #~ 4 APPLICATION_TCP_CLIENT,
        #~ 5 APPLICATION_PING,
        #~ 6 APPLICATION_MAX,
        if(example == "ping"):
            print("Starting ping example")
            print("Activating clients")
            app_manager.update_configuration({"APP_ActiveApplication": 5},range(2,len(global_node_manager.get_mac_address_list())+1))
        elif(example=="udp"):
            print("Starting udp example")
            print("Activating server")
            app_manager.update_configuration({"APP_ActiveApplication": 1},[1])
            print("Activating clients")
            app_manager.update_configuration({"APP_ActiveApplication": 2},range(2,len(global_node_manager.get_mac_address_list())+1))

        #EVENTS:
        with open(os.path.dirname(os.path.realpath(__file__))+'/event_settings.csv', 'r') as csvfile:
            event_settings = csv.reader(csvfile, delimiter=',')
            for event_setting_it in event_settings:
                event_setting = list(event_setting_it)
                print(event_setting)
                if event_setting[0] == "1":
                    ret_events = taisc_manager.subscribe_events([event_setting[1]], event_cb, 0)
                    print("Suscribe event %s returns %s"%(event_setting[1],ret_events))

        while True:
            #~ print(taisc_manager.get_measurements(["APP_STATS"]))
            gevent.sleep(1)
    except KeyboardInterrupt:
        log.debug("Exit")
        global_node_manager.stop()
        log.debug("Controller exits")
        import sys
        sys.exit(0)
