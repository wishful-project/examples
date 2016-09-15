import logging
import wishful_upis as upis
from wishful_agent.core import wishful_module
from common import AveragedSpectrumScanSampleEvent
from common import StartMyFilterEvent
from common import StopMyFilterEvent

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


@wishful_module.build_module
class MyAvgFilter(wishful_module.ControllerModule):
    def __init__(self, window):
        super(MyAvgFilter, self).__init__()
        self.log = logging.getLogger('MyFilter')
        self.window = window
        self.running = False
        self.samples = []

    @wishful_module.on_event(StartMyFilterEvent)
    def start_filter(self, event):
        self.log.info("Start MyAvgFilter")
        self.running = True

    @wishful_module.on_event(StopMyFilterEvent)
    def stop_filter(self, event):
        self.log.info("Stop MyAvgFilter")
        self.running = False

    @wishful_module.on_event(upis.radio.SpectralScanSampleEvent)
    def serve_spectral_scan_sample(self, event):
        if not self.running:
            return

        sample = event.sample
        node = event.node
        device = event.device
        self.log.debug("New SpectralScan Sample:{} from node {}, device: {}"
                       .format(sample, node, device))

        self.samples.append(sample)

        if len(self.samples) == self.window:
            s = sum(self.samples)
            self.samples.pop(0)
            avg = s / self.window
            self.log.debug("Calculated average: {}".format(avg))
            event = AveragedSpectrumScanSampleEvent(avg)
            self.send_event(event)
