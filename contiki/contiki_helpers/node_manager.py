import abc
import logging
import yaml

class Group(object):

    def __init__(self,name, manager, mac_address_list=None):
        self.name = named
        self.mac_address_list = []
        self.manager = manager
        if mac_address_list is not None and type(mac_address_list) is list:
            self.mac_address_list = mac_address_list

    def remove_node(self, mac_address):
        if mac_address in self.mac_address_list:
            self.mac_address_list.remove(mac_address)

    def add_node(self, mac_address):
        if mac_address not in self.mac_address_list:
            self.mac_address_list.append(mac_address)

    def blocking_group_call(self, upi_type, upi_fname, *args, **kwargs):
        return self.manager.execute_upi_function(upi_type, upi_fname, self.mac_address_list, args=args, kwargs=kwargs)

    def scheduled_group_call(self, upi_type, upi_fname, exec_time, *args, **kwargs):
        return self.manager.schedule_upi_function(upi_type, upi_fname, exec_time, self.mac_address_list, args=args, kwargs=kwargs)

    def delayed_group_call(self, upi_type, upi_fname, delay, *args, **kwargs):
        return self.manager.schedule_upi_function(upi_type, upi_fname, delay, self.mac_address_list, args=args, kwargs=kwargs)

class NodeManager():
    __metaclass__ = abc.ABCMeta

    def __init__(self,scope):
        self.log = logging.getLogger("Contiki Node Manager: ")
        self.scope = scope
        self.groups = {}
        self.mac_address_list = []
        self.mac_address_to_interface = {}

    def get_mac_address_list(self):
        return self.mac_address_list

    def create_group(self, group_name, mac_address_list=None):
        if group_name not in self.groups:
            self.groups[group_name] = Group(group_name,self,mac_address_list)
            return self.groups[group_name]
        return None

    def destroy_group(self, group_name):
        if group_name in self.groups:
            del self.groups[group_name]
        pass

    @abc.abstractmethod
    def execute_upi_function(self, upi_type, upi_fname, mac_address_list=None, *args, **kwargs):
        pass

    @abc.abstractmethod
    def schedule_upi_function(self, upi_type, upi_fname, exec_time, mac_address_list=None, callback=None, *args, **kwargs):
        pass

    @abc.abstractmethod
    def delay_upi_function(self, upi_type, upi_fname, delay, mac_address_list=None, callback=None, *args, **kwargs):
        pass
