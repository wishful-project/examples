#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name Name of the logfile
   --config configFile Config file path
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
import wishful_controller
import yaml
import gevent
import datetime
import wishful_upis as upis
from measurement_logger import *
from stdout_measurement_logger import *
from file_measurement_logger import *
from gnuplot_measurement_logger import *


__author__ = "Peter Ruckebusch & Jan Bauwens"
__copyright__ = "Copyright (c) 2016, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"

log = logging.getLogger('contiki_global_control_program')
measurement_logger_stdout = None
measurement_logger_file = None
measurement_logger_gnuplot = None

radio_param_list = [
    # "ContikiMAC_ChannelCheckRate",
    # "ContikiMAC_PhaseOptimization",
    "IEEE802154_macExtendedAddress",
    "IEEE802154_macPANId",
    "IEEE802154_macShortAddress",
    "IEEE802154_phyCurrentChannel",
    "IEEE802154_phyTXPower",
]
radio_measurement_list = [
    #~ "IEEE802154_measurement_macStats",
    "IEEE802154_measurement_energyStats"   
]
#~ radio_event_list = [
    #~ "IEEE802154_event_macStats"
#~ ]
net_param_list = [
    "link_address",
    "rpl_dio_interval_min",
    "rpl_dio_interval_doublings",
    "rpl_dio_redundancy",
    "rpl_default_lifetime",
    "rpl_objective_function",
    "APP_ActiveApplication"
]

#~ net_measurement_list = [
    #~ "ipv6_stats",
    #~ "icmp_stats",
    #~ "tcp_stats",
    #~ "udp_stats",
    #~ "nd6_stats",
    #~ "rpl_stats"
#~ ]


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
        
    measurement_logger_stdout   = STDOUTMeasurementLogger(experiment_name)
    measurement_logger_file     = FileMeasurementLogger(experiment_name, radio_measurement_list, log_dir + "/" + experiment_group + "/" )
    measurement_logger_gnuplot  = GnuplotMeasurementLogger(experiment_name, radio_measurement_list, log_dir + "/" + experiment_group + "/" )
    measurement_logger_file.start_logging()
    measurement_logger_gnuplot.start_logging()


    controller = wishful_controller.Controller()
    nodes = []

    @controller.new_node_callback()
    def new_node(node):
        nodes.append(node)
        print("New node appeared:")
        print(node)
        
    import numpy    
    counter = 0  
    time = 0
    measurements = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    prev_measurements = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    
    def flush_measurements(group, node, cmd, data, interface):
        global counter,measurements,prev_measurements, time
        counter += 1
        for key, value in data.items():
            measurement_logger_file.log_measurement(key, str((interface,) + value).replace(" ", "").replace("'","")[1:-2])
            measurement_logger_stdout.log_measurement(key, str(counter) + " - " + str((interface,) + value).replace(" ", "").replace("'","")[1:-2])
            measurements += numpy.array(value)/64
            if(counter == 64):
                time += measurements[0]
                log_measurements    = (measurements - prev_measurements)/(measurements.item(0)/1000000) * 31.25
                log_measurements[0]	= time
                
                log.fatal((25.8 *  log_measurements.item(1) + 1.6 * log_measurements.item(2) + log_measurements.item(3) * 0.175 + 22.3 * log_measurements.item(4)) / 1000000 * 3)
                
                prev_measurements   = measurements
                measurement_logger_gnuplot.log_measurement(key, log_measurements.tolist())
                counter = 0
                measurements = numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    
    @controller.set_default_callback()
    def default_callback(group, node, cmd, data, interface):
        #~ print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}, interface: {}".format(datetime.datetime.now(), group, node.name, cmd, data, interface))
        threading.Thread(target=flush_measurements(group, node, cmd, data, interface)).start()
    
        
    try:
        config_file_path = args['--config']
        config = None
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
        

        controller.load_config(config)
        controller.start()

        first_time = True

        while not nodes:
            #~ print("Waiting for agents to connect")
            gevent.sleep(1)
        
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])
        
        
        taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
            
        ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])
        
        for node in nodes:
            for param in radio_param_list:
                val = controller.blocking(True).node(node).radio.iface("lowpan0").get_parameters([param])
                print("lowpan0: {}".format(val))
            for param in net_param_list:
                val = controller.blocking(True).node(node).net.iface("lowpan0").get_parameters_net([param])
                print("lowpan0: {}".format(val))

        gevent.sleep(20)
        
        print("Starting applications")
        ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan0").set_parameters_net({"APP_ActiveApplication":1})
        for lowpan_index in range(0,64):
            ret = controller.blocking(True).node(nodes[0]).net.iface("lowpan" + str(lowpan_index)).set_parameters_net({"APP_ActiveApplication":2})
        print("Applications started")
        
        
        
        #~ import threading
        #~ while True:
            #~ gevent.sleep(10)
            #~ for node in nodes:
                #~ for m in radio_measurement_list:
                    #~ for lowpan_index in range(0,64):
                        #~ threading.Thread(target=controller.blocking(False).node(node).radio.iface("lowpan" + str(lowpan_index)).get_measurements([m])).start()
                        
                    #~ gevent.sleep(1)
                    
                    
                    
                    #~ gevent.sleep(1)
                #~ for m in net_measurement_list:
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan0").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan1").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan2").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan3").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan4").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan5").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan6").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan7").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan8").get_measurements_net([m])
                    #~ val = controller.blocking(False).node(node).net.iface("lowpan9").get_measurements_net([m])
                    #~ gevent.sleep(1)

    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        start_logging.stop_logging()
        log.debug("Exit")
        controller.stop()
