import logging


class AppManager(object):

    """Local MAC manager class implementing all the mandatory MACManager functions.
    This class can be extended to support extra functions, specific to a MAC protocol (CSMA,TDMA,TSCH)
    """

    def __init__(self, node_manager):
        """Creates a Local MAC Manager object.

        Args:
            local_engine (LocalManager): a reference to the local WiSHFUL engine.
        """
        self.node_manager = node_manager
        self.log = logging.getLogger("local_app_manager")

    def rpl_set_border_router(self, prefix_array, mac_address):
        """Sets the rpl border router.
        This function takes the ipv6 prefix of the border router
        This function returns a dictionary containing parameter key-error_code pairs.

        Args:
            prefix_array (List[str]): a list containing the ipv6 prefix
             radio_platforms (List[str], optional): list of radio platforms

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        return self.node_manager.execute_upi_function("net", "rpl_set_border_router", [mac_address], prefix_array)

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
        return self.node_manager.execute_upi_function("net", "set_parameters_net", mac_address_list, param_key_values_dict)

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
        return self.node_manager.execute_upi_function("net", "get_parameters_net", mac_address_list, param_key_list)

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
        return self.node_manager.execute_upi_function("net", "get_measurements_net", mac_address_list, measurement_key_list)

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
        if self.node_manager.scope == "local":
            return self.node_manager.execute_upi_function("net", "get_measurements_periodic_net", measurement_key_list, collect_period, report_period, num_iterations, report_callback, mac_address_list)
        else:
            return self.node_manager.get_measurements_periodic("net", measurement_key_list, collect_period, report_period, num_iterations, report_callback, mac_address_list)

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
        if self.node_manager.scope == "local":
            return self.node_manager.execute_upi_function("net", "subscribe_events_net", event_key_list, event_callback, event_duration, mac_address_list)
        else:
            return self.node_manager.subscribe_events("net", event_key_list, event_callback, event_duration, mac_address_list)
