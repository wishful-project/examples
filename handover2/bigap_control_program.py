import logging
import datetime
import random
import wishful_upis as upis
from wishful_agent.core import wishful_module
from wishful_agent.timer import TimerEventSender
from common import CQIReportingEvent
from common import DHCPNewEvent
from common import DHCPDelEvent

import time
import subprocess
import zmq

__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


@wishful_module.build_module
class BigAPController(wishful_module.ControllerModule):
    def __init__(self, mode, ap_iface):
        super(BigAPController, self).__init__()
        self.log = logging.getLogger('BigAPController')
        self.mode = mode
        self.ap_iface = ap_iface
        self.running = False
        self.activeSTAs = {} # MAC_ADDR -> IP_ADDR
        self.nodes = []

    @wishful_module.on_start()
    def my_start_function(self):
        print("BiGAP control app started")
        self.running = True

    @wishful_module.on_exit()
    def my_stop_function(self):
        print("BiGAP control app stopped")
        self.running = False

    @wishful_module.on_event(upis.mgmt.NewNodeEvent)
    def add_node(self, event):
        node = event.node

        if self.mode == "GLOBAL" and node.local:
            return

        self.log.info("Added new node: {}, Local: {}"
                      .format(node.uuid, node.local))
        self.nodes.append(node)

        devs = node.get_devices()
        for dev in devs:
            print("Dev: ", dev.name)


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


    @wishful_module.on_event(CQIReportingEvent)
    def serve_cqi_report_event(self, event):
        '''
            From APs
        '''
        curr_sigpower = event.curr_sigpower
        candidate_sigpower = event.candidate_sigpower
        self.log.info("CQIReportingEvent curr: {}"
                      .format(curr_sigpower))
        self.log.info("CQIReportingEvent curr: {}"
                      .format(candidate_sigpower))


    @wishful_module.on_event(DHCPNewEvent)
    def serve_dhcp_new_event(self, event):
        '''
            From DHCP
        '''
        self.log.info("DHCPNewEvent NEW: {}"
                      .format(event.mac_addr))
        self.log.info("DHCPNewEvent NEW: {}"
                      .format(event.ip_addr))

        if event.mac_addr not in self.activeSTAs:
            # new STA to be served
            self.activeSTAs[event.mac_addr] = event.ip_addr
        else:
            # already known
            pass


    @wishful_module.on_event(DHCPDelEvent)
    def serve_dhcp_del_event(self, event):
        '''
            From DHCP
        '''
        self.log.info("DHCPNewEvent DEL: {}"
                      .format(event.mac_addr))
        self.log.info("DHCPNewEvent DEL: {}"
                      .format(event.ip_addr))


        if event.mac_addr in self.activeSTAs:
            # new STA to be served
            del self.activeSTAs[event.mac_addr]
        else:
            # unknown STA
            pass


    ''' TBD '''
    def get_servingAP(self, sta_mac_addr):
        """
        Estimates the AP which serves the given STA. Note: if an STA is associated with multiple APs the one with the
        smallest inactivity time is returned.
        """

        self.log.debug('Function: is_associated_with')
        try:
            nodes_with_sta = {}

            for node in self.nodes:
                res = node.iface(self.ap_iface).blocking(True).radio.get_inactivity_time_of_connected_devices()

                if sta_mac_addr in res:
                    self.log.debug(res[sta_mac_addr])
                    nodes_with_sta[node] = int(res[sta_mac_addr][0])

                    # dictionary of aps where station is associated
                    self.log.debug("STA found on the following APs with the following idle times:")
                    self.log.debug(str(nodes_with_sta))

            if not bool(nodes_with_sta):
                # If no serving AP was found; return None
                return None

            # serving AP is the one with minimal STA idle value
            servingAP = min(nodes_with_sta, key=nodes_with_sta.get)
            self.log.info("STA %s is served by AP %s " % (sta_mac_addr, servingAP))

            return servingAP

        except Exception as e:
            self.log.fatal("An error occurred in get_servingAP: %s" % e)
            raise e


    ''' TBD '''
    def performHO(self, sta_mac_addr, sta_ip, target_AP, target_channel, serving_channel, target_AP_ip, target_AP_name, ho_scheme):

        """
            Functions perform handover.
        """

        try:
            self.log.debug('********* testPerformHardHO **********')

            # find out which AP is currently controlling this client STA
            serving_AP = self.get_servingAP(sta_mac_addr)
            serving_AP_ip = serving_AP.ip
            serving_AP_name = serving_AP.name


            self.log.debug('Serving AP of %s is %s' % (str(sta_mac_addr), str(serving_AP_name)))
            self.log.debug('Move STA %s from %s to %s' % (str(sta_mac_addr), str(serving_AP_name), str(target_AP_name)))

            retVal = controller.handover.perform_handover(wlan_iface, serving_AP, target_AP, sta_mac_addr,
                                                          wlan_inject_iface = wlan_inject_iface, sta_ip = sta_ip,
                                                          servingAP_ip = serving_AP_ip, servingChannel = serving_channel,
                                                          network_bssid = network_bssid, targetAP_ip = target_AP_ip,
                                                          targetChannel = target_channel, gateway = gateway,
                                                          ho_type = ho_scheme)

            self.log.debug('HO result %s' % (str(retVal)))

        except Exception as e:
            self.log.fatal("... An error occurred : %s" % e)
            raise e

"""
    DHCP daemon which sends events used for STA client discovery
"""
@wishful_module.build_module
class DHCPDaemon(wishful_module.ControllerModule):
    def __init__(self, mode, zmq_port):
        super(DHCPDaemon, self).__init__()
        self.log = logging.getLogger('DHCPDaemon')
        self.mode = mode
        self.zmq_port = zmq_port
        #self.activeSTAs = {}
        self.running = False


    @wishful_module.on_start()
    def my_start_function(self):
        print("BiGAP control app started")

        # start scanner
        self.exec_file = 'staticDHCPd'
        self.processArgs = self.exec_file + ' '
        self.process = subprocess.Popen(self.processArgs.split(), shell=False)
        # wait to settle down
        time.sleep(1)

        # ZMQ stuff
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect("tcp://localhost:%s" % self.zmq_port)

        self.running = True

        # ZMQ message loop
        while (True):
            dhcpJson = self.socket.recv_json()

            print(dhcpJson)

            for key in dhcpJson:
                print("key: %s , value: %s" % (key, dhcpJson[key]))
                if key == 'new':
                    print('NEW DHCP LEASE START THREAD')
                    dhcpNew = dhcpJson[key].split('/')
                    mac = dhcpNew[0]
                    ip = dhcpNew[1]

                    #if mac not in self.activeSTAs:
                    #    pass

                    event = DHCPNewEvent(mac, ip)
                    self.send_event(event)

                elif key == 'delete':
                    print('DHCP LEASE EXPIRED STOP THREAD')
                    dhcpDelete = dhcpJson[key].split('/')
                    mac = dhcpDelete[0]
                    ip = dhcpDelete[1]

                    event = DHCPDelEvent(mac, ip)
                    self.send_event(event)

            else:
                print('DHCP Server sent unknown key in dictionary')

    @wishful_module.on_exit()
    def my_stop_function(self):
        print("BiGAP control app stopped")
        # stop scanner
        self.process.kill()
        self.running = False

