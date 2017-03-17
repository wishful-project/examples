import threading
import wishful_agent
import wishful_controller
from contiki.contiki_helpers.node_manager import NodeManager


class LocalNodeManager(NodeManager):

    def __init__(self, config):
        super(LocalNodeManager, self).__init__("local")
        self.agent = wishful_agent.Agent(local=True)
        self.control_engine = self.agent.get_local_controller()
        self.agent.load_config(config)
        self.agent.run()
        t = threading.Timer(5, self.__update_mac_address_list)
        t.start()

    def __update_mac_address_list(self):
        radio_platforms = self.control_engine.blocking(True).iface("lowpan0").radio.get_radio_platforms()
        for radio_platform in radio_platforms:
            mac_addr = self.control_engine.blocking(True).iface(radio_platform).radio.get_hwaddr()
            self.mac_address_list.append(mac_addr)
            self.mac_address_to_interface[mac_addr] = radio_platform

    def execute_upi_function(self, upi_type, upi_fname, mac_address_list=None, *args, **kwargs):
        ret = {}
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        if type(mac_address_list) is int:
            mac_address_list = [mac_address_list]
        for mac_address in mac_address_list:
            if mac_address in self.mac_address_list:
                iface = self.mac_address_to_interface[mac_address]
                ret[mac_address] = self.control_engine.blocking(True).iface(iface).exec_cmd(upi_type=upi_type, fname=upi_fname, args=args, kwargs=kwargs)
        return ret

    def schedule_upi_function(self, upi_type, upi_fname, exec_time, mac_address_list=None, callback=None, *args, **kwargs):
        ret = {}
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        if type(mac_address_list) is int:
            mac_address_list = [mac_address_list]
        for mac_address in mac_address_list:
            if mac_address in self.mac_address_list:
                iface = self.mac_address_to_interface[mac_address]
                ret[mac_address] = self.control_engine.blocking(False).exec_time(exec_time).callback(callback).iface(iface).exec_cmd(upi_type=upi_type, fname=upi_fname, args=args, kwargs=kwargs)
        return ret

    def delay_upi_function(self, upi_type, upi_fname, delay, mac_address_list=None, callback=None, *args, **kwargs):
        ret = {}
        if mac_address_list is None:
            mac_address_list = self.mac_address_list
        if type(mac_address_list) is int:
            mac_address_list = [mac_address_list]
        for mac_address in mac_address_list:
            if mac_address in self.mac_address_list:
                iface = self.mac_address_to_interface[mac_address]
                ret[mac_address] = self.control_engine.blocking(False).delay(delay).callback(callback).iface(iface).exec_cmd(upi_type=upi_type, fname=upi_fname, args=args, kwargs=kwargs)
        return ret

    def stop(self):
        self.agent.stop()
