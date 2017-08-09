#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import signal
import sys, os
import yaml

sys.path.append('../../')
sys.path.append("../../agent_modules/net_linux")
sys.path.append("../../agent_modules/module_lte")
sys.path.append("../../agent_modules/module_lte/wishful_module_lte")
sys.path.append('../../upis')
sys.path.append('../../framework')
sys.path.append('../../agent')

import wishful_upis as upis
import wishful_agent

__author__ = "Francesco Giannone, Domenico Garlisi"
__copyright__ = "Copyright (c) 2017, Sant'Anna, CNIT"
__version__ = "0.1.0"
__email__ = "{francesco.giannone@santannapisa.it, domenico.garlisi@cnit.it}"

"""
Setting of experiment node
"""

node_interface = "eth5"
group_name = "lte_example"

"""
END setting of experiment nodes
"""


""" START WiSHFUL agent setting """
"""
The WiSHFUL controller module is the core module of the WiSHFUL framework and allow all the basics functions
such as the node discovery, the UPI functions execution on local and remote node, perform the messages exchange between
global control program and local control program, and all the other management functions of the framework. The different
works of the controller are  performed by different module can be added on demand in the controller
"""

#Create agent
agent = wishful_agent.Agent()

#Configure agent, we specify in the parameters the controller name and a string information related to the
#controller
agent.set_agent_info(name="experiment-node", info="Example tutorial Agent", iface=node_interface)


#the following rows add all the needed modules to the controller

#add the discovery module, responsable for the nodes discovery procedure
#we specify interface and the name of the nodes group

agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre", 
                 className="PyreDiscoveryAgentModule", kwargs={"iface":node_interface, "groupName":group_name})

#add the net_linux module,
agent.add_module(moduleName="net_linux", pyModule="wishful_module_net_linux",
                 className="NetworkModule")

#add the wifi_wmp module, responsable to controll wmp platform
agent.add_module(moduleName="lte", pyModule="wishful_module_lte", className="LteModule")


""" END WiSHFUL agent setting """


""" START Define logging controller """
""" we use the python logging system module (https://docs.python.org/2/library/logging.html) """

#set the logging name
log = logging.getLogger('wishful_agent')
logLevel = logging.INFO
logging.basicConfig(level=logLevel, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

""" END Define logging controller """

try:
    #Start agent
    agent.run()
except KeyboardInterrupt:
    log.debug("Agent exits")
finally:
    log.debug("Exit")
    agent.stop()