import logging
import datetime
import random
import wishful_upis as upis
from wishful_agent.core import wishful_module
from wishful_agent.timer import TimerEventSender
from common import AveragedSpectrumScanSampleEvent
from common import StartMyFilterEvent
from common import StopMyFilterEvent

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class PeriodicEvaluationTimeEvent(upis.mgmt.TimeEvent):
    def __init__(self):
        super().__init__()


@wishful_module.build_module
class MyController(wishful_module.ControllerModule):
    def __init__(self, mode):
        super(MyController, self).__init__()
        self.log = logging.getLogger('MyController')
        self.mode = mode
        self.running = False
        self.nodes = []

        self.timeInterval = 10
        self.timer = TimerEventSender(self, PeriodicEvaluationTimeEvent)
        self.timer.start(self.timeInterval)

        self.myFilterRunning = False
        self.packetLossEventsEnabled = False

    @wishful_module.on_start()
    def my_start_function(self):
        print("start control app")
        self.running = True

    @wishful_module.on_exit()
    def my_stop_function(self):
        print("stop control app")
        self.running = False

    @wishful_module.on_event(upis.mgmt.NewNodeEvent)
    def add_node(self, event):
        node = event.node

        if self.mode == "GLOBAL" and node.local:
            return

        self.log.info("Added new node: {}, Local: {}"
                      .format(node.uuid, node.local))
        self.nodes.append(node)

        retVal = node.net.create_packetflow_sink(port=1234)
        print("Server started: {}".format(retVal))

        devs = node.get_devices()
        for dev in devs:
            print("Dev: ", dev.name)

        device = node.get_device(0)
        device.radio.set_power(15)
        device.radio.set_channel(random.randint(1, 11))
        device.enable_event(upis.radio.PacketLossEvent)
        self.packetLossEventsEnabled = True
        device.start_service(
            upis.radio.SpectralScanService(rate=1000, f_range=[2200, 2500]))

    @wishful_module.on_event(upis.mgmt.NodeExitEvent)
    @wishful_module.on_event(upis.mgmt.NodeLostEvent)
    def remove_node(self, event):
        self.log.info("Node lost".format())
        node = event.node
        reason = event.reason
        if node in self.nodes:
            self.nodes.remove(node)
            self.log.info("Node: {}, Local: {} removed reason: {}"
                          .format(node.uuid, node.local, reason))

    @wishful_module.on_event(upis.radio.PacketLossEvent)
    def serve_packet_loss_event(self, event):
        node = event.node
        device = event.device
        self.log.info("Packet loss in node {}, dev: {}"
                      .format(node.uuid, device.name))

    @wishful_module.on_event(AveragedSpectrumScanSampleEvent)
    def serve_spectral_scan_sample(self, event):
        avgSample = event.avg
        self.log.info("Averaged Spectral Scan Sample: {}"
                      .format(avgSample))

    def default_cb(self, data):
        node = data.node
        devName = None
        if data.device:
            devName = data.device.name
        msg = data.msg
        print("Default Callback: "
              "Node: {}, Dev: {}, Data: {}"
              .format(node.uuid, devName, msg))

    def get_power_cb(self, data):
        node = data.node
        dev = data.device
        msg = data.msg
        print("Power in "
              "Node: {}, Dev: {}, was set to: {}"
              .format(node.uuid, dev.name, msg))

    @wishful_module.on_event(PeriodicEvaluationTimeEvent)
    def periodic_evaluation(self, event):
        # go over collected samples, etc....
        # make some decisions, etc...
        print("Periodic Evaluation")
        print("My nodes: ", [node.uuid for node in self.nodes])
        self.timer.start(self.timeInterval)

        if len(self.nodes) == 0:
            return

        node = self.nodes[0]
        device = node.get_device(0)

        if self.packetLossEventsEnabled:
            device.disable_event(upis.radio.PacketLossEvent)
            self.packetLossEventsEnabled = False
        else:
            device.enable_event(upis.radio.PacketLossEvent)
            self.packetLossEventsEnabled = True

        if self.myFilterRunning:
            self.send_event(StopMyFilterEvent())
            self.myFilterRunning = False
        else:
            self.send_event(StartMyFilterEvent())
            self.myFilterRunning = True

        # execute non-blocking function immediately
        node.blocking(False).device("phy0").radio.set_power(random.randint(1, 20))

        # execute non-blocking function immediately, with specific callback
        node.callback(self.get_power_cb).radio.device("phy0").get_power()

        # schedule non-blocking function delay
        node.delay(3).callback(self.default_cb).net.create_packetflow_sink(port=1234)

        # schedule non-blocking function exec time
        exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
        node.exec_time(exec_time).radio.device(
            "phy0").set_channel(channel=random.randint(1, 11))

        # execute blocking function immediately
        result = node.radio.device("phy0").get_channel()
        print("{} Channel is: {}".format(datetime.datetime.now(), result))

        # exception handling, clean_per_flow_tx_power_table implementation
        # raises exception
        try:
            device.radio.clean_per_flow_tx_power_table()
        except Exception as e:
            print("{} !!!Exception!!!: {}".format(
                datetime.datetime.now(), e))
