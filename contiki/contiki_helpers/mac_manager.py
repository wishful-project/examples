""" This module implements basic abstractions for MAC configuration and control on sensor nodes.
"""
import logging


class MACManager(object):
    """Local MAC manager class implementing all the mandatory MACManager functions.
    This class can be extended to support extra functions, specific to a MAC protocol (CSMA,TDMA,TSCH)
    """

    def __init__(self, node_manager, mac_mode):
        """Creates a MAC Manager object.

        Args:
            local_engine (LocalManager): a reference to the local WiSHFUL engine.
        """
        self.node_manager = node_manager
        self.log = logging.getLogger("mac_manager")
        self.mac_mode = mac_mode
        pass

    def update_macconfiguration(self, param_key_values_dict, mac_address_list=None):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.

        Args:
            parameter_key_values (Dict[str,Any]): a dictionary containing parameter key-value pairs.
             radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        return self.node_manager.execute_upi_function("radio", "set_parameters", mac_address_list, param_key_values_dict)

    def read_macconfiguration(self, param_key_list, mac_address_list=None):
        """Update the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.

        Args:
            parameter_keys (List[str]): a list of parameter keys
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        return self.node_manager.execute_upi_function("radio", "get_parameters", mac_address_list, param_key_list)

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
        return self.node_manager.execute_upi_function("radio", "get_measurements", mac_address_list, measurement_key_list)

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
        if self.node_manager.scope = "local":
			return self.node_manager.execute_upi_function("radio", "get_measurements_periodic", mac_address_list, measurement_key_list, collect_period, report_period, num_iterations, report_callback)
		else:
			return self.node_manager.get_measurements_periodic("radio", measurement_key_list, collect_period, report_period, num_iterations, report_callback, mac_address_list=None)

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
        if self.node_manager.scope = "local":
			return self.node_manager.execute_upi_function("radio", "subscribe_events", mac_address_list, event_key_list, event_callback, event_duration)
        else:
			return self.node_manager.subscribe_events("radio", mac_address_list, event_key_list, event_callback, event_duration)

    def activate_radio_program(self, name, mac_address_list=None):
        """Activate a MAC radio program.

        Args:
            name (str): Name of the MAC radioprogram (CSMA, TDMA, TSCH).
            radio_platforms (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        if self.mac_mode == name:
            return 0
        return self.node_manager.execute_upi_function("radio", "activate_radio_program", mac_address_list, name)

    def get_radio_info(self, mac_address_list=None):
        """Returns a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.

        Args:
            radio_platforms (List[str], optional): list of radio platforms
        Returns:
            UPI_R.radio_info_t: a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.
        """
        return self.node_manager.execute_upi_function("radio", "get_radio_info", mac_address_list)
 
    def get_radio_platforms(self, mac_address_list=None):
        radio_platforms = []
        if mac_address_list is None:
			mac_address_list = self.node_manager.mac_address_list
        for mac_address in mac_address_list:
            radio_platforms.append(self.node_manager.mac_address_to_interface[mac_address])
        return radio_platforms

    def get_hwaddr_list(self):
        """Returns the macaddress of the interface.

        Args:
            radio_platforms (List[str], optional): list of radio platforms
        Returns:
            int: the macaddress
        """
        return self.node_manager.get_mac_address_list()
