import logging
import datetime
import wishful_upis as upis
from wishful_agent.core import wishful_module
from wishful_agent.timer import TimerEventSender

__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"

class PeriodicTimeEvent(upis.mgmt.TimeEvent):
    def __init__(self):
        super().__init__()

'''
Simple control program for testing mininet functionality.
'''

@wishful_module.build_module
class MininetWiFiController(wishful_module.ControllerModule):
    def __init__(self):
        super(MininetWiFiController, self).__init__()
        self.log = logging.getLogger('MininetWiFiController')
        self.interval = 5
        self.nodes = {} # APs UUID -> node
        self.running = False

    @wishful_module.on_start()
    def my_start_function(self):
        self.log.info("Topology control app started")

        # channel hopping every 100ms
        self.staTimer = TimerEventSender(self, PeriodicTimeEvent)
        self.staTimer.start(self.interval)

        self.running = True

    @wishful_module.on_exit()
    def my_stop_function(self):
        self.running = False

    @wishful_module.on_event(upis.mgmt.NewNodeEvent)
    def add_node(self, event):
        node = event.node

        self.log.info("Added new node: {}"
                      .format(node.uuid))
        self.nodes[node.uuid] = node


    @wishful_module.on_event(upis.mgmt.NodeExitEvent)
    @wishful_module.on_event(upis.mgmt.NodeLostEvent)
    def remove_node(self, event):
        self.log.info("Node lost".format())
        node = event.node
        reason = event.reason
        if node in self.nodes:
            del self.nodes[node.uuid]
            self.log.info("Node: {}, removed reason: {}"
                          .format(node.uuid, reason))


    @wishful_module.on_event(PeriodicTimeEvent)
    def periodic_tx_stats(self, event):

        self.log.info("Periodic getting tx stats")
        self.staTimer.start(self.interval)

        try:



        except Exception as e:
            self.log.error("{} !!!Exception!!!: {}".format(
                datetime.datetime.now(), e))

