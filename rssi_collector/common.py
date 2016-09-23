import wishful_upis as upis

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class AveragedRssiSampleEvent(upis.upi.EventBase):
    def __init__(self, ta, rssi):
        super().__init__()
        self.ta = ta
        self.rssi = rssi

    def serialize(self):
        return {"ta": self.ta, "rssi": self.rssi}

    @classmethod
    def parse(cls, buf):
        rssi = buf.get("rssi", None)
        ta = buf.get("ta", None)
        return cls(ta, rssi)


class StartMyFilterEvent(upis.upi.EventBase):
    def __init__(self):
        super().__init__()


class StopMyFilterEvent(upis.upi.EventBase):
    def __init__(self):
        super().__init__()
