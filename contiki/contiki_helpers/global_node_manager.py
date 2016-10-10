import gevent
import threading
import _thread

from contiki_helpers.local_monitoring_cp import local_monitoring_program
from contiki_helpers.node_manager import NodeManager


class GlobalNodeManager(NodeManager):

    def __init__(self, control_engine):
        super(GlobalNodeManager, self).__init__(control_engine, "global")
        connected_nodes = {}
        mac_address_to_node_id = {}
        mac_address_to_event_cb = {}
        mac_address_to_report_cb = {}
        mac_address_to_hc_connector = {}


    #~ def __get_macaddress_by_nodeid_iface(self,node_id, iface):
        #~ for addr in self.mac_address_list:
            #~ if self.mac_address_to_node_id[addr] == node_id and self.mac_address_to_interface[addr] == iface:
                #~ return addr
        #~ return -1

    def __hc_message_handler(hc_connector, mac_address, node_id, iface):
        while True:
            msg = hc_connector.recv(block=False, timeout=1)
            while msg is not None:
                if type(msg) is dict and "msg_type" in msg:
                    msg_type = msg["msg_type"]
                    if msg_type == "cmd_result":
                        if self.control_engine.default_callback is not None:
                            gevent.spawn(self.control_engine.fire_callback, self.control_engine.default_callback, "all", node_id, msg["cmd"], msg["result"])
                        else:
                            self.log.debug("No default callback defined in CP for command results dropping msg {}".format(msg))
                    elif msg_type == "report":
                        #~ mac_address = self.__get_macaddress_by_nodeid_iface(agent_id, msg["interface"])
                        if mac_address in self.mac_address_to_report_cb:
                            geven.spawn(self.mac_address_to_report_cb[mac_address],mac_address,msg["report"])
                        else:
                            self.log.debug("No report callback defined in CP for report {}".format(msg))
                    elif msg_type == "event":
                        #~ mac_address = self.__get_macaddress_by_nodeid_iface(agent_id, msg["interface"])
                        if mac_address in self.mac_address_to_event_cb:
                            geven.spawn(self.mac_address_to_event_cb[mac_address],mac_address,msg["event_name"],msg["event_value"])
                        else:
                            self.log.debug("No report callback defined in CP for report {}".format(msg))
                    else:
                        print("{} Global Manager received unknown msgtype {} from local CP {}".format(datetime.datetime.now(), msg, agent_id))
                else:
                    print("{} Global Manager received unknown msg {} from local CP {}".format(datetime.datetime.now(), msg, agent_id))
                msg = hc_connector.recv(block=False, timeout=1)
            gevent.sleep(1)
        pass

    def start_local_monitoring_cp(self, mac_address_list=None):
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        for mac_address in mac_address_list:
            if mac_address not in self.mac_address_to_hc_connector:
                node_id = self.mac_address_to_node_id[mac_address]
                self.mac_address_to_event_cb[mac_address] = None
                self.mac_address_to_report_cb[mac_address] = None
                hc_connector = self.control_engine.node(node_id).hc.start_local_control_program(program=local_monitoring_program)
                self.mac_address_to_hc_connector[mac_address] = hc_connector
                _thread.start_new_thread(hc_message_handler, (hc_connector,mac_address,node_id,iface))
            else:
                self.log.debug("Local monitoring program already started for {}".format(mac_address))

    def subscribe_events(self, upi_type, event_key_list, event_callback, event_duration, mac_address_list=None):
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        for mac_address in mac_address_list:
            self.mac_address_to_event_cb[mac_address] = event_callback
            msg = {'interface': [self.mac_address_to_interface[mac_address]], 'command': 'SUBSCRIBE_EVENT', 'upi_type': upi_type, 'event_key_list': event_key_list, 'event_duration': event_duration}
            self.mac_address_to_hc_connector[mac_address].send(msg)


    def get_measurements_periodic(self, upi_type, measurement_key_list, collect_period, report_period, num_iterations, report_callback, mac_address_list=None):
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        for mac_address in mac_address_list:
            self.mac_address_to_report_cb[mac_address] = report_callback
            msg = {'interface': [self.mac_address_to_interface[mac_address]], 'command': 'GET_MEASUREMENTS_PERIODIC', 'upi_type': upi_type, 'measurement_key_list': measurement_key_list, 'collect_period': collect_period, 'report_period': report_period, 'num_iterations': num_iterations}
            self.mac_address_to_hc_connector[mac_address].send(msg)

    @classmethod
    def __update_mac_address_list(*args, **kwargs):
        node_id = args[1]
        print(args)
        radio_platforms = self.control_engine.node(node_id).exec_time(None).delay(None).timeout(None).callback(None).blocking(True).iface("lowpan0").radio.get_radio_platforms()
        for radio_platform in radio_platforms:
            mac_addr = self.control_engine.node(self.connected_nodes[node_id]).blocking(True).iface(radio_platform).radio.get_hwaddr()
            self.mac_address_list.append(mac_addr)
            self.mac_address_to_node_id[mac_addr] = node_id
            self.mac_address_to_interface[mac_addr] = radio_platform

    def add_node(self, node):
        self.connected_nodes[node.id] = node
        threading.Timer(10,self.__update_mac_address_list,args=(node.id,)).start()
        print("New node appeared:")
        print(node)

    def remove_node(self, node):
        mac_address_exit_list = []
        if node.id in self.connected_nodes:
            for mac_address in self.mac_address_list[:]:
                if self.mac_address_to_node_id[mac_address] == node.id:
                    mac_address_exit_list.append(mac_address)
                    del self.mac_address_to_node_id[mac_address]
                    del self.mac_address_to_interface[mac_address]
                    if mac_address in self.mac_address_to_event_cb:
                        del self.mac_address_to_event_cb[mac_address]
                    if mac_address in self.mac_address_to_report_cb:
                        del self.mac_address_to_report_cb[mac_address]
                    if mac_address in self.mac_address_to_hc_connector:
                        del self.mac_address_to_hc_connector[mac_address]
                    self.mac_address_list.remove(mac_address)
                    for group_name in self.groups:
                        self.group[group_name].remove_node(mac_address)
            del self.connected_nodes[node.id]
        print("NodeExit : NodeID : {} MAC_ADDR : {} Reason : {}".format(node.id,mac_address_exit_list, reason))

    def wait_for_agents(ip_address_list, timeout=60):
        for i in range(0, timeout):
            num_matches = 0
            if len(nodes) == len(ip_address_list):
                for node_id in nodes:
                    if nodes[node_id].ip in ip_address_list:
                        num_matches+=1
                        break
                if num_matches == len(ip_address_list):
                    log.info("All nodes are active we can start the local control programs")
                    log.info("Connected nodes: %s", nodes)
                    return True
            log.info("Still waiting for %d nodes", len(ip_address_list) - num_matches)
            gevent.sleep(1)
        return False

    def execute_upi_function(self, upi_type, upi_fname, mac_address_list=None, *args, **kwargs):
        ret = {}
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        if type(mac_address_list) is int:
            mac_address_list = [mac_address_list]
        for mac_address in mac_address_list:
            if mac_address in self.mac_address_list:
                node = self.mac_address_to_node_id[mac_address]
                iface = self.mac_address_to_interface[mac_address]
                ret[mac_address] = self.control_engine.blocking(True).node(node).iface(iface).exec_cmd(upi_type=upi_type, fname=upi_fname, args=args, kwargs=kwargs)
        return ret

    def schedule_upi_function(self, upi_type, upi_fname, exec_time, mac_address_list=None, callback=None, *args, **kwargs):
        ret = {}
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        if type(mac_address_list) is int:
            mac_address_list = [mac_address_list]
        for mac_address in mac_address_list:
            if mac_address in self.mac_address_list:
                node = self.mac_address_to_node_id[mac_address]
                iface = self.mac_address_to_interface[mac_address]
                ret[mac_address] = self.control_engine.blocking(False).exec_time(exec_time).callback(callback).node(node).iface(iface).exec_cmd(upi_type=upi_type, fname=upi_fname, args=args, kwargs=kwargs)
        return ret

    def delay_upi_function(self, upi_type, upi_fname, delay, mac_address_list=None, callback=None, *args, **kwargs):
        ret = {}
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        if type(mac_address_list) is int:
            mac_address_list = [mac_address_list]
        for mac_address in mac_address_list:
            if mac_address in self.mac_address_list:
                node = self.mac_address_to_node_id[mac_address]
                iface = self.mac_address_to_interface[mac_address]
                ret[mac_address] = self.control_engine.blocking(False).delay(delay).callback(callback).node(node).iface(iface).exec_cmd(upi_type=upi_type, fname=upi_fname, args=args, kwargs=kwargs)
        return ret
