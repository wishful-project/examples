import wishful_upis as upis

__author__ = "Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


class CQIReportingEvent(upis.upi.EventBase):
    '''
    Events reported by each AP.
    '''
    def __init__(self, candidate_sigpower, curr_sigpower):
        super().__init__()
        self.candidate_sigpower = candidate_sigpower
        self.curr_sigpower = curr_sigpower


class DHCPEvent(upis.upi.EventBase):
    '''
    Base class for event reported by DHCP
    '''
    def __init__(self, mac_addr, ip_addr):
        super().__init__()
        self.mac_addr = mac_addr
        self.ip_addr = ip_addr


class DHCPNewEvent(DHCPEvent):
    '''
    Event reported by DHCP server for new leases
    '''
    def __init__(self, mac_addr, ip_addr):
        super().__init__(mac_addr, ip_addr)


class DHCPDelEvent(DHCPEvent):
    '''
    Event reported by DHCP server for deleted leases
    '''
    def __init__(self, mac_addr, ip_addr):
        super().__init__(mac_addr, ip_addr)


class HOTriggerRequestEvent(upis.upi.EventBase):
    '''
    Events send by BigAP controller to trigger a handover operation.
    '''
    def __init__(self, sta_mac_addr, sta_ip, wlan_iface, wlan_inject_iface, network_bssid, serving_AP, serving_AP_ip,
                 serving_channel, target_AP, target_AP_ip, target_channel, gateway, ho_scheme):
        super().__init__()
        self.sta_mac_addr = sta_mac_addr
        self.sta_ip = sta_ip
        self.wlan_iface = wlan_iface
        self.wlan_inject_iface = wlan_inject_iface
        self.network_bssid = network_bssid
        self.serving_AP = serving_AP
        self.servingAP_ip = serving_AP_ip
        self.servingChannel = serving_channel
        self.target_AP = target_AP
        self.targetAP_ip = target_AP_ip
        self.targetChannel = target_channel
        self.gateway = gateway
        self.ho_type = ho_scheme


class HOTriggerReplyEvent(upis.upi.EventBase):
    '''
    Event send back to BigAP controller.
    '''
    def __init__(self, success):
        super().__init__()
        self.success = success