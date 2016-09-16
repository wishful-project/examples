import wishful_upis as upis

__author__ = "Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


class CQIReportingEvent(upis.upi.EventBase):
    def __init__(self, candidate_sigpower, curr_sigpower):
        super().__init__()
        self.candidate_sigpower = candidate_sigpower
        self.curr_sigpower = curr_sigpower


class DHCPNewEvent(upis.upi.EventBase):
    def __init__(self, mac_addr, ip_addr):
        super().__init__()
        self.mac_addr = mac_addr
        self.ip_addr = ip_addr


class DHCPDelEvent(upis.upi.EventBase):
    def __init__(self, mac_addr, ip_addr):
        super().__init__()
        self.mac_addr = mac_addr
        self.ip_addr = ip_addr