import logging
import wishful_upis as upis
from wishful_agent.core import wishful_module
from common import AveragedRssiSampleEvent

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


@wishful_module.build_module
class MyAvgFilter(wishful_module.ControllerModule):
    def __init__(self, window):
        super(MyAvgFilter, self).__init__()
        self.log = logging.getLogger('MyAvgFilter')
        self.window = window
        self.samplesPerTransmitter = {}

    @wishful_module.on_event(upis.radio.RssiSampleEvent)
    def serve_rssi_sample(self, event):

        rssi = event.rssi
        ta = event.ta
        node = event.node
        device = event.device
        self.log.info(
            "RSSI Sample: node: {}, device: {}, transmitter: {}, value: {}"
            .format(node.hostname, device.name, ta, rssi))

        if ta not in self.samplesPerTransmitter:
            self.samplesPerTransmitter[ta] = [rssi]
        else:
            self.samplesPerTransmitter[ta].append(rssi)

        samples = self.samplesPerTransmitter[ta]

        if len(samples) == self.window:
            s = sum(samples)
            self.samplesPerTransmitter[ta].pop(0)
            avg = s / self.window
            event = AveragedRssiSampleEvent(ta, avg)
            self.send_event(event)
            self.log.info(
                "Averaged RSSI Sample: transmitter: {}, value: {}"
                .format(ta, avg))
