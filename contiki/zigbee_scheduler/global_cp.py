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
   --application_name Name of the contiki application (udp/ping)
   --abs_log_dir Absolute path of the logging directory
   --measurements measurementsConfig Config file with measurement info
   --param_config_file Parameter configuration file (csv)
   --event_config_file Events configuration file (csv)
   --slotframe_file File containing a slotframe configuration
   --hopping_sequence_file File containing a TSCH hopping sequence

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
import sys

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

def default_callback(group, node, cmd, data, interface = ""):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}, interface: {}".format(datetime.datetime.now(), group, node.name, cmd, data, interface))

def handle_event(mac_address, event_name, event_value):
    print("%s @ %s: %s"%(str(mac_address), event_name, str(event_value)))
    measurement_logger.log_measurement(event_name, event_value)

def event_cb(mac_address, event_name, event_value):
    _thread.start_new_thread(handle_event, (mac_address, event_name, event_value))

slotframe_file = None
hopping_sequence_file = None

def main():
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


    ##############################
    # Load script configuration: #
    ##############################
    
    script_arguments = docopt(__doc__, version=__version__)
    load_config(script_arguments)

    ##############################
    # Start script:              #
    ##############################
    
    try:
        # Setup the sensor node helpers:
        global_node_manager = GlobalNodeManager(config)
        app_manager = AppManager(global_node_manager)
        taisc_manager = TAISCMACManager(global_node_manager, "TSCH")
        
        # Configure the default callback:
        global_node_manager.set_default_callback(default_callback)

        # Wait for the agents to connect to the global controller:
        global_node_manager.wait_for_agents(node_config['ip_address_list'])
        
        # Configure the first sensor node as border router and start the local monitoring control programs:
        border_router_id = 1
        print("Set node %d as border router"%(border_router_id))
        app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],border_router_id)
        global_node_manager.start_local_monitoring_cp()
        
        gevent.sleep(3)

        # Set the superframe allocation:
        if slotframe_file is not None:
            err = taisc_manager.update_slotframe(slotframe_file,'TSCH')
            print("Setting superframe allocation to %s (%s)"%(slotframe_file,err)) 
        
        # Configure the hopping sequence:
        if hopping_sequence_file is not None:
            err = taisc_manager.update_hopping_sequence(hopping_sequence_file,'TSCH')
            print("Setting hopping sequence to %s (%s)"%(hopping_sequence_file,err)) 
        
        # Load the sensor node settings:
        if param_config_file is not None:
            with open(param_config_file, 'r') as csvfile:
                settings = csv.reader(csvfile, delimiter=',')
                for setting_iterator in settings:
                    setting = list(setting_iterator)
                    if setting[0] == "mac":
                        err = taisc_manager.update_macconfiguration({setting[1]: int(setting[2])})
                    elif setting[0] == "app":
                        err = app_manager.update_configuration({setting[1]: int(setting[2])})
                    print("Setting %s to %s (%s)"%(setting[1],setting[2],err)) 
                
        # Start the application:
        if(application_name == "ping"):
            print("Starting ping example")
            print("Activating clients")
            app_manager.update_configuration({"APP_ActiveApplication": 5},range(2,len(global_node_manager.get_mac_address_list())+1))
        elif(application_name=="udp"):
            print("Starting udp example")
            print("Activating server")
            app_manager.update_configuration({"APP_ActiveApplication": 1},[1])
            print("Activating clients")
            app_manager.update_configuration({"APP_ActiveApplication": 2},range(2,len(global_node_manager.get_mac_address_list())+1))
        else:
            print("No application active (%s)"%(application_name))

        # Register events:
        if event_config_file is not None:
            with open(event_config_file, 'r') as csvfile:
                event_settings = csv.reader(csvfile, delimiter=',')
                for event_setting_it in event_settings:
                    event_setting = list(event_setting_it)
                    print(event_setting)
                    if event_setting[0] == "1":
                        ret_events = taisc_manager.subscribe_events([event_setting[1]], event_cb, 0)
                        print("Suscribe event %s returns %s"%(event_setting[1],ret_events))

        # Run the experiment until keyboard interrupt is triggered:
        while True:
            gevent.sleep(1)
            
    except KeyboardInterrupt:
        log.debug("Exit")
        global_node_manager.stop()
        log.debug("Controller exits")
        sys.exit(0)
        
def load_config(args): 
    global config, node_config, application_name, slotframe_file, \
        hopping_sequence_file, param_config_file, event_config_file, \
        measurement_logger
    
    # a) Verbosity:
    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    # b) Log file location:
    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']
    logging.basicConfig(filename=logfile, level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')
    
    # c) Load measuremts config (yaml):
    if args['--measurements'] is not None:
        measurements_file_path = args['--measurements']
        with open(measurements_file_path, 'r') as f:
            measurement_config = yaml.load(f)
        measurement_logger = MeasurementLogger.load_config(measurement_config)
        measurement_logger.start_logging()
    else:
        log_measurements = False

    # d) Load the configuration file path (yaml):
    if args['--config'] is not None:
        config_file_path = args['--config']
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
    else:
        logging.fatal("Please provide config file (--config)")
        sys.exit(0)
        
    # e) Load the ip's of the agents (yaml):
    if args['--nodes'] is not None:
        nodes_file_path = args['--nodes']
        with open(nodes_file_path, 'r') as f:
            node_config = yaml.load(f)
    else:
        logging.fatal("Please provide nodes file (--nodes)")
        sys.exit(0)
        
    # f) Load the node configuration file(csv):
    if args['--param_config_file'] is not None:
        param_config_file = args['--param_config_file']
    
    # g) Load the event configuration file (csv):
    if args['--event_config_file'] is not None:
        event_config_file = args['--event_config_file']
    
    # h) Load the application name:
    if args['--application_name'] is not None:
        application_name = args['--application_name']
    else:
        application_name = "None"
    
    # i) Load the slot frame file:
    if args['--slotframe_file'] is not None:
        slotframe_file = args['--slotframe_file']
        
    
    # i) Load the hopping sequence file:
    if args['--hopping_sequence_file'] is not None:
        hopping_sequence_file = args['--hopping_sequence_file']
        
    return


if __name__ == "__main__":
    main()
    
