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
from contiki.contiki_helpers.global_node_manager import *
from contiki.contiki_helpers.taisc_manager import *
from contiki.contiki_helpers.app_manager import *


__author__ = "Peter Ruckebusch & Jan Bauwens"
__copyright__ = "Copyright (c) 2016, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

CONTIKIMAC_TX_SUCCESS       = 0;
CONTIKIMAC_TX_NOACK         = 1;
CONTIKIMAC_TX_COLLISION     = 2;
CONTIKIMAC_CCA_FAILED       = 3;

cm_msg_type_index           = 0;
cm_msg_success_index        = 1;
cm_msg_size_index           = 2;
cm_strobe_amount_index      = 3;
cm_strobe_duration_index    = 4;

BROADCAST_STAT              = 1
UNICAST_STAT                = 2

radio_measurement_list = [
    "IEEE802154_measurement_macStats",
    "IEEE802154_measurement_energyStats"   
]
radio_event_list = [
    "IEEE802154_event_macStats",
    "IEEE802154_event_energyStats"
]

log = logging.getLogger('contiki_global_control_program')

measurement_logger_file                     = None
measurement_logger_gnuplot_energy           = None
measurement_logger_gnuplot_current          = None
measurement_logger_gnuplot_strobe_uc        = None
measurement_logger_gnuplot_strobe_bc        = None
measurement_logger_gnuplot_strobe_time_uc   = None
measurement_logger_gnuplot_strobe_time_bc   = None
measurement_logger_gnuplot_tx_stats         = None

packet_statistics_total = 0
packet_statistics = { 0:0, 1:0, 2:0, 3:0}

def default_callback(group, node, cmd, data, interface = ""):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}, interface: {}".format(datetime.datetime.now(), group, node.name, cmd, data, interface))

def event_cb(mac_address, event_name, event_value):
    print(str(event_name) + " : " + str(event_value))
    global packet_statistics_total
    #~ print("Event " + event_name + "(" + event_value[0] + "," + event_value[0])
    if event_name == "IEEE802154_event_contikimacStats":
        # Broadcast:
        #~ if event_value[0] == BROADCAST_STAT:
            #~ measurement_logger_gnuplot_strobe_Bc.log_measurement("strobe_bc", str(event_value[cm_msg_size_index]) + " " + str(event_value[cm_strobe_amount_index]))
            #~ measurement_logger_gnuplot_strobe_time_bc.log_measurement("strobe_time_bc", str(event_value[cm_msg_size_index]) + " " + str(event_value[cm_strobe_duration_index]))
        # Unicast:
        if event_value[cm_msg_type_index] == UNICAST_STAT and  event_value[cm_msg_success_index] == CONTIKIMAC_TX_SUCCESS:
            measurement_logger_gnuplot_strobe_uc.log_measurement("strobe_uc", str(event_value[cm_msg_size_index]) + " " + str(event_value[cm_strobe_amount_index]))
            measurement_logger_gnuplot_strobe_time_uc.log_measurement("strobe_time_uc", str(event_value[cm_msg_size_index]) + " " + str(event_value[cm_strobe_duration_index]))
        
        if event_value[cm_msg_type_index] == UNICAST_STAT:
            packet_statistics[event_value[cm_msg_success_index]]+= 1
            packet_statistics_total += 1
            
    elif event_name == "IEEE802154_event_energyStats":
        threading.Thread(target=flush_measurements("TAISC_event", mac_address, event_name, event_value, mac_address)).start()
    
def contikimac_event_cb(mac_address, event_name, event_value):
    print(str(mac_address) + " - " + str(event_name) + " - " + str(event_value))

def flush_measurements(group, node, cmd, data, interface):
    global counter,measurements,prev_measurements, time
    counter += 1
    measurement_logger_file.log_measurement(cmd, str((interface,) + data).replace(" ", "").replace("'","")[1:-2])
    measurements += numpy.array(data)/64
    if(counter == 64):
        time += measurements[0]
        log_measurements    = (measurements - prev_measurements)/(measurements.item(0)/1000000) * 31.25
        log_measurements[0] = time
        prev_measurements   = measurements
        measurement_logger_gnuplot_energy.log_measurement(cmd, log_measurements.tolist())
        measurement_logger_gnuplot_current.log_measurement("current", [((25.8 *  log_measurements.item(1) + 1.6 * log_measurements.item(2) + log_measurements.item(3) * 0.175 + 22.3 * log_measurements.item(4)) / 1000000 * 3)])
        counter = 0
        measurements = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

def signal_handler(signum, frame):
    if packet_statistics_total != 0:
        value = (packet_statistics[CONTIKIMAC_TX_SUCCESS] if CONTIKIMAC_TX_SUCCESS in packet_statistics else 0) * 100 / packet_statistics_total
        measurement_logger_gnuplot_tx_stats.log_measurement("tx_statistics","success    " + str(value))
        value = (packet_statistics[CONTIKIMAC_TX_NOACK] if CONTIKIMAC_TX_NOACK in packet_statistics else 0) * 100 / packet_statistics_total
        measurement_logger_gnuplot_tx_stats.log_measurement("tx_statistics","noack      " + str(value))
        value = (packet_statistics[CONTIKIMAC_TX_COLLISION] if CONTIKIMAC_TX_COLLISION in packet_statistics else 0) * 100 / packet_statistics_total
        measurement_logger_gnuplot_tx_stats.log_measurement("tx_statistics","collision  " + str(value))
        value = (packet_statistics[CONTIKIMAC_CCA_FAILED] if CONTIKIMAC_CCA_FAILED in packet_statistics else 0) * 100 / packet_statistics_total
        measurement_logger_gnuplot_tx_stats.log_measurement("tx_statistics","cca\\\\_failed " + str(value))
    
    measurement_logger_file.stop_logging()
    measurement_logger_gnuplot_energy.stop_logging()
    measurement_logger_gnuplot_current.stop_logging()
    measurement_logger_gnuplot_strobe_bc.stop_logging()
    measurement_logger_gnuplot_strobe_uc.stop_logging()
    measurement_logger_gnuplot_strobe_time_bc.stop_logging()
    measurement_logger_gnuplot_strobe_time_uc.stop_logging()
    measurement_logger_gnuplot_tx_stats.stop_logging()

    log.debug("Exit")
    global_node_manager.stop()

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
        
    measurement_logger_file                     = FileMeasurementLogger(experiment_name, radio_measurement_list + radio_event_list, log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_energy           = GnuplotMeasurementLogger(experiment_name, radio_measurement_list + radio_event_list, log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_current          = GnuplotMeasurementLogger(experiment_name, ["current"], log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_strobe_uc        = GnuplotMeasurementLogger(experiment_name, ["strobe_uc"], log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_strobe_bc        = GnuplotMeasurementLogger(experiment_name, ["strobe_bc"], log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_strobe_time_uc   = GnuplotMeasurementLogger(experiment_name, ["strobe_time_uc"], log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_strobe_time_bc   = GnuplotMeasurementLogger(experiment_name, ["strobe_time_bc"], log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot_tx_stats         = GnuplotMeasurementLogger(experiment_name, ["tx_statistics"], log_dir + "/" + experiment_group + "/" )
    
    measurement_logger_file.start_logging()
    measurement_logger_gnuplot_energy.start_logging()
    measurement_logger_gnuplot_current.start_logging()
    measurement_logger_gnuplot_strobe_bc.start_logging()
    measurement_logger_gnuplot_strobe_uc.start_logging()
    measurement_logger_gnuplot_strobe_time_bc.start_logging()
    measurement_logger_gnuplot_strobe_time_uc.start_logging()
    measurement_logger_gnuplot_tx_stats.start_logging()

    nodes = []
    counter = 0  
    time = 0
    measurements = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    prev_measurements = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
    config_file_path = args['--config']
    config = None
    
    
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
            
        global_node_manager = GlobalNodeManager(config)
        app_manager = AppManager(global_node_manager)
        taisc_manager = TAISCMACManager(global_node_manager, "ContikiMAC")
        
        global_node_manager.set_default_callback(default_callback)

        nodes_file_path = args['--nodes']
        with open(nodes_file_path, 'r') as f:
            node_config = yaml.load(f)
        global_node_manager.wait_for_agents(node_config['ip_address_list'])
        
        
        border_router_id = 1
        print("Set node %d as border router"%(border_router_id))
        app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],border_router_id)
          
        global_node_manager.start_local_monitoring_cp()
        gevent.sleep(5) 
        ret_events = taisc_manager.subscribe_events(["IEEE802154_event_contikimacStats"],   event_cb, 0) 
        ret_events = taisc_manager.subscribe_events(["IEEE802154_event_energyStats"],       event_cb, 0)
        print("Suscribe event returns %s"%(ret_events))
        
        print("Activating server")
        app_manager.update_configuration({"app_activate": 1},[1])
        print("Activating clients")
        app_manager.update_configuration({"app_activate": 2},range(2,len(global_node_manager.get_mac_address_list())+1))
        
        while True:
            gevent.sleep(20)
    except KeyboardInterrupt:
        log.debug("Controller exits")
        import sys
        sys.exit(0)
