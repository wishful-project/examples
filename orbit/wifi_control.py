import logging
import datetime
import random
import wishful_upis as upis
from wishful_agent.core import wishful_module
from wishful_agent.timer import TimerEventSender

import time
import subprocess
import zmq

__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"

class PeriodicDiscoveryTimeEvent(upis.mgmt.TimeEvent):
    def __init__(self):
        super().__init__()

'''
	Simple RPC test
'''

@wishful_module.build_module
class WiFiController(wishful_module.ControllerModule):
    def __init__(self, mode):
        super(WiFiController, self).__init__()
        self.log = logging.getLogger('WiFiAPController')
        self.mode = mode
        self.discovery_interval = 5

        self.running = False
        self.nodes = {} # APs UUID -> node
 
    @wishful_module.on_start()
    def my_start_function(self):
        print("control app started")

        # channel hopping every 100ms
        self.discoveryTimer = TimerEventSender(self, PeriodicDiscoveryTimeEvent)
        self.discoveryTimer.start(self.discovery_interval)

        self.running = True

    @wishful_module.on_exit()
    def my_stop_function(self):
        print("control app stopped")
        self.running = False

    @wishful_module.on_event(upis.mgmt.NewNodeEvent)
    def add_node(self, event):
        node = event.node

        self.log.info("Added new node: {}, Local: {}"
                      .format(node.uuid, node.local))
        self.nodes[node.uuid] = node

        devs = node.get_devices()
        for dev in devs:
            self.log.info("Dev: %s" % dev.name)


    @wishful_module.on_event(upis.mgmt.NodeExitEvent)
    @wishful_module.on_event(upis.mgmt.NodeLostEvent)
    def remove_node(self, event):
        self.log.info("Node lost".format())
        node = event.node
        reason = event.reason
        if node in self.nodes:
            del self.nodes[node.uuid]
            self.log.info("Node: {}, Local: {} removed reason: {}"
                          .format(node.uuid, node.local, reason))


    @wishful_module.on_event(PeriodicDiscoveryTimeEvent)
    def periodic_discovery(self, event):

        if self.localNode == None:
            return

        self.log.debug("Periodic discovery")
        self.log.debug("My node: %s" % self.localNode.uuid)
        self.discoveryTimer.start(self.discovery_interval)

        try:
		    start = time.time()
            for node in self.nodes.values():

                self.log.info(node)
                device = node.get_device(0)
                self.log.info(device)

                wifaces = device.radio.get_interfaces()
                for wif in wifaces:
                    self.log.info('WIFI::wif %s' % str(wif))
                    winfo = device.radio.get_wifi_card_info(wif)
                    self.log.info('WIFI::winfo: %s' % str(winfo))

                    if winfo['driver'] == 'ath9k':
                        self.log.info('Running ATH9k driver')

            end = time.time()
            delta = end - start
			self.log.info('Exec time: %0.6f" % delta)
            
        except Exception as e:
            self.log.error("{} !!!Exception!!!: {}".format(
                datetime.datetime.now(), e))
