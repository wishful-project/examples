""" This module implements basic abstractions for MAC configuration and control on sensor nodes.
"""
import abc
import logging


class AppManager(object):
    """Abstract MAC manager class listing all the mandatory MACManager functions.
    These functions must be implemented by the subclassess.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_configuration(self, param_key_values_dict):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.
        Args:
            parameter_key_values (Dict[str,Any]): a dictionary argument containing parameter key-value pairs.
        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        return -1

    @abc.abstractmethod
    def read_configuration(self, param_key_list):
        """Reads the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.
        Args:
            parameter_keys (List[str]): a list of parameter keys as arguments.
        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        return -1

    @abc.abstractmethod
    def get_measurements(self, measurement_key_list):
        """Monitor the current MAC behaviour in a pull based manner.
        This function takes a list of measurement keys as arguments.
        This function returns a dictionary containing measurement key-value pairs.
        Args:
            measurement_keys (List[str]): a list of measurement keys as arguments.
        Returns:
            Dict[str,Any]: a dictionary containing measurement key-value pairs.
        """
        return -1

    @abc.abstractmethod
    def get_measurements_periodic(self, measurement_key_list, collect_period, report_period, num_iterations, report_callback):
        """Monitor the current MAC behaviour periodically in a pull based manner.
        This function takes a list of measurement keys and configuration alues for the periodic collection as arguments.
        This function returns an error code.
        Args:
            measurement_keys (List[str]): a list of measurement keys as arguments
            collect_period (int): Period between measurements.
            collect_iterations (int): Number of collect periods.
            report_period (int): Period between reports (report_period<=collect_period*collect_iterations)
            report_callback (Callable[[str,Dict[str,List[Any]]], None]): Callback with arguments radio_platform and measurement report.
        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return -1

    @abc.abstractmethod
    def subscribe_events(self, event_key_list, event_callback, event_duration):
        """Monitor the MAC behaviour asynchroniously in a push based manner by registering for events.
        This function takes a list of event keys and an event callback as arguements.
        This function returns an error code.
        Args:
            event_keys (List[str]): a list of event keys
            event_callback (Callable[[str,str,Any],None]): Callback with arguments radio_platform, event name and event value.
        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return -1

    @abc.abstractmethod
    def get_hwaddr_list(self):
        """Returns the macaddress of the interface.
        Returns:
            int: the macaddress
        """
        return -1


class LocalAppManager(AppManager):
    """Local MAC manager class implementing all the mandatory MACManager functions.
    This class can be extended to support extra functions, specific to a MAC protocol (CSMA,TDMA,TSCH)
    """

    def __init__(self, control_engine, mac_manager):
        """Creates a Local MAC Manager object.

        Args:
            local_engine (LocalManager): a reference to the local WiSHFUL engine.
        """
        self.control_engine = control_engine
        self.log = logging.getLogger("local_app_manager")
        self.mac_manager = mac_manager

    def __execute_local_upi_func(self, UPIfunc, mac_address_list, *UPIargs, **UPIkwargs):
        if mac_address_list is None:
            mac_address_list = self.mac_manager.mac_address_radio_platform_dict.keys()
        ret = {}
        for mac_address in mac_address_list:
            ret[mac_address] = self.control_engine.blocking(True).iface(self.mac_manager.mac_address_radio_platform_dict[mac_address]).exec_cmd(upi_type="radio", fname=UPIfunc, args=UPIargs, kwargs=UPIkwargs)  
        return ret

    def update_configuration(self, param_key_values_dict, mac_address_list=None):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.

        Args:
            parameter_key_values (Dict[str,Any]): a dictionary containing parameter key-value pairs.
             radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        return self.__execute_local_upi_func("set_parameters_net", mac_address_list, param_key_values_dict)

    def read_configuration(self, param_key_list, mac_address_list=None):
        """Update the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.

        Args:
            parameter_keys (List[str]): a list of parameter keys
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        return self.__execute_local_upi_func("get_parameters_net", mac_address_list, param_key_list)

    def get_measurements(self, measurement_key_list, mac_address_list=None):
        """Monitor the current MAC behaviour in a pull based manner.
        This function takes a list of measurement keys as arguments.
        This function returns a dictionary containing measurement key-value pairs.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing measurement key-value pairs.
        """
        return self.__execute_local_upi_func("get_measurements_net", mac_address_list, measurement_key_list)

    def get_measurements_periodic(self, measurement_key_list, collect_period, report_period, num_iterations, report_callback, mac_address_list=None):
        """Monitor the current MAC behaviour periodically in a pull based manner.
        This function takes a list of measurement keys and configuration alues for the periodic collection as arguments.
        This function returns an error code.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            collect_period (int): Period between measurements.
            collect_iterations (int): Number of collect periods.
            report_period (int): Period between reports (report_period<=collect_period*collect_iterations)
            report_callback (Callable[[str,Dict[str,List[Any]]], None]): Callback with arguments radio_platform and measurement report.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return self.__execute_local_upi_func("get_measurements_periodic_net", mac_address_list, measurement_key_list, collect_period, report_period, num_iterations, report_callback)

    def subscribe_events(self, event_key_list, event_callback, event_duration, mac_address_list=None):
        """Monitor the MAC behaviour asynchroniously in a push based manner by registering for events.
        This function takes a list of event keys and an event callback as arguements.
        This function returns an error code.

        Args:
            event_keys (List[str]): a list of event keys
            event_callback (Callable[[str,str,Any],None]): Callback with arguments radio_platform, event name and event value.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return self.__execute_local_upi_func("subscribe_events_net", mac_address_list, event_key_list, event_callback, event_duration)

class GlobalAppManager(AppManager):
    """ Class doc """

    def __init__(self, control_engine, mac_manager):
        """ Class initialiser """
        self.control_engine = control_engine
        self.log = logging.getLogger("global_app_manager")
        self.mac_manager = mac_manager
        pass

    def __execute_global_upi_func(self, UPIfunc, mac_address_list=None, *UPIargs, **UPIkwargs):
        if mac_address_list is None:
            mac_address_list = self.mac_manager.mac_address_node_radioplatform_dict.keys()
        ret = {}
        for mac_addr in mac_address_list:
            node = self.mac_manager.mac_address_node_radioplatform_dict[mac_addr][0]
            radio_platform = self.mac_manager.mac_address_node_radioplatform_dict[mac_addr][1]
            ret[mac_addr] = self.control_engine.blocking(True).node(node).iface(radio_platform).exec_cmd(upi_type="net", fname=UPIfunc, args=UPIargs, kwargs=UPIkwargs)
        return ret

    def update_configuration(self, param_key_values_dict, mac_address_list=None):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.

        Args:
            parameter_key_values (Dict[str,Any]): a dictionary argument containing parameter key-value pairs.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        return self.__execute_global_upi_func("set_parameters_net", mac_address_list, param_key_values_dict)

    def read_configuration(self, param_key_list, mac_address_list=None):
        """Update the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.

        Args:
            parameter_keys (List[str]): a list of parameter keys as arguments.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        return self.__execute_global_upi_func("get_parameters_net", mac_address_list, param_key_list)

    def get_measurements(self, measurement_key_list, mac_address_list=None):
        """Monitor the current MAC behaviour in a pull based manner.
        This function takes a list of measurement keys as arguments.
        This function returns a dictionary containing measurement key-value pairs.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing measurement key-value pairs.
        """
        return self.__execute_global_upi_func("get_measurements_net", mac_address_list, measurement_key_list)

    def get_measurements_periodic(self, measurement_key_list, collect_period, report_period, num_iterations, report_callback, mac_address_list=None):
        """Monitor the current MAC behaviour periodically in a pull based manner.
        This function takes a list of measurement keys and configuration alues for the periodic collection as arguments.
        This function returns an error code.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            collect_period (int): Period between measurements.
            collect_iterations (int): Number of collect periods.
            report_period (int): Period between reports (report_period<=collect_period*collect_iterations)
            report_callback (Callable[[str,Dict[str,List[Any]]], None]): Callback with arguments radio_platform and measurement report.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return self.__execute_global_upi_func("get_measurements_periodic", mac_address_list, measurement_key_list, collect_period, report_period, num_iterations, report_callback)

    def subscribe_events(self, event_keys, event_callback, event_duration, mac_address_list=None):
        """Monitor the MAC behaviour asynchroniously in a push based manner by registering for events.
        This function takes a list of event keys and an event callback as arguements.
        This function returns an error code.

        Args:
            event_keys (List[str]): a list of event keys
            event_callback (Callable[[str,str,Any],None]): Callback with arguments radio_platform, event name and event value.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return self.__execute_global_upi_func("subscribe_events_net", mac_address_list, event_keys, event_callback, event_duration)
